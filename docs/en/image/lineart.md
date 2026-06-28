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

## Input And Output Paths

| Kind | Allowed paths |
|------|---------------|
| Input LineArt JSON | `samples/lineart/`, `generated/lineart/` |
| Output SVG | `generated/vector/` |

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

## Related Pages

- For shape fields such as `role` and `container_id`, see [lineart-metadata.md](lineart-metadata.md).
- For validation reports and repair loops, see [lineart-validation.md](lineart-validation.md).
