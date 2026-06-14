# クイックスタート

[English](../en/quickstart.md) · 日本語

GraphAssist は Pillow ベースの画像 CLI です。プロジェクトルートから実行します。

## セットアップ

```bash
pip install -r requirements.txt
```

または:

```bash
uv sync
```

## ランタイム（任意・推奨）

バイナリ・フォントは Git 外の `runtime/` に置きます。

```powershell
.\scripts\setup-runtime.ps1
```

[setup/runtime.md](setup/runtime.md)

## 一括変換（convert）

PNG を WebP に変換し、長辺を 1024px に揃えます。

```bash
uv run graphassist convert samples/source/your.png generated/images/out --long-edge 1024 --format webp
```

成功時、`generated/images/out.webp` が作成されます。

## 編集ジョブ（job）

ImageJob JSON でリサイズと枠線を適用します。まず dry-run で確認します。

```bash
uv run graphassist job samples/jobs/resize_border.json --dry-run
uv run graphassist job samples/jobs/resize_border.json
```

詳細は [edit-job.md](image/edit-job.md) を参照してください。

## カタログ素材（composite）

権利フリー装飾・UI パネルは manifest から fetch し、Job で `overlay_asset` に id を指定します。

```powershell
uv run graphassist assets fetch
uv run graphassist job samples/jobs/demo_catalog_minimal.json
uv run graphassist run samples/jobs/demo_catalog_pipeline_asset_ids.json
```

一覧: [samples/jobs/README.md](../../samples/jobs/README.md) · 索引: [samples/jobs/catalog/index.json](../../samples/jobs/catalog/index.json) · スキル: [catalog-assets](../../.rulesync/skills/catalog-assets/SKILL.md)
