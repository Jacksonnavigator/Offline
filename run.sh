#!/usr/bin/env bash
set -euo pipefail

# run.sh - activates the project's virtualenv (if present) and runs the app
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PY="$DIR/venv/bin/python"

if [ -x "$VENV_PY" ]; then
  echo "Activating virtualenv at $DIR/venv"
  export PATH="$DIR/venv/bin:$PATH"
else
  echo "Warning: virtualenv not found at $DIR/venv — falling back to system python"
  VENV_PY="/usr/bin/python3"
fi

exec "$VENV_PY" "$DIR/app.py" api "$@"
