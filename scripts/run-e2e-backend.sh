#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
E2E_DB_PATH="${E2E_DB_PATH:-/tmp/crushme-e2e.sqlite3}"
E2E_BACKEND_PORT="${E2E_BACKEND_PORT:-8001}"

if [[ "$(basename "$E2E_DB_PATH")" != *e2e* ]]; then
  echo 'Refusing E2E startup: E2E_DB_PATH filename must contain "e2e".' >&2
  exit 2
fi

if [[ ! "$E2E_BACKEND_PORT" =~ ^[0-9]+$ ]] || (( E2E_BACKEND_PORT < 1024 || E2E_BACKEND_PORT > 65535 )); then
  echo 'Refusing E2E startup: E2E_BACKEND_PORT must be between 1024 and 65535.' >&2
  exit 2
fi

if [[ -n "${E2E_PYTHON:-}" ]]; then
  PYTHON="$E2E_PYTHON"
elif [[ -x "$BACKEND_DIR/venv_cpu/bin/python" ]]; then
  PYTHON="$BACKEND_DIR/venv_cpu/bin/python"
else
  PYTHON="python"
fi

export DJANGO_ENV=e2e
export DJANGO_SETTINGS_MODULE=crushme_project.settings_e2e
export E2E_DB_PATH

cd "$BACKEND_DIR"
"$PYTHON" manage.py migrate --noinput
"$PYTHON" manage.py flush --noinput
"$PYTHON" manage.py seed_e2e_data
exec "$PYTHON" manage.py runserver "127.0.0.1:$E2E_BACKEND_PORT" --noreload --insecure
