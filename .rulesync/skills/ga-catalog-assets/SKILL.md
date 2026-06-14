---
name: ga-catalog-assets
description: 権利フリー素材カタログの fetch・materialize と ImageJob/Batch での overlay_asset / input_asset 参照
---

# Catalog Assets

## 目的

`.rulesync/metadata/asset-catalog.jsonc` に登録された素材を取得し、ImageJob / Batch で **id 参照** してレイアウトする。

LLM は **既存 catalog id のみ** 使う。新規 URL 追加・manifest 編集は人間が行う。

## いつ使うか

| 状況 | 使うもの |
|------|----------|
| 装飾・アイコンを載せる | `composite.overlay_asset` |
| カタログ PNG を土台にする | `input_asset` |
| fetch から Job まで 1 JSON | Batch `assets.materialize` → `job` |
| 索引・タグ確認 | `samples/jobs/catalog/index.json` |

## 手順

1. 索引を読む: `samples/jobs/catalog/index.json`
2. 必要なら materialize:

```bash
uv run graphassist assets fetch
uv run graphassist assets fetch --id ui-panel-dark
uv run graphassist assets list --format json
```

3. ImageJob を書く（**id は manifest ホワイトリストのみ**）

```json
{
  "version": "1.0",
  "input_asset": "ui-panel-dark",
  "output": "generated/images/card.png",
  "operations": [
    {
      "type": "composite",
      "overlay_asset": "ornament-fleur-de-lis-simple",
      "x": 200,
      "y": 280,
      "anchor": "center"
    }
  ]
}
```

4. または Batch（推奨パターン）:

```bash
uv run graphassist run samples/jobs/demo_catalog_pipeline_asset_ids.json --dry-run
uv run graphassist run samples/jobs/demo_catalog_pipeline_asset_ids.json
```

5. 出力確認: `generated/images/` · ログ: `generated/logs/`

## 参照方式

| フィールド | 説明 |
|------------|------|
| `input` / `overlay` | materialize 後の **PNG パス**（`samples/source/...`） |
| `input_asset` / `overlay_asset` | **catalog id**（未 fetch 時は実行時 auto materialize） |

`overlay` と `overlay_asset` は **どちらか一方**。`input` と `input_asset` も同様。

## 禁止事項

- manifest に無い id の invent
- 外部 URL の Job 直書き
- `.svg` を overlay/input に指定（PNG mirror のみ）
- 商標ロゴ・再配布不可素材の追加

## Demo 一覧

[samples/jobs/README.md](../../samples/jobs/README.md)

| 用途 | ファイル |
|------|----------|
| 最小 | `demo_catalog_minimal.json` |
| 土台 id | `demo_catalog_panel_input_asset.json` |
| center anchor | `demo_catalog_anchor_center.json` |
| Batch 推奨 | `demo_catalog_pipeline_asset_ids.json` |
| 素材 1 点ずつ | `demo_catalog_asset_*.json` |

## 将来（Phase A）

materialize → job → `analyze` の Batch 例は [samples/jobs/_future/README.md](../../samples/jobs/_future/README.md)

## 参照

- [docs/ja/setup/runtime.md](../../docs/ja/setup/runtime.md)
- [docs/ja/image/edit-job.md](../../docs/ja/image/edit-job.md)
- [docs/ja/image/batch.md](../../docs/ja/image/batch.md)
- [assets/catalog/README.md](../../assets/catalog/README.md)
- [ga-batch-runner スキル](../ga-batch-runner/SKILL.md)
- [ga-image-job-runner スキル](../ga-image-job-runner/SKILL.md)
