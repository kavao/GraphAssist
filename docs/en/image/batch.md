# Batch manifest (multiple commands)

English · [日本語](../ja/image/batch.md)

Run **multiple commands from one JSON file** with `graphassist run`.  
LLMs can describe an entire pipeline in a single manifest.

## Location

| Kind | Path |
|------|------|
| Batch manifest | `samples/jobs/` |

Single ImageJob files (no `commands` key) still use `graphassist job`.

## Format (v1.0)

```json
{
  "version": "1.0",
  "commands": [
    {
      "type": "mosaic.decode",
      "input": "samples/mosaic/finale_rocket.json",
      "output": "generated/images/rocket.png",
      "cell_size": 8
    },
    {
      "type": "mosaic.decode",
      "art": {
        "version": "1.0",
        "width": 4,
        "height": 2,
        "transparent": ".",
        "palette": { "R": "#ff0000" },
        "rows": ["RR..", "..RR"]
      },
      "output": "generated/images/inline.png",
      "cell_size": 4
    },
    {
      "type": "job",
      "input": "samples/source/icon.png",
      "output": "generated/images/icon_out.png",
      "operations": [
        {"type": "resize", "long_edge": 128}
      ]
    }
  ]
}
```

## Command types

| type | Description |
|------|-------------|
| `job` | Same fields as ImageJob (`input`, `output`, `operations`) |
| `mosaic.decode` | CharGrid → image. Use **either** `input` (JSON path) **or** inline `art` |
| `mosaic.encode` | Image → MosaicArt JSON |
| `mosaic.export` | MosaicArt JSON → JS / JSON text |

| `mosaic.export` | MosaicArt JSON → JS / JSON text |
| `assets.materialize` | Fetch and mirror catalog assets (`ids` omitted = all enabled) |

## Catalog + Job

```json
{
  "version": "1.0",
  "commands": [
    {"type": "assets.materialize", "ids": ["ornament-fleur-de-lis-simple"]},
    {
      "type": "job",
      "input": "samples/source/demo_text_base.png",
      "output": "generated/images/demo_catalog_pipeline.png",
      "operations": [
        {
          "type": "composite",
          "overlay": "samples/source/catalog/ornament-fleur-de-lis-simple.png",
          "x": 308,
          "y": 72,
          "anchor": "top_left"
        }
      ]
    }
  ]
}
```

## Previous command output as job input

When **`job.input` equals the previous command’s `output` path** in a Batch manifest, inputs under `generated/` are allowed (standalone `graphassist job` still requires `samples/source/` only).

See [birds_on_trunk_pipeline.json](../../../samples/jobs/birds_on_trunk_pipeline.json) for a `mosaic.decode` → `job` example with title text.

## Run

```bash
uv run graphassist run samples/jobs/mosaic_pipeline.json --dry-run
uv run graphassist run samples/jobs/mosaic_pipeline.json
```

Logs are written to `generated/logs/` as JSONL.

## Sample

- [samples/jobs/README.md](../../../samples/jobs/README.md) — Demo index
- [samples/jobs/mosaic_pipeline.json](../../../samples/jobs/mosaic_pipeline.json)
- [samples/jobs/birds_on_trunk_pipeline.json](../../../samples/jobs/birds_on_trunk_pipeline.json) — mosaic.decode → job (titled)
- [samples/jobs/demo_catalog_pipeline_asset_ids.json](../../../samples/jobs/demo_catalog_pipeline_asset_ids.json) — recommended (materialize + overlay_asset)
- [samples/jobs/demo_catalog_pipeline.json](../../../samples/jobs/demo_catalog_pipeline.json)

## See also

- [mosaic.md](mosaic.md) — CharGrid format
- [edit-job.md](edit-job.md) — ImageJob operations
