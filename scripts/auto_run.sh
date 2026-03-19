#!/bin/bash
# ============================================================
# MedScribe AI - Automatic Task Runner for Claude Code
# ============================================================
# Usage:
#   ./scripts/auto_run.sh phase 0        # Run all tasks in Phase 0
#   ./scripts/auto_run.sh all            # Run ALL phases (0-12)
#   ./scripts/auto_run.sh task 0 1       # Run single task 0.1
#   ./scripts/auto_run.sh resume         # Resume from last failed task
#   ./scripts/auto_run.sh status         # Show progress
# ============================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Config
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TASKS_DIR="$PROJECT_DIR/.claude/tasks"
LOG_FILE="$PROJECT_DIR/task_log.csv"
STATE_FILE="$PROJECT_DIR/.claude/.runner_state"
FAIL_LOG="$PROJECT_DIR/.claude/.fail_log"
MAX_RETRIES=2
PAUSE_BETWEEN_TASKS=3  # seconds

# ============================================================
# Helper Functions
# ============================================================

log_info()  { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_ok()    { echo -e "${GREEN}[✔]${NC}    $1"; }
log_fail()  { echo -e "${RED}[✘]${NC}    $1"; }
log_warn()  { echo -e "${YELLOW}[!]${NC}    $1"; }
log_step()  { echo -e "${CYAN}[>>]${NC}   $1"; }

separator() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

timestamp() { date '+%Y-%m-%d %H:%M:%S'; }

# Get all task files for a phase, sorted numerically
get_phase_tasks() {
    local phase=$1
    local dir="$TASKS_DIR/phase${phase}"
    if [ ! -d "$dir" ]; then
        echo ""
        return
    fi
    # Sort by task number (handles 1.1, 1.2, ... 1.10 correctly)
    ls "$dir"/task_*.md 2>/dev/null | sort -t'.' -k2 -n
}

# Extract task number from filename (e.g., task_0.1.md → 0.1)
task_id_from_file() {
    basename "$1" | sed 's/task_//' | sed 's/\.md//'
}

# Save runner state (for resume)
save_state() {
    local phase=$1
    local task=$2
    local status=$3
    echo "${phase}|${task}|${status}|$(timestamp)" > "$STATE_FILE"
}

# Load last state
load_state() {
    if [ -f "$STATE_FILE" ]; then
        cat "$STATE_FILE"
    else
        echo ""
    fi
}

# Log task result to CSV
log_task_csv() {
    local task_id=$1
    local mission=$2
    local errors=$3
    local status=$4
    
    # Ensure CSV has headers
    if [ ! -f "$LOG_FILE" ] || [ ! -s "$LOG_FILE" ]; then
        echo "TASK_ID,MISSION,ERRORS,CAUSE,SOLUTIONS,CHANGES,COMPLETED" > "$LOG_FILE"
    fi
    
    # Escape commas in mission text
    mission=$(echo "$mission" | tr ',' ';' | head -c 200)
    errors=$(echo "$errors" | tr ',' ';' | tr '\n' ' ' | head -c 200)
    
    echo "${task_id},\"${mission}\",\"${errors}\",\"\",\"\",\"\",${status}" >> "$LOG_FILE"
}

# ============================================================
# Core: Run a single task
# ============================================================

run_single_task() {
    local task_file=$1
    local task_id=$(task_id_from_file "$task_file")
    local phase=$(echo "$task_id" | cut -d'.' -f1)
    local task_num=$(echo "$task_id" | cut -d'.' -f2)
    local mission=$(head -1 "$task_file" | sed 's/TASK: //')
    local attempt=0
    local success=false

    separator
    log_step "Task ${task_id}: ${mission}"
    log_info "File: ${task_file}"
    log_info "Started: $(timestamp)"
    echo ""

    while [ $attempt -lt $MAX_RETRIES ] && [ "$success" = false ]; do
        attempt=$((attempt + 1))
        
        if [ $attempt -gt 1 ]; then
            log_warn "Retry attempt ${attempt}/${MAX_RETRIES}..."
            sleep 2
        fi

        # Run Claude Code with the task
        local output_file="/tmp/claude_task_${task_id}_${attempt}.log"
        
        if cd "$PROJECT_DIR" && claude -p "$(cat "$task_file")" > "$output_file" 2>&1; then
            success=true
            log_ok "Task ${task_id} COMPLETED (attempt ${attempt})"
            save_state "$phase" "$task_num" "done"
            log_task_csv "$task_id" "$mission" "NONE" "YES"
        else
            local exit_code=$?
            local error_msg=$(tail -5 "$output_file" 2>/dev/null || echo "Unknown error")
            log_fail "Task ${task_id} FAILED (attempt ${attempt}, exit code: ${exit_code})"
            
            if [ $attempt -ge $MAX_RETRIES ]; then
                log_fail "Max retries reached for task ${task_id}"
                save_state "$phase" "$task_num" "failed"
                log_task_csv "$task_id" "$mission" "$error_msg" "NO"
                echo "${task_id}|${mission}|$(timestamp)|${error_msg}" >> "$FAIL_LOG"
                return 1
            fi
        fi
    done

    log_info "Finished: $(timestamp)"
    
    # Compact Claude's context after every 5 tasks to save tokens
    local total_done=$(grep -c "YES" "$LOG_FILE" 2>/dev/null || echo "0")
    if [ $((total_done % 5)) -eq 0 ] && [ "$total_done" -gt 0 ]; then
        log_info "Auto-compacting Claude context (every 5 tasks)..."
    fi

    # Pause between tasks
    if [ $PAUSE_BETWEEN_TASKS -gt 0 ]; then
        sleep $PAUSE_BETWEEN_TASKS
    fi

    return 0
}

# ============================================================
# Run all tasks in a phase
# ============================================================

run_phase() {
    local phase=$1
    local tasks=$(get_phase_tasks "$phase")
    
    if [ -z "$tasks" ]; then
        log_fail "No tasks found for Phase ${phase}"
        return 1
    fi

    local total=$(echo "$tasks" | wc -l)
    local current=0
    local failed=0

    separator
    echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  Phase ${phase} - Starting ${total} tasks                      ║${NC}"
    echo -e "${CYAN}║  Time: $(timestamp)                    ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"

    for task_file in $tasks; do
        current=$((current + 1))
        log_info "Progress: [${current}/${total}] in Phase ${phase}"
        
        if ! run_single_task "$task_file"; then
            failed=$((failed + 1))
            
            # Ask whether to continue or stop
            log_warn "Task failed. Continue with next task? (y/n/s=skip)"
            read -t 30 -r answer || answer="n"
            
            case "$answer" in
                y|Y) log_info "Continuing to next task..." ;;
                s|S) log_info "Skipping failed task..." ;;
                *)   
                    log_fail "Stopping Phase ${phase}. Use './scripts/auto_run.sh resume' to continue."
                    return 1
                    ;;
            esac
        fi
    done

    separator
    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║  ✔ Phase ${phase} COMPLETE - ${total}/${total} tasks passed          ║${NC}"
        echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
    else
        echo -e "${YELLOW}╔══════════════════════════════════════════════════╗${NC}"
        echo -e "${YELLOW}║  ⚠ Phase ${phase} DONE - $((total-failed))/${total} passed, ${failed} failed   ║${NC}"
        echo -e "${YELLOW}╚══════════════════════════════════════════════════╝${NC}"
    fi

    return 0
}

