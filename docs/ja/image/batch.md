# Batch manifest（複数命令）

[English](../en/image/batch.md) · 日本語

**1 つの JSON** に複数の命令を並べ、`graphassist run` で順番に実行します。  
LLM はパイプライン全体を 1 ファイルに書けます。

## 配置

| 種別 | パス |
|------|------|
| Batch manifest | `samples/jobs/` |

単一 ImageJob（`commands` なし）は従来どおり `graphassist job` を使います。

## 形式（v1.0）

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
    },
    {
      "type": "mosaic.encode",
      "input": "samples/source/icon.png",
      "output": "generated/mosaic/icon.json",
      "grid": "16x16",
      "max_colors": 16
    },
    {
      "type": "mosaic.export",
      "input": "samples/mosaic/finale_rocket.json",
      "format": "js",
      "output": "generated/mosaic/finale.js",
      "name": "FINALE_ROCKET"
    }
  ]
}
```

## 命令一覧

| type | 説明 |
|------|------|
| `job` | ImageJob と同じ（`input`, `output`, `operations`） |
| `mosaic.decode` | CharGrid → 画像。`input`（JSON パス）または `art`（インライン）の **どちらか一方** |
| `mosaic.encode` | 画像 → MosaicArt JSON |
| `mosaic.export` | MosaicArt JSON → JS / JSON テキスト |

## 実行

```bash
uv run graphassist run samples/jobs/mosaic_pipeline.json --dry-run
uv run graphassist run samples/jobs/mosaic_pipeline.json
```

ログは `generated/logs/` に JSONL で残ります。

## サンプル

- [samples/jobs/mosaic_pipeline.json](../../../samples/jobs/mosaic_pipeline.json)

## 参照

- [mosaic.md](mosaic.md) — CharGrid 形式
- [edit-job.md](edit-job.md) — ImageJob operations
