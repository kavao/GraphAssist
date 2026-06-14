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
- **Fetches fonts** — copies Git-bundled DejaVu / PixelMplus12 into runtime, then downloads Japanese (Noto / Misaki), English (Inter / Roboto / Source Sans 3); Meiryo copied from Windows when available (mirrored to `assets/fonts/`, `NOTICES.md` generated)
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

**Git bundle (minimum):** `assets/fonts/DejaVuSans.ttf` and `PixelMplus12-Regular.ttf` are available immediately after clone (birds demo, basic tests).

`setup-runtime` installs additional ImageJob `text` fonts under **`runtime/assets/fonts/`** and mirrors them to `assets/fonts/`.

| Font | Use | Source |
|------|-----|--------|
| `DejaVuSans.ttf` | Latin, etc. | **Git bundle** / setup |
| `PixelMplus12-Regular.ttf` | Pixel-style Japanese | **Git bundle** / setup |
| `NotoSansJP-Regular.otf` | Japanese (recommended) | Download (OFL) |
| `misaki_gothic.ttf` | 8×8 dot Japanese | Download |
| `InterVariable.ttf` | English UI | Download (OFL) |
| `Roboto-Regular.ttf` | English UI | Download (Apache 2.0) |
| `SourceSans3-Regular.ttf` | English UI | Download (OFL) |
| `Meiryo.ttc` | Windows optional | System font copy only (not redistributable) |

Copyright and licenses: [assets/fonts/README.md](../../../assets/fonts/README.md) and `assets/fonts/NOTICES.md` after setup.

JSON still references `assets/fonts/...`. `resolve_font` checks runtime first.

## Asset catalog (CC0 / public domain)

`setup-runtime` fetches SVG assets from `.rulesync/metadata/asset-catalog.jsonc` and mirrors SVG + PNG to `samples/source/catalog/`.

```powershell
.\scripts\setup-runtime.ps1
uv run python scripts/runtime_fetch.py --catalog-only
uv run graphassist assets fetch --id ornament-fleur-de-lis-simple
```

PNG rasterization requires **resvg-py** (`uv sync --extra catalog` or dev dependencies).

Index: [samples/jobs/catalog/index.json](../../../samples/jobs/catalog/index.json)  
Copyright: `assets/catalog/NOTICES.md` after setup.

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

## Adopting in another project

**Default: pattern B (source injection)** — ship `src/graphassist/` + rulesync + samples in the same repo. CLI-only adoption loses most LLM JSON pipeline value; **include rulesync (`graphassist.md` + ga-* skills)**.

Full checklist, merge steps, and GitHub references: **[Adoption guide](adoption.md)**

After adoption:

1. Add `runtime/**`, `generated/**`, and rulesync outputs to the adoptee `.gitignore`
2. `uv sync` → `corepack pnpm dlx rulesync generate` (when using dna_kernel)
3. Run **First setup** on this page (`setup-runtime`)
4. Skills prefer `runtime/bin`, then `uv run graphassist`

## Design details

See [_workingspace/plans/deployment-design.md](../../../_workingspace/plans/deployment-design.md)

## See also

- [operations.md](../image/operations.md)
- [quickstart.md](../quickstart.md)
