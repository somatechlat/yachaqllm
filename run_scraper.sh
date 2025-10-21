#!/usr/bin/env bash
set -euo pipefail
cd ~/yachaqllm_repo || exit 1
# activate venv
source .venv/bin/activate
LOG=registro_oficial_run.log
PIDFILE=registro_oficial.pid
echo "Starting scraper at $(date)" >> "$LOG"
# start scraper in background under venv
.venv/bin/python rag/ingest/real_registro_oficial_scraper.py --back-to-year 2020 --upload --limit 0 >> "$LOG" 2>&1 &
# write pid
echo $! > "$PIDFILE"
# report
echo "Launcher started, pid=$(cat "$PIDFILE" 2>/dev/null || echo none)"
