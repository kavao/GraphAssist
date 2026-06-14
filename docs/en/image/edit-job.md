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
uv run python tools/graphassist/graphassist.py job samples/jobs/resize_border.json --dry-run
```

Then run for real.

```bash
uv run python tools/graphassist/graphassist.py job samples/jobs/resize_border.json
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
| `composite` | `overlay`, `x`, `y`, `anchor` |
| `text` | `content`, `font`, `size`, `color`, `x`, `y`, `stroke_color`, `stroke_width` |
| `trim` | `background`, `padding`, `tolerance` |
| `flatten` | `background` |

Allowed `fill` / `color` / `background`: name or `#RRGGBB` (`transparent`, `white`, `black`, `red`, `green`, `blue`, `gray`)

## Composite example

```json
{
  "type": "composite",
  "overlay": "samples/source/badge.png",
  "x": 24,
  "y": 24,
  "anchor": "top_left"
}
```

## Prohibited (for LLMs)

- Generating or running ImageMagick / raw shell commands
- Read/write outside allowed paths
- Undefined operation types

## See also

- [batch.md](batch.md) — Batch manifest (mosaic + job in one JSON)
- [mosaic.md](mosaic.md) — CharGrid pixel art
