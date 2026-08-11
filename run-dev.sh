#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Python environment not found. Run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi

if ! command -v node >/dev/null 2>&1; then
  if [[ -s "$HOME/.nvm/nvm.sh" ]]; then
    # shellcheck disable=SC1090
    source "$HOME/.nvm/nvm.sh"
  fi
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "Node.js 20.19 or newer is required. Install/activate Node, then run this command again."
  exit 1
fi

LAN_IP="$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || true)"
LAN_IP="${LAN_IP:-127.0.0.1}"

"$VENV_PYTHON" "$PROJECT_DIR/manage.py" migrate
"$VENV_PYTHON" "$PROJECT_DIR/manage.py" runserver 0.0.0.0:8000 &
BACKEND_PID=$!
trap 'kill "$BACKEND_PID" 2>/dev/null || true' EXIT INT TERM

echo "Django API: http://$LAN_IP:8000/api/scenarios/"
echo "Starting Expo with API URL http://$LAN_IP:8000/api"

cd "$PROJECT_DIR/mobile"
EXPO_PUBLIC_API_URL="http://$LAN_IP:8000/api" npm start
