# Asset catalog index（LLM 向け）

権利フリー装飾素材の **id → path** 索引です。正本は `.rulesync/metadata/asset-catalog.jsonc`。

## 使い方

1. **materialize**: `setup-runtime` / `uv run graphassist assets fetch` / Batch `assets.materialize`
2. Job で **`overlay_asset`** / **`input_asset`**（推奨）または path 指定
3. **新規 URL の追加は LLM 禁止** — manifest は人間が更新

## UI パネル（土台）

| id | 用途 | license |
|----|------|---------|
| `ui-panel-dark` | カード / バッジ土台 400×600（seed 同梱） | CC0 1.0 |

Job の `input` に `samples/source/catalog/ui-panel-dark.png` を指定可能（materialize 後）。

## フラデリス紋（fleur-de-lis）

| id | 用途 | license |
|----|------|---------|
| `ornament-fleur-de-lis-simple` | 中央・汎用（Wikimedia PD、軽量） | Public domain |
| `ornament-fleur-de-lis-outline` | 暗い UI 上の線画・角装飾 | Public domain |

## 月桂冠（laurel wreath）

| id | 用途 | license |
|----|------|---------|
| `ornament-laurel-wreath-icooon` | 受賞・ヘッダー装飾（[icooon-mono](https://icooon-mono.com/15552-%E6%9C%88%E6%A1%82%E5%86%A0%E3%82%A2%E3%82%A4%E3%82%B3%E3%83%B3/)） | ICOON MONO License |

## カタログ Demo 一覧

詳細: [samples/jobs/README.md](../README.md)

| 目的 | Job |
|------|-----|
| 最小（id 1 点） | `demo_catalog_minimal.json` |
| 実行時 fetch | `demo_catalog_auto_fetch.json` |
| パス指定 composite | `demo_catalog_ornament.json` |
| id 指定 composite | `demo_catalog_asset_ids.json` |
| Batch 推奨 | `demo_catalog_pipeline_asset_ids.json` |

## Job 例（materialize 後）

```json
{
  "type": "composite",
  "overlay": "samples/source/catalog/ornament-fleur-de-lis-simple.png",
  "x": 308,
  "y": 80,
  "anchor": "top_left"
}
```

または `overlay_asset: "ornament-fleur-de-lis-simple"`（S6）

`demo_text_base.png` の EVENT 列やヘッダー横に載せる想定。

## 参照

- manifest: `.rulesync/metadata/asset-catalog.jsonc`
- 操作: [docs/ja/image/edit-job.md](../../../docs/ja/image/edit-job.md)
