# LineArt SVG Rendering

English · [日本語](../../ja/image/lineart.md)

This guide shows the shortest path from LineArt JSON to SVG. LineArt is a vector drawing format where the LLM writes structured JSON and Python validates and converts it instead of asking the LLM to hand-write SVG.

## When To Use This Document

Use this when you want to render a LineArt JSON sample as SVG.

The minimal prompt can be:

```text
Render this LineArt JSON as SVG.
```

With that prompt, the assistant uses `graphassist lineart render`, checks the input and output path with dry-run first, then writes the SVG.

If you want the assistant to create the LineArt artwork itself, you can simply ask:

```text
Create a simple icon with LineArt.
```

With that prompt, the assistant writes LineArt JSON under `samples/lineart/` or `generated/lineart/`, runs a dry-run, then generates SVG or PNG. For multi-step work, it creates a Batch manifest and chains `lineart.render` into ImageJob.

You can inspect these outputs:

| Output | Location |
|--------|----------|
| LineArt JSON | `samples/lineart/` or `generated/lineart/` |
| SVG | `generated/vector/` |
| PNG | `generated/images/` |
| Batch manifest | `samples/jobs/` |
| Run logs | `generated/logs/` |

## Command

Validate the sample LineArt JSON and preview the output path.

```powershell
# Dry-run — do not write the SVG yet
uv run graphassist lineart render samples/lineart/icon_minimal.json generated/vector/icon_minimal.svg --dry-run
```

If the dry-run looks right, generate the SVG.

```powershell
# Run — save the SVG under generated/vector/
uv run graphassist lineart render samples/lineart/icon_minimal.json generated/vector/icon_minimal.svg
```

After the command finishes, inspect `generated/vector/icon_minimal.svg`.

To generate a PNG at the same time, pass `--png`.

```powershell
# Generate SVG and PNG — save the PNG under generated/images/
uv run graphassist lineart render samples/lineart/icon_minimal.json generated/vector/icon_minimal.svg --png generated/images/icon_minimal.png --png-width 512
```

PNG rasterization uses the optional `resvg-py` or `cairosvg` backend. If neither is installed, run `uv sync --extra catalog`.

## Input And Output Paths

| Kind | Allowed paths |
|------|---------------|
| Input LineArt JSON | `samples/lineart/`, `generated/lineart/` |
| Output SVG | `generated/vector/` |
| Output PNG | `generated/images/` |

Absolute paths and parent traversal with `..` are not allowed.

## Minimal JSON

```json
{
  "version": "1.0",
  "canvas": {
    "width": 128,
    "height": 128,
    "background": "transparent"
  },
  "layers": [
    {
      "id": "main_layer",
      "shapes": [
        {
          "id": "wave_01",
          "type": "smooth_path",
          "role": "annotation",
          "points": [[32, 72], [52, 48], [76, 80], [96, 56]],
          "interpolation": "catmull_rom",
          "closed": false,
          "stroke": {
            "color": "#3a86ff",
            "width": 5,
            "join": "round",
            "cap": "round"
          }
        }
      ]
    }
  ]
}
```

`path` supports `M`, `L`, `Q`, `C`, and `Z` commands. `smooth_path` converts point lists to cubic Bezier curves with Catmull-Rom interpolation.

## Gradients

Define gradients in `definitions.gradients`, then reference them from a shape `fill`.

```json
{
  "definitions": {
    "gradients": {
      "panel_gradient": {
        "type": "linear",
        "from": [20, 20],
        "to": [108, 108],
        "stops": [
          {"offset": 0, "color": "#ffffff"},
          {"offset": 1, "color": "#dbeafe"}
        ]
      }
    }
  },
  "layers": [
    {
      "id": "main_layer",
      "shapes": [
        {
          "id": "panel_01",
          "type": "rect",
          "x": 20,
          "y": 20,
          "width": 88,
          "height": 88,
          "fill": {"type": "gradient", "ref": "panel_gradient"}
        }
      ]
    }
  ]
}
```

Use `linear` or `radial` for `type`. Each `stops[].offset` must be between `0` and `1`, in ascending order.

## Group, Transform, And Clip

Use `group` when you want to move, rotate, or scale multiple shapes together. Define `clip_path` entries in `definitions.clip_paths`, then reference them from a shape or group.

```json
{
  "definitions": {
    "clip_paths": {
      "badge_clip": {
        "shapes": [
          {"id": "badge_clip_rect", "type": "rect", "x": 70, "y": 78, "width": 28, "height": 24}
        ]
      }
    }
  },
  "layers": [
    {
      "id": "main_layer",
      "shapes": [
        {
          "id": "group_01",
          "type": "group",
          "opacity": 0.85,
          "clip_path": "badge_clip",
          "transform": {
            "translate": [0, 0],
            "rotate": -8,
            "rotate_origin": [84, 90],
            "scale": 1
          },
          "shapes": [
            {"id": "bar_01", "type": "rect", "x": 72, "y": 84, "width": 24, "height": 6}
          ]
        }
      ]
    }
  ]
}
```

`transform` supports `translate`, `rotate`, `rotate_origin`, and `scale`. `opacity` must be between `0` and `1`.

## Related Pages

- For shape fields such as `role` and `container_id`, see [lineart-metadata.md](lineart-metadata.md).
- For validation reports and repair loops, see [lineart-validation.md](lineart-validation.md).
