#!/usr/bin/env bash
# Equivalente ao dev.ps1 para Linux/macOS (útil em CI ou WSL).
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
(cd "$ROOT/backend" && .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8765 --reload) &
(cd "$ROOT/frontend" && npm run dev) &
wait
