#!/bin/bash
# ============================================================
# MedScribe AI - Load Secrets from Google Cloud Secret Manager
# ============================================================
# Syncs all secrets from GCP Secret Manager into /opt/drscribe/.env
#
# Usage:
#   ./scripts/load_secrets.sh              # Sync all known secrets
#   ./scripts/load_secrets.sh --check      # Only verify, don't write
#   ./scripts/load_secrets.sh --restart    # Sync + restart affected services
# ============================================================

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$PROJECT_DIR/.env"
GCP_PROJECT="${GCP_PROJECT:-drscribe-prod-001}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

CHECK_ONLY=false
RESTART_SERVICES=false
for arg in "$@"; do
  case "$arg" in
    --check)   CHECK_ONLY=true ;;
    --restart) RESTART_SERVICES=true ;;
    -h|--help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
  esac
done

# Pre-flight checks
command -v gcloud >/dev/null 2>&1 || { echo -e "${RED}gcloud CLI not found${NC}"; exit 1; }

echo -e "${CYAN}>>> GCP project: ${GCP_PROJECT}${NC}"
gcloud config set project "$GCP_PROJECT" >/dev/null 2>&1

# Discover all secrets from Secret Manager
mapfile -t SECRETS < <(gcloud secrets list --format="value(name)" 2>/dev/null)

if [ "${#SECRETS[@]}" -eq 0 ]; then
  echo -e "${RED}No secrets found in Secret Manager (project: $GCP_PROJECT)${NC}"
  exit 1
fi

echo -e "${CYAN}>>> Found ${#SECRETS[@]} secrets in Secret Manager${NC}"

# Ensure .env exists
[ -f "$ENV_FILE" ] || touch "$ENV_FILE"
chmod 600 "$ENV_FILE"

# Backup current .env
if [ "$CHECK_ONLY" = false ]; then
  cp "$ENV_FILE" "${ENV_FILE}.bak.$(date +%Y%m%d_%H%M%S)"
fi

UPDATED=0
SKIPPED=0
ADDED=0

for secret_name in "${SECRETS[@]}"; do
  # Fetch secret value
  value="$(gcloud secrets versions access latest --secret="$secret_name" 2>/dev/null || true)"
  if [ -z "$value" ]; then
    echo -e "  ${YELLOW}! ${secret_name}: empty/inaccessible${NC}"
    continue
  fi

  # Check if key exists in .env
  current="$(grep -E "^${secret_name}=" "$ENV_FILE" | tail -n1 | cut -d= -f2- || true)"

  if [ "$current" = "$value" ]; then
    echo -e "  ${GREEN}= ${secret_name}: in sync${NC}"
    SKIPPED=$((SKIPPED+1))
    continue
  fi

  if [ "$CHECK_ONLY" = true ]; then
    if [ -z "$current" ]; then
      echo -e "  ${YELLOW}+ ${secret_name}: MISSING from .env${NC}"
    else
      echo -e "  ${YELLOW}~ ${secret_name}: differs from Secret Manager${NC}"
    fi
    continue
  fi

  # Update or append
  if [ -z "$current" ]; then
    echo "${secret_name}=${value}" >> "$ENV_FILE"
    echo -e "  ${GREEN}+ ${secret_name}: added${NC}"
    ADDED=$((ADDED+1))
  else
    # Replace using a safe sed (handles special chars via | delimiter)
    escaped_value="$(printf '%s\n' "$value" | sed -e 's/[\/&|]/\\&/g')"
    sed -i -E "s|^${secret_name}=.*|${secret_name}=${escaped_value}|" "$ENV_FILE"
    echo -e "  ${GREEN}~ ${secret_name}: updated${NC}"
    UPDATED=$((UPDATED+1))
  fi
done

echo ""
echo -e "${CYAN}>>> Summary:${NC} added=$ADDED updated=$UPDATED in-sync=$SKIPPED"

if [ "$CHECK_ONLY" = true ]; then
  exit 0
fi

if [ "$RESTART_SERVICES" = true ] && [ $((ADDED + UPDATED)) -gt 0 ]; then
  echo -e "${CYAN}>>> Restarting backend + celery-worker${NC}"
  cd "$PROJECT_DIR"
  docker-compose up -d backend celery-worker
fi

echo -e "${GREEN}>>> Done${NC}"
