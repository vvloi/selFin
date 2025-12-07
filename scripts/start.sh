#!/usr/bin/env bash
set -euo pipefail

# Start the uvicorn server in background, write pid to uvicorn.pid
# Usage: RELOAD=true ./scripts/start.sh

DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DIR"
VENV=".venv"
PID_FILE="$DIR/uvicorn.pid"
LOG_FILE="$DIR/uvicorn.log"

RELOAD_FLAG=""
if [ "${RELOAD:-false}" = "true" ]; then
  RELOAD_FLAG="--reload"
fi

if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  if kill -0 "$PID" 2>/dev/null; then
    echo "Server already running (pid $PID)"
    exit 0
  else
    echo "Stale pid file found, removing"
    rm -f "$PID_FILE"
  fi
fi

if [ ! -x "$DIR/$VENV/bin/activate" ]; then
  echo "Virtualenv not found at $DIR/$VENV. Create it first: python -m venv .venv"
  exit 1
fi

source "$DIR/$VENV/bin/activate"

nohup "$DIR/$VENV/bin/uvicorn" app.main:app --host 127.0.0.1 --port 8000 $RELOAD_FLAG > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
echo "Started uvicorn (pid $(cat $PID_FILE)), log: $LOG_FILE"
