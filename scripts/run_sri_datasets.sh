#!/usr/bin/env bash
# Runner for SRI datasets scraper (nohup)
set -euo pipefail
BASEDIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$HOME/.yachaq_env" || true
source "$HOME/venv_yachaq/bin/activate" || true
cd "$BASEDIR"

LOG="$HOME/sri_datasets_full.log"
PIDFILE="$HOME/sri_datasets_full.pid"

echo "Starting SRI datasets scraper; logs -> $LOG"
nohup python3 rag/ingest/real_sri_datasets_scraper.py --verbose --force >> "$LOG" 2>&1 &
echo $! > "$PIDFILE"
echo "PID $(cat $PIDFILE)" 