# ============================================================
# Run ALL phases sequentially
# ============================================================

run_all() {
    local start_phase=${1:-0}
    
    echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║     MedScribe AI - FULL BUILD                    ║${NC}"
    echo -e "${CYAN}║     Starting from Phase ${start_phase}                        ║${NC}"
    echo -e "${CYAN}║     Time: $(timestamp)                    ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"

    for phase in $(seq "$start_phase" 12); do
        local tasks=$(get_phase_tasks "$phase")
        if [ -z "$tasks" ]; then
            log_warn "Phase ${phase} has no tasks, skipping"
            continue
        fi

        if ! run_phase "$phase"; then
            log_fail "Phase ${phase} had failures."
            log_warn "Continue to Phase $((phase+1))? (y/n)"
            read -t 60 -r answer || answer="n"
            if [[ ! "$answer" =~ ^[yY]$ ]]; then
                log_info "Stopped at Phase ${phase}. Resume with: ./scripts/auto_run.sh resume"
                return 1
            fi
        fi

        separator
        log_ok "Phase ${phase} complete. Moving to Phase $((phase+1))..."
        sleep 5
    done

    separator
    echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     🎉 ALL PHASES COMPLETE!                      ║${NC}"
    echo -e "${GREEN}║     Time: $(timestamp)                    ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
}

