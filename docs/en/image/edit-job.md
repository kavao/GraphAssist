# Edit Job Guide

English · [日本語](../../ja/image/edit-job.md)

ImageJob describes edit steps for a single image as JSON and runs them via `graphassist job`.  
LLMs produce ImageJob JSON; Python validates with Pydantic and executes with Pillow.

## Path restrictions

| Kind | Allowed path |
|------|----------------|
| Input / overlay | Under `samples/source/` only |
| Output | Under `generated/` only |

Absolute paths and `..` parent traversal are rejected.

## Minimal example

```json
{
  "version": "1.0",
  "input": "samples/source/sample.png",
  "output": "generated/images/sample_out.png",
  "operations": [
    {"type": "resize", "width": 1024},
    {"type": "border", "size": 20, "color": "white"}
  ]
}
```

## Run workflow

Confirm steps and output path with dry-run first.

```bash
uv run graphassist job samples/jobs/resize_border.json --dry-run
```

Then run for real.

```bash
uv run graphassist job samples/jobs/resize_border.json
```

Logs (JSONL, Markdown, replay script) are written under `generated/logs/`.

## Operations (v1.0)

| type | Main fields |
|------|-------------|
| `resize` | `width`, `height`, or `long_edge` |
| `crop` | `width`, `height`, `x`, `y` |
| `extend` | `left`, `right`, `top`, `bottom`, `fill` |
| `rotate` | `degrees`, `fill` |
| `border` | `size`, `color` |
| `composite` | `overlay` **or** `overlay_asset` (catalog id), `x`, `y`, `anchor` |
| `text` | `content`, `font`, `size`, `color`, `x`, `y`, `stroke_color`, `stroke_width` |
| `trim` | `background`, `padding`, `tolerance` |
| `flatten` | `background` |
| `adjust` | `brightness`, `contrast`, `saturation` (0..3, 1.0 = no change) |
| `grayscale` | `mode`: `luminance` (Rec.601, aligned with `analyze`) |
| `sepia` | `strength` (0..1) |
| `curve` | `mode`: `gamma` (`gamma` 0.1..5) or `levels` (`black`, `white`) |
| `quantize` | `colors` (2..256), `dither` (bool) |
| `posterize` | `bits` (1..8) |
| `blur` | `kind`: `gaussian` / `box`, `radius` (0..50) |
| `sharpen` | `kind`: `enhance` (`amount`) or `unsharp` (`radius`, `percent`, `threshold`) |
| `to_mosaic` | `grid` (`WxH` or `[w,h]`), `max_colors`, `mosaic_output` (**last op only**) |

Allowed `fill` / `color` / `background`: name or `#RRGGBB` (`transparent`, `white`, `black`, `red`, `green`, `blue`, `gray`)

## Tone adjustment example

```json
{
  "version": "1.0",
  "input": "samples/source/job_test_base.png",
  "output": "generated/images/tone_pipeline_out.png",
  "operations": [
    {"type": "adjust", "brightness": 1.15, "contrast": 1.05},
    {"type": "curve", "mode": "gamma", "gamma": 1.1},
    {"type": "quantize", "colors": 16, "dither": false}
  ]
}
```

Use `analyze --compare` for before/after checks. Samples: `samples/jobs/adjust_brighten.json`, `samples/jobs/tone_pipeline.json`

## Composite example

Path (classic):

```json
{
  "type": "composite",
  "overlay": "samples/source/badge.png",
  "x": 24,
  "y": 24,
  "anchor": "top_left"
}
```

Catalog id (after materialize, or auto-fetch at run time):

```json
{
  "type": "composite",
  "overlay_asset": "ornament-fleur-de-lis-simple",
  "x": 24,
  "y": 24
}
```

Ids must exist in `.rulesync/metadata/asset-catalog.jsonc`. Index: `samples/jobs/catalog/index.json`

## Catalog input (`input_asset`)

```json
{
  "version": "1.0",
  "input_asset": "ui-panel-dark",
  "output": "generated/images/card.png",
  "operations": []
}
```

Use **either** `input` or `input_asset`, not both.

## `anchor: center`

Treat `x`, `y` as the overlay center point.

Example: `samples/jobs/demo_catalog_anchor_center.json`

## Text on CharGrid art

For Japanese titles on pixel art, use **Batch `mosaic.decode` → `job` (`text`)**, not CharGrid row embedding.

```bash
uv run graphassist run samples/jobs/birds_on_trunk_pipeline.json
```

## Prohibited (for LLMs)

- Generating or running ImageMagick / raw shell commands
- Read/write outside allowed paths
- Undefined operation types

## See also

- [batch.md](batch.md) — Batch manifest (mosaic + job in one JSON)
- [mosaic.md](mosaic.md) — CharGrid pixel art
