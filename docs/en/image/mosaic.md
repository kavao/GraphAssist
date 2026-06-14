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
uv run graphassist mosaic decode \
  samples/mosaic/finale_rocket.json \
  generated/images/finale_rocket.png \
  --cell-size 8
```

`--cell-size` scales the preview (1 = one pixel per cell).

## encode (image → JSON)

```bash
uv run graphassist mosaic encode \
  samples/source/icon.png \
  generated/mosaic/icon.json \
  --grid 32x32 \
  --max-colors 16
```

Uses nearest-neighbor downscale and quantization — **lossy**; do not expect a perfect round trip.

## ImageJob `to_mosaic` (raster → CharGrid)

As the **last operation** in an ImageJob, encode the edited canvas to MosaicArt JSON (wrapper around `mosaic encode`).

```json
{
  "version": "1.0",
  "input": "samples/source/icon.png",
  "output": "generated/images/icon_edited.png",
  "operations": [
    {"type": "resize", "long_edge": 128},
    {
      "type": "to_mosaic",
      "grid": "16x16",
      "max_colors": 16,
      "mosaic_output": "generated/mosaic/icon.json"
    }
  ]
}
```

- `to_mosaic` must be the **final** operation
- `grid`: `"WxH"` or `[width, height]`
- Job `output` is still the **PNG**; `mosaic_output` is the **JSON** path

```bash
uv run graphassist job samples/jobs/to_mosaic_pipeline.json
```

## export (JS snippet)

```bash
uv run graphassist mosaic export \
  samples/mosaic/finale_rocket.json \
  --format js \
  --name FINALE_ROCKET
```

Prints `const FINALE_ROCKET = [...]` to stdout for chat copy-paste.

## Sample

| JSON | Content | decode example |
|------|---------|----------------|
| [finale_rocket.json](../../../samples/mosaic/finale_rocket.json) | Rocket 8×10 | `uv run graphassist mosaic decode samples/mosaic/finale_rocket.json generated/images/finale_rocket.png --cell-size 8` |
| [parakeet.json](../../../samples/mosaic/parakeet.json) | Parakeet (single) | `… parakeet.json generated/images/parakeet.png --cell-size 8` |
| [parrot.json](../../../samples/mosaic/parrot.json) | Parrot (single) | `… parrot.json generated/images/parrot.png --cell-size 8` |
| [birds_on_trunk.json](../../../samples/mosaic/birds_on_trunk.json) | Two birds + branch (composite) | `… birds_on_trunk.json generated/images/birds_on_trunk_base.png --cell-size 8` |

Titled final PNG: use Batch manifest [birds_on_trunk_pipeline.json](../../../samples/jobs/birds_on_trunk_pipeline.json) (below).

## Mosaic + text

Readable Japanese titles should use **ImageJob `text`**, not CharGrid rows.  
Use a Batch manifest (`mosaic.decode` → `job`) as the canonical one-command pipeline.

```bash
uv run graphassist run samples/jobs/birds_on_trunk_pipeline.json
```

See [batch.md](batch.md) — “Previous command output as job input”.

## Merging multiple JSON files

Compose part mosaics (e.g. `parakeet.json` + `parrot.json`) with merge:

```bash
uv run graphassist mosaic compose-birds generated/mosaic/birds_on_trunk_merged.json
uv run python scripts/merge_birds_on_trunk.py
```

Generic merge:

```bash
uv run graphassist mosaic merge generated/mosaic/merged.json \
  --canvas 50x26 \
  --layer samples/mosaic/parakeet.json@8,6 \
  --layer samples/mosaic/parrot.json@24,3
```

## See also

- [edit-job.md](edit-job.md) — ImageJob editing
- [quickstart.md](../quickstart.md)
