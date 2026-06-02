#!/usr/bin/env bash
# Convenience launcher for the backend.
# Creates a virtualenv on first run, installs deps, then starts the API.
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "Creating virtualenv (.venv)..."
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo "Starting API on http://localhost:8000 (docs at /docs) ..."
exec uvicorn app.main:app --reload --port 8000
