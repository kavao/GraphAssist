# Runtime setup

English · [日本語](../ja/setup/runtime.md)

GraphAssist separates **source (Git)** from **installation (runtime)**.

| Layer | Path | Git |
|-------|------|-----|
| Source | `src/graphassist/` | Tracked |
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
- Downloads binary from GitHub Releases when `runtime-manifest.jsonc` URLs are set (network required)
- `runtime/manifest.local.json` (install record)
- Falls back to source execution if download fails

Force re-download:

```powershell
.\scripts\setup-runtime.ps1 -Force
```

## Binary placement

Normally `setup-runtime` fetches from [GitHub Releases](https://github.com/kavao/GraphAssist/releases). To install manually:

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
3. Dev: `uv run graphassist`

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
