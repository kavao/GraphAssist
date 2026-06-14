#!/usr/bin/env bash
# GraphAssist runtime bootstrap (idempotent, re-runnable).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME="${GRAPHASSIST_RUNTIME:-$ROOT/runtime}"

mkdir -p "$RUNTIME/bin" \
         "$RUNTIME/assets/fonts" \
         "$RUNTIME/assets/weights/bg-removal"

META="$ROOT/.rulesync/metadata/graphassist.json"
TOOL_VERSION="unknown"
if [[ -f "$META" ]]; then
  TOOL_VERSION="$(python -c "import json; print(json.load(open('$META'))['version'])")"
fi

BIN="$RUNTIME/bin/graphassist"
BIN_EXE="$RUNTIME/bin/graphassist.exe"
PRESENT=false
[[ -x "$BIN" || -f "$BIN_EXE" ]] && PRESENT=true

LOCAL_MANIFEST="$RUNTIME/manifest.local.json"
cat > "$LOCAL_MANIFEST" <<EOF
{
  "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "runtime_root": "$RUNTIME",
  "components": [
    {
      "id": "graphassist",
      "kind": "binary",
      "version": "$TOOL_VERSION",
      "path": "$BIN",
      "present": $PRESENT
    }
  ]
}
EOF

echo "GraphAssist runtime setup"
echo "  runtime: $RUNTIME"
echo "  tool version (metadata): $TOOL_VERSION"
if $PRESENT; then
  echo "  binary: OK"
else
  echo "  binary: not installed"
  echo "    uv run python tools/graphassist/graphassist.py --version"
fi
echo "  manifest: $LOCAL_MANIFEST"
echo "Done."
