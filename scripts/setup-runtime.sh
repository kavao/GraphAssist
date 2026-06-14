#!/usr/bin/env bash
# GraphAssist runtime bootstrap (idempotent, re-runnable).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ARGS=("$ROOT/scripts/runtime_fetch.py")
if [[ "${1:-}" == "--force" ]]; then
  ARGS+=("--force")
fi
python "${ARGS[@]}"
