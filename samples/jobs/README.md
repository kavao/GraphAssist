# ImageJob / Batch サンプル一覧

`graphassist job` または `graphassist run` で実行します。  
カタログ素材を使う Job は **事前 materialize 推奨**（`uv run graphassist assets fetch`）。  
`overlay_asset` のみの Job は未 fetch 時に実行時自動取得します。

## カタログ（Phase S）

| ファイル | コマンド | 目的 | 出力 |
|----------|----------|------|------|
| [demo_catalog_minimal.json](demo_catalog_minimal.json) | `job` | 最小: `overlay_asset` 1 点 | `generated/images/demo_catalog_minimal.png` |
| [demo_catalog_auto_fetch.json](demo_catalog_auto_fetch.json) | `job` | materialize なし・id 2 点（実行時 fetch） | `generated/images/demo_catalog_auto_fetch.png` |
| [demo_catalog_ornament.json](demo_catalog_ornament.json) | `job` | v1: `overlay` **パス** 3 点 + 縦書き | `generated/images/demo_catalog_ornament.png` |
| [demo_catalog_asset_ids.json](demo_catalog_asset_ids.json) | `job` | S6: `overlay_asset` 3 点 + 縦書き | `generated/images/demo_catalog_asset_ids.png` |
| [demo_catalog_pipeline.json](demo_catalog_pipeline.json) | `run` | Batch materialize → パス composite | `generated/images/demo_catalog_pipeline.png` |
| [demo_catalog_pipeline_asset_ids.json](demo_catalog_pipeline_asset_ids.json) | `run` | **推奨**: materialize → `overlay_asset` | `generated/images/demo_catalog_pipeline_asset_ids.png` |

| Batch 推奨 | `demo_catalog_pipeline_asset_ids.json` |
| カタログ土台 + 装飾 | `demo_catalog_panel_card.json` |
| 土台 `input_asset` | `demo_catalog_panel_input_asset.json` |
| `anchor: center` | `demo_catalog_anchor_center.json` |

### 素材 1 点ずつ（id と見た目の対応）

| ファイル | overlay_asset |
|----------|---------------|
| [demo_catalog_asset_fleur_simple.json](demo_catalog_asset_fleur_simple.json) | `ornament-fleur-de-lis-simple` |
| [demo_catalog_asset_fleur_outline.json](demo_catalog_asset_fleur_outline.json) | `ornament-fleur-de-lis-outline` |
| [demo_catalog_asset_laurel.json](demo_catalog_asset_laurel.json) | `ornament-laurel-wreath-icooon` |

索引: [catalog/index.json](catalog/index.json) · manifest: `.rulesync/metadata/asset-catalog.jsonc` · スキル: [ga-catalog-assets](../../.rulesync/skills/ga-catalog-assets/SKILL.md)

将来 Demo（Phase A）: [_future/README.md](_future/README.md)

## テンプレ土台 + テキスト

| ファイル | 出力 |
|----------|------|
| [demo_zangyo_extend.json](demo_zangyo_extend.json) | `generated/images/demo_zangyo_extend.png` |

土台 PNG: `samples/source/demo_text_base.png`（[gen_demo_text_base.py](../../scripts/gen_demo_text_base.py) で再生成可）

## Mosaic + Job（CharGrid + タイトル）

| ファイル | コマンド | 出力 |
|----------|----------|------|
| [birds_on_trunk_pipeline.json](birds_on_trunk_pipeline.json) | `run` | `generated/images/birds_on_trunk.png` |

```bash
uv run graphassist run samples/jobs/birds_on_trunk_pipeline.json
```

- Mosaic 正本（合成）: [samples/mosaic/birds_on_trunk.json](../mosaic/birds_on_trunk.json)
- 部品（単体 decode）: [parakeet.json](../mosaic/parakeet.json) · [parrot.json](../mosaic/parrot.json)
- 中間 PNG は pipeline 内で `generated/` に出力（`samples/source/` へ置かない）

## LineArt + Job（ベクター → PNG → 後処理）

| ファイル | コマンド | 出力 |
|----------|----------|------|
| [lineart_icon_pipeline.json](lineart_icon_pipeline.json) | `run` | `generated/images/lineart_icon_pipeline.png` |
| [lineart_repair_loop_validate.json](lineart_repair_loop_validate.json) | `run` | `generated/logs/lineart_repair_loop_validation.json` |
| [title_logo_neon_forge_pipeline.json](title_logo_neon_forge_pipeline.json) | `run` | `generated/images/title_logo_neon_forge.png` |
| [neon_yoroshiku_medicine_pipeline.json](neon_yoroshiku_medicine_pipeline.json) | `run` | `generated/images/neon_yoroshiku_medicine.png` |

```bash
uv run graphassist run samples/jobs/lineart_icon_pipeline.json
uv run graphassist run samples/jobs/lineart_repair_loop_validate.json
uv run graphassist run samples/jobs/title_logo_neon_forge_pipeline.json
uv run graphassist run samples/jobs/neon_yoroshiku_medicine_pipeline.json
```

- LineArt 正本: [samples/lineart/icon_minimal.json](../lineart/icon_minimal.json)
- 修正ループ fixture: [samples/lineart/repair_loop_issues.json](../lineart/repair_loop_issues.json)
- タイトルロゴ正本: [samples/lineart/title_logo_neon_forge.json](../lineart/title_logo_neon_forge.json)
- 日本語ネオン正本: [samples/lineart/neon_yoroshiku_medicine.json](../lineart/neon_yoroshiku_medicine.json)
- 中間 SVG: `generated/vector/lineart_icon_pipeline.svg`
- 中間 PNG: `generated/images/lineart_icon_pipeline_base.png`

## その他

| ファイル | コマンド | 用途 |
|----------|----------|------|
| [resize_border.json](resize_border.json) | `job` | resize + border |
| [text_sample.json](text_sample.json) | `job` | 横書き text |
| [temp_align.json](temp_align.json) | `job` | crop / extend 整列 |
| [temp_align_webp.json](temp_align_webp.json) | `job` | WebP 出力 |
| [mosaic_pipeline.json](mosaic_pipeline.json) | `run` | mosaic + job 混在 Batch |

## 一括実行（カタログ Demo）

```powershell
uv run graphassist assets fetch
uv run graphassist job samples/jobs/demo_catalog_minimal.json
uv run graphassist job samples/jobs/demo_catalog_auto_fetch.json
uv run graphassist job samples/jobs/demo_catalog_ornament.json
uv run graphassist job samples/jobs/demo_catalog_asset_ids.json
uv run graphassist run samples/jobs/demo_catalog_pipeline.json
uv run graphassist run samples/jobs/demo_catalog_pipeline_asset_ids.json
uv run graphassist run samples/jobs/demo_catalog_panel_card.json
uv run graphassist job samples/jobs/demo_catalog_asset_fleur_simple.json
uv run graphassist job samples/jobs/demo_catalog_asset_fleur_outline.json
uv run graphassist job samples/jobs/demo_catalog_asset_laurel.json
uv run graphassist job samples/jobs/demo_catalog_panel_input_asset.json
uv run graphassist job samples/jobs/demo_catalog_anchor_center.json
```
