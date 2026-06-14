# Runtime setup

English · [日本語](../ja/setup/runtime.md)

GraphAssist separates **source (Git)** from **installation (runtime)**.

| Layer | Path | Git |
|-------|------|-----|
| Source | `tools/graphassist/` (future: `src/graphassist/`) | Tracked |
| Runtime | `runtime/` | **Not tracked** |
| Output | `generated/` | Not tracked |

## First setup (re-runnable)

```powershell
.\scripts\setup-runtime.ps1
```

```bash
chmod +x scripts/setup-runtime.sh
./scripts/setup-runtime.sh
```

This creates:

- `runtime/bin/`, `runtime/assets/fonts/`, `runtime/assets/weights/`
- `runtime/manifest.local.json` (install record)
- Falls back to source execution if no binary is present

## Binary placement

Put `graphassist.exe` from Releases at:

```text
runtime/bin/graphassist.exe
```

Do not commit it to Git.

## Fonts

For ImageJob `text`, place fonts under:

```text
runtime/assets/fonts/DejaVuSans.ttf
```

Legacy fallback: `assets/fonts/` during migration.

## Future AI weights

Reserved layout for optional models (e.g. background removal):

```text
runtime/assets/weights/<component-id>/
```

Declared in `.rulesync/metadata/runtime-manifest.jsonc` as optional. Core Pillow CLI works without them.

## CLI priority

1. `GRAPHASSIST_BIN` env var
2. `runtime/bin/graphassist.exe` if present
3. Dev: `uv run python tools/graphassist/graphassist.py`

## Environment variables

| Variable | Description |
|----------|-------------|
| `GRAPHASSIST_RUNTIME` | Runtime root (default `<project>/runtime`) |
| `GRAPHASSIST_BIN` | Full path to CLI binary |

## Design details

See [_workingspace/plans/deployment-design.md](../../../_workingspace/plans/deployment-design.md)

## See also

- [operations.md](../image/operations.md)
- [quickstart.md](../quickstart.md)
