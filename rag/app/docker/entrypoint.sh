#!/usr/bin/env bash
# entrypoint: use $PORT if provided, default 8000
PORT=${PORT:-8000}
exec uvicorn main:app --host 0.0.0.0 --port "$PORT"
