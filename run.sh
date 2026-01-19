#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "✔️  Missing required command: $1"
    echo "Please install $1 before running this script."
    exit 1
  fi
}

# Basic dependency checks
for cmd in python3 npm docker make; do
  require_command "$cmd"
done

if ! docker compose version >/dev/null 2>&1; then
  echo "✔️  'docker compose' is not available. Ensure Docker Compose v2+ is installed."
  exit 1
fi

setup_python() {
  echo "→ Preparing Python virtual environment"
  if [ ! -d "backend/venv" ]; then
    python3 -m venv backend/venv
  fi
  backend/venv/bin/python -m pip install --upgrade pip setuptools wheel >/dev/null
  backend/venv/bin/pip install -r backend/requirements.txt
}

setup_frontend() {
  echo "→ Ensuring frontend dependencies"
  cd frontend
  npm install
  cd "$ROOT_DIR"
}

echo "Starting Chimera full stack workflow..."
setup_python
setup_frontend

echo "→ Launching development data services"
make dev-db

backend_pid=0
frontend_pid=0
cleanup() {
  echo "→ Shutting down Chimera (backend:$backend_pid frontend:$frontend_pid)"
  set +e
  if [ "$backend_pid" -ne 0 ]; then
    kill "$backend_pid" >/dev/null 2>&1 || true
  fi
  if [ "$frontend_pid" -ne 0 ]; then
    kill "$frontend_pid" >/dev/null 2>&1 || true
  fi
  make down >/dev/null 2>&1 || true
}
trap cleanup EXIT
trap 'cleanup; exit 0' INT TERM

echo "→ Starting backend server"
backend/venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 >/tmp/chimera-backend.log 2>&1 &
backend_pid=$!

sleep 1

echo "→ Starting frontend dev server"
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173 >/tmp/chimera-frontend.log 2>&1 &
frontend_pid=$!
cd "$ROOT_DIR"

cat <<'EOF'

╔════════════════════════════════════════╗
║ Chimera development environment is up! ║
╠════════════════════════════════════════╣
║ Backend : http://localhost:8000         ║
║ Frontend: http://localhost:5173         ║
╠════════════════════════════════════════╣
║ Logs:
║   tail -f /tmp/chimera-backend.log
║   tail -f /tmp/chimera-frontend.log
╚════════════════════════════════════════╝
EOF

wait