# ============================================================
# Resume from last failed task
# ============================================================

run_resume() {
    local state=$(load_state)
    
    if [ -z "$state" ]; then
        log_warn "No saved state found. Starting from Phase 0."
        run_all 0
        return
    fi

    local last_phase=$(echo "$state" | cut -d'|' -f1)
    local last_task=$(echo "$state" | cut -d'|' -f2)
    local last_status=$(echo "$state" | cut -d'|' -f3)
    local last_time=$(echo "$state" | cut -d'|' -f4)

    log_info "Last state: Phase ${last_phase}, Task ${last_task}, Status: ${last_status} (${last_time})"

    if [ "$last_status" = "done" ]; then
        # Find next task
        local next_task=$((last_task + 1))
        local next_file="$TASKS_DIR/phase${last_phase}/task_${last_phase}.${next_task}.md"
        
        if [ -f "$next_file" ]; then
            log_info "Resuming from task ${last_phase}.${next_task}"
            # Run remaining tasks in current phase, then continue
            local found_start=false
            for task_file in $(get_phase_tasks "$last_phase"); do
                local tid=$(task_id_from_file "$task_file")
                local tnum=$(echo "$tid" | cut -d'.' -f2)
                if [ "$tnum" -ge "$next_task" ]; then
                    run_single_task "$task_file" || true
                fi
            done
            # Continue with remaining phases
            run_all $((last_phase + 1))
        else
            # No more tasks in this phase, move to next
            log_info "Phase ${last_phase} complete. Starting Phase $((last_phase + 1))"
            run_all $((last_phase + 1))
        fi
    else
        # Retry the failed task
        log_info "Retrying failed task ${last_phase}.${last_task}"
        local retry_file="$TASKS_DIR/phase${last_phase}/task_${last_phase}.${last_task}.md"
        if [ -f "$retry_file" ]; then
            run_single_task "$retry_file" || true
        fi
        # Continue from next
        run_resume
    fi
}

# ============================================================
# Show progress status
# ============================================================

show_status() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║        MedScribe AI - Build Progress             ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
    echo ""

    local total_tasks=0
    local total_done=0

    printf "%-12s %-30s %s\n" "Phase" "Name" "Progress"
    echo "─────────────────────────────────────────────────────"

    local phase_names=(
        "Infrastructure"
        "Authentication"
        "Patients"
        "Recording"
        "Transcription"
        "Summarization"
        "Search"
        "Dashboard"
        "Pipeline"
        "Security"
        "Monitoring"
        "Admin"
        "Polish"
    )

    for phase in $(seq 0 12); do
        local tasks=$(get_phase_tasks "$phase")
        local count=0
        if [ -n "$tasks" ]; then
            count=$(echo "$tasks" | wc -l)
        fi
        total_tasks=$((total_tasks + count))

        # Count completed from CSV
        local done=0
        if [ -f "$LOG_FILE" ]; then
            done=$(grep -c "^${phase}\." "$LOG_FILE" 2>/dev/null | grep -c "YES" 2>/dev/null || echo "0")
            # More reliable: count lines starting with phase number that end with YES
            done=$(awk -F',' -v p="$phase" '$1 ~ "^"p"\\." && $NF == "YES" {c++} END {print c+0}' "$LOG_FILE")
        fi
        total_done=$((total_done + done))

        # Progress bar
        local bar=""
        if [ $count -gt 0 ]; then
            local filled=$((done * 20 / count))
            local empty=$((20 - filled))
            bar=$(printf '%0.s█' $(seq 1 $filled 2>/dev/null) 2>/dev/null || echo "")
            bar="${bar}$(printf '%0.s░' $(seq 1 $empty 2>/dev/null) 2>/dev/null || echo "")"
        else
            bar="░░░░░░░░░░░░░░░░░░░░"
        fi

        local status_color=$NC
        if [ $done -eq $count ] && [ $count -gt 0 ]; then
            status_color=$GREEN
        elif [ $done -gt 0 ]; then
            status_color=$YELLOW
        fi

        printf "Phase %-3s %-20s ${status_color}%s${NC} %d/%d\n" \
            "$phase" "${phase_names[$phase]}" "$bar" "$done" "$count"
    done

    echo "─────────────────────────────────────────────────────"
    printf "%-33s %d/%d tasks\n" "TOTAL" "$total_done" "$total_tasks"
    echo ""

    # Show last state
    local state=$(load_state)
    if [ -n "$state" ]; then
        echo -e "Last activity: ${YELLOW}${state}${NC}"
    fi

    # Show failures
    if [ -f "$FAIL_LOG" ] && [ -s "$FAIL_LOG" ]; then
        echo ""
        echo -e "${RED}Failed tasks:${NC}"
        cat "$FAIL_LOG" | while IFS='|' read -r tid mission ftime err; do
            echo -e "  ${RED}✘${NC} ${tid}: ${mission}"
        done
    fi
    echo ""
}

