#!/bin/bash
# MedScribe AI - Task Runner for Claude Code
# Usage: ./scripts/run_task.sh <phase> <task>
# Example: ./scripts/run_task.sh 0 1

PHASE=$1
TASK=$2
TASK_FILE=".claude/tasks/phase${PHASE}/task_${PHASE}.${TASK}.md"

if [ ! -f "$TASK_FILE" ]; then
    echo "ERROR: Task file not found: $TASK_FILE"
    echo "Available tasks:"
    ls .claude/tasks/phase${PHASE}/ 2>/dev/null || echo "Phase ${PHASE} not found"
    exit 1
fi

echo "=========================================="
echo "Running: Phase ${PHASE} - Task ${PHASE}.${TASK}"
echo "File: ${TASK_FILE}"
echo "=========================================="

claude -p "$(cat $TASK_FILE)"
