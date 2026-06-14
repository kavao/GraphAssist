# CharGrid (MosaicArt) guide

English · [日本語](../ja/image/mosaic.md)

**MosaicArt JSON** is an LLM-friendly grid format: one character per cell plus a palette map.  
Use `graphassist mosaic` for **JSON ↔ image** conversion and **JS snippet** export.

## Path rules

| Kind | Allowed path |
|------|----------------|
| encode input | `samples/source/` |
| MosaicArt JSON (decode / export input) | `samples/mosaic/`, `generated/mosaic/` |
| encode output JSON | `generated/mosaic/` |
| decode output image | `generated/` |

## MosaicArt JSON (v1.0)

```json
{
  "version": "1.0",
  "width": 8,
  "height": 10,
  "transparent": ".",
  "palette": {
    "B": "#d7c6eb",
    "W": "#65d8ff",
    "F": "#ffae42",
    "R": "#ff5f4d"
  },
  "rows": ["...BB...", "..BBBB.."]
}
```

- Each row length must equal `width`
- Row count must equal `height`
- `palette` allows up to 32 colors (16 recommended for LLM use)
- The `transparent` character cannot be a palette key

## decode (JSON → image)

```bash
uv run python tools/graphassist/graphassist.py mosaic decode \
  samples/mosaic/finale_rocket.json \
  generated/images/finale_rocket.png \
  --cell-size 8
```

`--cell-size` scales the preview (1 = one pixel per cell).

## encode (image → JSON)

```bash
uv run python tools/graphassist/graphassist.py mosaic encode \
  samples/source/icon.png \
  generated/mosaic/icon.json \
  --grid 32x32 \
  --max-colors 16
```

Uses nearest-neighbor downscale and quantization — **lossy**; do not expect a perfect round trip.

## export (JS snippet)

```bash
uv run python tools/graphassist/graphassist.py mosaic export \
  samples/mosaic/finale_rocket.json \
  --format js \
  --name FINALE_ROCKET
```

Prints `const FINALE_ROCKET = [...]` to stdout for chat copy-paste.

## Sample

- [samples/mosaic/finale_rocket.json](../../../samples/mosaic/finale_rocket.json) — rocket 8×10

## See also

- [edit-job.md](edit-job.md) — ImageJob editing
- [quickstart.md](../quickstart.md)
