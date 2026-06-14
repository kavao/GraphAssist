---
name: ga-batch-runner
description: Batch manifest（1 JSON・複数命令）を生成し graphassist run で順次実行する
---

# Batch Runner

## 目的

**1 つの JSON** に複数の処理を並べ、`graphassist run` で順番に実行する。  
mosaic（CharGrid）と ImageJob（レタッチ）を **同じファイルに混在** できる。

## いつ使うか

| 状況 | 使うコマンド |
|------|--------------|
| 1 枚への連続編集のみ | `graphassist job` → [ga-image-job-runner](../ga-image-job-runner/SKILL.md) |
| CharGrid のみ 1 操作 | `graphassist mosaic` → [ga-mosaic-art](../ga-mosaic-art/SKILL.md) |
| **複数種類・複数ステップ** | **`graphassist run`**（このスキル） |

## 手順

1. ユーザーの指示から必要な命令列を抽出する。
2. `version: "1.0"` と `commands: [...]` を持つ JSON を書く。
3. **`samples/jobs/`** に保存する（例: `samples/jobs/pipeline.json`）。
4. dry-run で確認する。

```bash
uv run graphassist run samples/jobs/pipeline.json --dry-run
```

5. 問題なければ本番実行する。

```bash
uv run graphassist run samples/jobs/pipeline.json
```

6. `generated/logs/` の JSONL を確認する。
7. 査証ログに追記する（dna_kernel）。

## 命令 type 一覧

| type | 概要 |
|------|------|
| `job` | ImageJob 相当（`input`, `output`, `operations`） |
| `mosaic.decode` | CharGrid → 画像。**`input`（JSON パス）か `art`（インライン）のどちらか一方** |
| `mosaic.encode` | 画像 → MosaicArt JSON |
| `mosaic.export` | MosaicArt JSON → JS / JSON テキスト |
| `assets.materialize` | カタログ素材を fetch + mirror（`ids` 省略で全件） |

## Batch 内の `generated/` → job 連鎖

直前 command の **`output` と同一パス** を次の `job.input` に書くと、`generated/` 入力が許可されます（単体 `graphassist job` は `samples/source/` のみ）。

例: [birds_on_trunk_pipeline.json](../../samples/jobs/birds_on_trunk_pipeline.json) — `mosaic.decode` → `job`（タイトル text）

## カタログ + Job パイプライン

カタログ PNG を Job で使う前に materialize する例:

```json
{
  "version": "1.0",
  "commands": [
    {
      "type": "assets.materialize",
      "ids": ["ornament-fleur-de-lis-simple", "ornament-fleur-de-lis-outline"]
    },
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

- カタログ id の一覧: `samples/jobs/catalog/index.json`
- **新規 URL 追加は LLM 禁止** — manifest は人間が更新
- 単体 fetch: `uv run graphassist assets fetch` / `assets materialize`

## JSON 例

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
      "type": "mosaic.export",
      "input": "samples/mosaic/finale_rocket.json",
      "format": "js",
      "output": "generated/mosaic/finale.js",
      "name": "FINALE_ROCKET"
    }
  ]
}
```

## パス制限

| 種別 | 許可パス |
|------|----------|
| Batch ファイル | `samples/jobs/` |
| job / mosaic.encode 入力 | `samples/source/`（catalog materialize 後の `samples/source/catalog/` 含む） |
| mosaic.decode 入力 | `samples/mosaic/`, `generated/mosaic/` |
| mosaic.encode / export 出力 JSON | `generated/mosaic/` |
| 画像出力 | `generated/` |

## 禁止事項

- ImageMagick や任意シェルの生成
- 絶対パス、`..` パス
- `commands` も `operations` も無い JSON を `run` に渡す（単一 ImageJob は `job` を使う）

## 参照

- [docs/ja/image/batch.md](../../docs/ja/image/batch.md)（編集正本）
- [docs/en/image/batch.md](../../docs/en/image/batch.md)
- カタログパイプライン → [ga-catalog-assets スキル](../ga-catalog-assets/SKILL.md)
- [samples/jobs/README.md](../../samples/jobs/README.md) — Demo 一覧
- [samples/jobs/mosaic_pipeline.json](../../samples/jobs/mosaic_pipeline.json)
- [samples/jobs/demo_catalog_pipeline_asset_ids.json](../../samples/jobs/demo_catalog_pipeline_asset_ids.json) — **推奨** Batch
- [samples/jobs/demo_catalog_pipeline.json](../../samples/jobs/demo_catalog_pipeline.json)
- [samples/jobs/demo_catalog_asset_ids.json](../../samples/jobs/demo_catalog_asset_ids.json)
- [samples/jobs/demo_catalog_minimal.json](../../samples/jobs/demo_catalog_minimal.json)