# ============================================================
# Unattended mode (no prompts, stop on failure)
# ============================================================

run_unattended() {
    local target=${1:-"all"}
    
    # Override the read commands to auto-continue
    export AUTO_CONTINUE=true
    
    log_warn "UNATTENDED MODE - will stop on first failure"
    
    if [ "$target" = "all" ]; then
        # Run all without prompts - stop on failure
        for phase in $(seq 0 12); do
            local tasks=$(get_phase_tasks "$phase")
            [ -z "$tasks" ] && continue
            
            for task_file in $tasks; do
                if ! run_single_task "$task_file"; then
                    log_fail "STOPPED: Task $(task_id_from_file "$task_file") failed"
                    log_info "Resume with: ./scripts/auto_run.sh resume"
                    exit 1
                fi
            done
            log_ok "Phase ${phase} complete"
        done
    else
        # Run specific phase unattended
        for task_file in $(get_phase_tasks "$target"); do
            if ! run_single_task "$task_file"; then
                log_fail "STOPPED: Task $(task_id_from_file "$task_file") failed"
                exit 1
            fi
        done
    fi
}

# ============================================================
# Main
# ============================================================

cd "$PROJECT_DIR"

case "${1:-help}" in
    phase)
        if [ -z "${2:-}" ]; then
            log_fail "Usage: $0 phase <number>"
            exit 1
        fi
        run_phase "$2"
        ;;
    all)
        run_all "${2:-0}"
        ;;
    task)
        if [ -z "${2:-}" ] || [ -z "${3:-}" ]; then
            log_fail "Usage: $0 task <phase> <task>"
            exit 1
        fi
        task_file="$TASKS_DIR/phase${2}/task_${2}.${3}.md"
        if [ ! -f "$task_file" ]; then
            log_fail "Task file not found: $task_file"
            exit 1
        fi
        run_single_task "$task_file"
        ;;
    resume)
        run_resume
        ;;
    status)
        show_status
        ;;
    unattended)
        run_unattended "${2:-all}"
        ;;
    help|--help|-h)
        echo ""
        echo "MedScribe AI - Auto Task Runner"
        echo "================================"
        echo ""
        echo "Commands:"
        echo "  phase <N>          Run all tasks in Phase N"
        echo "  all [start_phase]  Run all phases (default: from 0)"
        echo "  task <P> <T>       Run single task P.T"
        echo "  resume             Resume from last checkpoint"
        echo "  status             Show build progress"
        echo "  unattended [N|all] Run without prompts, stop on failure"
        echo ""
        echo "Examples:"
        echo "  ./scripts/auto_run.sh phase 0       # Build infrastructure"
        echo "  ./scripts/auto_run.sh all            # Build everything"
        echo "  ./scripts/auto_run.sh all 3          # Start from Phase 3"
        echo "  ./scripts/auto_run.sh task 1 3       # Run task 1.3 only"
        echo "  ./scripts/auto_run.sh resume         # Continue after failure"
        echo "  ./scripts/auto_run.sh status         # Check progress"
        echo "  ./scripts/auto_run.sh unattended     # Full auto, no prompts"
        echo "  ./scripts/auto_run.sh unattended 2   # Phase 2, no prompts"
        echo ""
        ;;
    *)
        log_fail "Unknown command: $1"
        echo "Use '$0 help' for usage"
        exit 1
        ;;
esac
