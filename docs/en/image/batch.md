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
| `lineart.render` | LineArt JSON → SVG, and optionally PNG |
| `assets.materialize` | Fetch and mirror catalog assets (`ids` omitted = all enabled) |
| `analyze` | Image metrics (profile or compare when `compare` is set) |

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

## LineArt To Job

`lineart.render` generates SVG from LineArt JSON. When `png_output` is set, it also writes a PNG, which can be used as the next `job.input`.

```json
{
  "version": "1.0",
  "commands": [
    {
      "type": "lineart.render",
      "input": "samples/lineart/icon_minimal.json",
      "output": "generated/vector/lineart_icon.svg",
      "png_output": "generated/images/lineart_icon_base.png",
      "png_width": 128
    },
    {
      "type": "job",
      "input": "generated/images/lineart_icon_base.png",
      "output": "generated/images/lineart_icon.png",
      "operations": [
        {"type": "extend", "left": 8, "right": 8, "top": 8, "bottom": 8, "fill": "transparent"}
      ]
    }
  ]
}
```

When `png_output` is used as a downstream `job.input`, it must match the previous command output path.

## Previous command output as analyze input

Batch **`analyze`** also supports `generated/` chaining:

| Field | Rule |
|-------|------|
| `input` | When under `generated/`, must **match the previous command’s `output`** |
| `compare` | When under `generated/`, must match **any earlier command output** in the same manifest |
| `output` | Under `generated/` (e.g. `generated/logs/`) |

```json
{
  "version": "1.0",
  "commands": [
    {
      "type": "job",
      "input": "samples/source/job_test_base.png",
      "output": "generated/images/tone_before.png",
      "operations": []
    },
    {
      "type": "job",
      "input": "generated/images/tone_before.png",
      "output": "generated/images/tone_after.png",
      "operations": [{"type": "adjust", "brightness": 1.5}]
    },
    {
      "type": "analyze",
      "input": "generated/images/tone_after.png",
      "compare": "generated/images/tone_before.png",
      "output": "generated/logs/tone_compare.json"
    }
  ]
}
```

For before/after QA after tone ops. Standalone CLI: [operations.md](operations.md#analyze).

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
- [samples/jobs/lineart_icon_pipeline.json](../../../samples/jobs/lineart_icon_pipeline.json) — lineart.render → job
- [samples/jobs/tone_analyze_pipeline.json](../../../samples/jobs/tone_analyze_pipeline.json) — job → adjust → analyze compare
- [samples/jobs/demo_catalog_pipeline_asset_ids.json](../../../samples/jobs/demo_catalog_pipeline_asset_ids.json) — recommended (materialize + overlay_asset)
- [samples/jobs/demo_catalog_pipeline.json](../../../samples/jobs/demo_catalog_pipeline.json)

## See also

- [mosaic.md](mosaic.md) — CharGrid format
- [edit-job.md](edit-job.md) — ImageJob operations
