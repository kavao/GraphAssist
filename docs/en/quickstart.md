# Quickstart

English · [日本語](../ja/quickstart.md)

GraphAssist is a Pillow-based image CLI. Run commands from the project root.

## Setup

```bash
pip install -r requirements.txt
```

Or:

```bash
uv sync
```

## Runtime (optional, recommended)

Binaries and fonts live outside Git under `runtime/`.

```powershell
.\scripts\setup-runtime.ps1
```

See [setup/runtime.md](setup/runtime.md).

## Batch convert

Convert PNG to WebP and resize so the long edge is 1024px.

```bash
uv run graphassist convert samples/source/your.png generated/images/out --long-edge 1024 --format webp
```

On success, `generated/images/out.webp` is created.

## Edit job

Apply resize and border via ImageJob JSON. Run dry-run first.

```bash
uv run graphassist job samples/jobs/resize_border.json --dry-run
uv run graphassist job samples/jobs/resize_border.json
```

See [edit-job.md](image/edit-job.md) for details.

## Asset catalog (composite)

Fetch curated overlays and UI panels, then reference catalog ids in ImageJob:

```powershell
uv run graphassist assets fetch
uv run graphassist job samples/jobs/demo_catalog_minimal.json
uv run graphassist run samples/jobs/demo_catalog_pipeline_asset_ids.json
```

Index: [samples/jobs/catalog/index.json](../../samples/jobs/catalog/index.json) · [samples/jobs/README.md](../../samples/jobs/README.md) · Skill: [catalog-assets](../../.rulesync/skills/catalog-assets/SKILL.md)
