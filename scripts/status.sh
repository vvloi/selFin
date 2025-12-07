#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$DIR/uvicorn.pid"
LOG_FILE="$DIR/uvicorn.log"

if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  if kill -0 "$PID" 2>/dev/null; then
    echo "uvicorn running (pid $PID)"
    echo "Last 20 log lines from $LOG_FILE:"
    tail -n 20 "$LOG_FILE" || true
    exit 0
  else
    echo "Pid file exists but process $PID not running"
    exit 1
  fi
else
  echo "Server not running (no $PID_FILE)"
  exit 1
fi
