#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")/.." && pwd)"

"$DIR/scripts/stop.sh" || true
sleep 1
"$DIR/scripts/start.sh"
