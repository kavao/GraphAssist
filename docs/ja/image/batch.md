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
| `lineart.render` | LineArt JSON → SVG、必要に応じて PNG |
| `lineart.validate` | LineArt JSON → Validation Report JSON |
| `assets.materialize` | カタログ素材の fetch + mirror（`ids` 省略で有効な全件） |
| `analyze` | 画像 metrics（profile または `compare` 付き compare） |

## カタログ + Job

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

## 直前 command の output を job input に

Batch 内で **`job.input` が直前の command の `output` と同一パス** のとき、`generated/` 配下を入力として許可します（単体 `graphassist job` は従来どおり `samples/source/` のみ）。

```json
{
  "version": "1.0",
  "commands": [
    {
      "type": "mosaic.decode",
      "input": "samples/mosaic/birds_on_trunk.json",
      "output": "generated/images/birds_on_trunk_base.png",
      "cell_size": 8
    },
    {
      "type": "job",
      "input": "generated/images/birds_on_trunk_base.png",
      "output": "generated/images/birds_on_trunk.png",
      "operations": [
        {"type": "extend", "top": 56, "fill": "black"},
        {"type": "text", "content": "インコとオウム", "font": "assets/fonts/PixelMplus12-Regular.ttf", "size": 20, "color": "white", "x": 130, "y": 10}
      ]
    }
  ]
}
```

`generated/` を job input に書く場合、**必ず直前 command の output と同じパス**にしてください。

## LineArt → Job

`lineart.render` は LineArt JSON から SVG を生成します。`png_output` を指定すると PNG も生成し、その PNG を直後の `job.input` として使えます。
`validate_report` を指定すると、同じ入力に対する Validation Report JSON v0.1 も `generated/logs/` に保存できます。

```json
{
  "version": "1.0",
  "commands": [
    {
      "type": "lineart.render",
      "input": "samples/lineart/icon_minimal.json",
      "output": "generated/vector/lineart_icon.svg",
      "png_output": "generated/images/lineart_icon_base.png",
      "png_width": 128,
      "validate_report": "generated/logs/lineart_icon_validation.json"
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

`png_output` を後段の `job.input` に使う場合も、直前 command の output と同じパスにしてください。

検証だけを Batch に入れる場合は `lineart.validate` を使います。

```json
{
  "version": "1.0",
  "commands": [
    {
      "type": "lineart.validate",
      "input": "samples/lineart/icon_minimal.json",
      "report": "generated/logs/icon_minimal_validation.json"
    }
  ]
}
```

## 直前 command の output を analyze input に

`analyze` も Batch 内で **`generated/` 連鎖** に対応しています。

| フィールド | ルール |
|------------|--------|
| `input` | `generated/` のとき **直前 command の `output` と同一** |
| `compare` | `generated/` のとき **それより前のいずれかの command `output` と一致** |
| `output` | `generated/logs/` 等、`generated/` 配下 |

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

Job / 変換の before/after 検証パイプライン向け。単体 CLI は [operations.md](operations.md#analyze) の `graphassist analyze`。

## 実行

```bash
uv run graphassist run samples/jobs/mosaic_pipeline.json --dry-run
uv run graphassist run samples/jobs/mosaic_pipeline.json
```

ログは `generated/logs/` に JSONL で残ります。

## サンプル

- [samples/jobs/README.md](../../../samples/jobs/README.md) — Demo 一覧
- [samples/jobs/mosaic_pipeline.json](../../../samples/jobs/mosaic_pipeline.json)
- [samples/jobs/birds_on_trunk_pipeline.json](../../../samples/jobs/birds_on_trunk_pipeline.json) — mosaic.decode → job（タイトル付き）
- [samples/jobs/lineart_icon_pipeline.json](../../../samples/jobs/lineart_icon_pipeline.json) — lineart.render → job
- [samples/jobs/lineart_repair_loop_validate.json](../../../samples/jobs/lineart_repair_loop_validate.json) — lineart.validate → Validation Report
- [samples/jobs/tone_analyze_pipeline.json](../../../samples/jobs/tone_analyze_pipeline.json) — job → adjust → analyze compare
- [samples/jobs/demo_catalog_pipeline_asset_ids.json](../../../samples/jobs/demo_catalog_pipeline_asset_ids.json) — 推奨（materialize + overlay_asset）
- [samples/jobs/demo_catalog_pipeline.json](../../../samples/jobs/demo_catalog_pipeline.json)

## 参照

- [mosaic.md](mosaic.md) — CharGrid 形式
- [edit-job.md](edit-job.md) — ImageJob operations
