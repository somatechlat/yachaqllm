#!/usr/bin/env bash
# Runner to start a full Asamblea crawl under nohup on the VM.
# Sources the project's venv and environment file, respects robots' crawl-delay,
# writes PID and logs for monitoring.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="${HOME}/venv_yachaq"
ENV_FILE="${HOME}/.yachaq_env"
PID_PATH="${HOME}/asamblea_full.pid"
LOG_PATH="${HOME}/asamblea_full.log"

# Export polite crawler settings
export ASAMBLEA_CRAWL_DELAY=${ASAMBLEA_CRAWL_DELAY:-10}
export PYTHONUNBUFFERED=1

if [ -f "$ENV_FILE" ]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

if [ -d "$VENV_DIR" ]; then
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
fi

cd "$ROOT_DIR"

nohup python3 rag/ingest/real_asamblea_scraper.py \
  --issue-url "https://www.asambleanacional.gob.ec/es/leyes-aprobadas" \
  --verbose --force >> "$LOG_PATH" 2>&1 &

echo $! > "$PID_PATH"
echo "Started Asamblea full crawler: PID=$(cat $PID_PATH), log=$LOG_PATH"
