#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if systemctl --user is-active --quiet passerine-api.service || systemctl --user is-active --quiet passerine-worker.service; then
  echo 'Passerine is running under systemd. Use: systemctl --user restart passerine-api passerine-worker' >&2
  exit 1
fi
if [[ -f .env ]]; then set -a; source .env; set +a; fi
: "${PASSERINE_PASSWORD:?Set PASSERINE_PASSWORD to at least 12 characters in .env}"
export PYTHONPATH=backend
.venv/bin/python -m app.worker &
worker_pid=$!
trap 'kill "$worker_pid" 2>/dev/null || true' EXIT
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
