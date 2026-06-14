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

## Run

```bash
uv run graphassist run samples/jobs/mosaic_pipeline.json --dry-run
uv run graphassist run samples/jobs/mosaic_pipeline.json
```

Logs are written to `generated/logs/` as JSONL.

## Sample

- [samples/jobs/mosaic_pipeline.json](../../../samples/jobs/mosaic_pipeline.json)

## See also

- [mosaic.md](mosaic.md) — CharGrid format
- [edit-job.md](edit-job.md) — ImageJob operations
