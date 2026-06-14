# GraphAssist — Image Processing CLI

English · [日本語](README.ja.md)

**GraphAssist** is a **Pillow + NumPy** image processing CLI for LLM-assisted editors such as Cursor.

## Concept

**Offload repetitive, uncreative image work to the tool** — resizing, format conversion, trimming, alignment, and similar chores with fixed steps but little room for creativity belong in the CLI and ImageJob JSON. You describe *what* you want via JSON or flags; Python validates and runs it. See [overview (plans)](_workingspace/plans/overview.md#コンセプト).

## Setup

### 1. Python dependencies

```bash
uv sync
```

### 2. Runtime (binaries, fonts — outside Git)

```powershell
.\scripts\setup-runtime.ps1
```

See [Runtime setup](docs/en/setup/runtime.md).

## 30-Second Quickstart

```bash
uv run graphassist convert samples/source/your.png generated/images/out --long-edge 1024 --format webp
uv run graphassist job samples/jobs/resize_border.json --dry-run
uv run graphassist mosaic decode samples/mosaic/finale_rocket.json generated/images/rocket.png --cell-size 8
```

`runtime/` and `generated/` are gitignored.

## Documentation

| Guide | Description |
|-------|-------------|
| [Docs index](docs/README.md) | Entry point |
| [CLI reference](docs/en/image/operations.md) | All subcommands |
| [Runtime setup](docs/en/setup/runtime.md) | Binaries, fonts, weights |
| [ImageJob](docs/en/image/edit-job.md) | JSON pipeline |
| [CharGrid](docs/en/image/mosaic.md) | Pixel art |
| [Work plan](_workingspace/plans/work-plan.md) | Phases |
| [Deployment design](_workingspace/plans/deployment-design.md) | Source vs runtime |

## Status

| Phase | Scope | Status |
|-------|-------|--------|
| 0–3 | convert, ImageJob, composite | Done |
| 4–7 | text, trim, diff, inspect, sheets, palette | Done |
| M | CharGrid + Batch | Done |
| Post-7 | runtime install, `src/` migration | In progress |

## License

MIT License — see [LICENSE](LICENSE).
