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
- Downloads the CLI binary from GitHub Releases (network required)
- **Fetches fonts** — Japanese (Noto / Misaki / PixelMplus), English (Inter / Roboto / Source Sans 3 / DejaVu); Meiryo copied from Windows when available (mirrored to `assets/fonts/`, `NOTICES.md` generated)
- `runtime/manifest.local.json` (install record)
- Falls back to source execution if the binary download fails; optional fonts are skipped when unavailable

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

`setup-runtime` installs ImageJob `text` fonts under **`runtime/assets/fonts/`** and mirrors them to `assets/fonts/`.

| Font | Use | Source |
|------|-----|--------|
| `NotoSansJP-Regular.otf` | Japanese (recommended) | Download (OFL) |
| `misaki_gothic.ttf` | 8×8 dot Japanese | Download |
| `PixelMplus12-Regular.ttf` | Pixel-style Japanese | Download (M+ LICENSE) |
| `DejaVuSans.ttf` | Latin, etc. | Download |
| `InterVariable.ttf` | English UI | Download (OFL) |
| `Roboto-Regular.ttf` | English UI | Download (Apache 2.0) |
| `SourceSans3-Regular.ttf` | English UI | Download (OFL) |
| `Meiryo.ttc` | Windows optional | System font copy only (not redistributable) |

Copyright and licenses: [assets/fonts/README.md](../../../assets/fonts/README.md) and `assets/fonts/NOTICES.md` after setup.

JSON still references `assets/fonts/...`. `resolve_font` checks runtime first.

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
