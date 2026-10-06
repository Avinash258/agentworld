#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT/backend"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi
PYTHONPATH=. .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8765 &
BACK_PID=$!

cd "$ROOT/frontend"
if [[ ! -d node_modules ]]; then
  npm install
fi
npm run dev &
FRONT_PID=$!

echo "Runtime:  http://127.0.0.1:8765/api/status"
echo "Console:  http://127.0.0.1:43123"
echo "PIDs: backend=$BACK_PID frontend=$FRONT_PID"
wait
