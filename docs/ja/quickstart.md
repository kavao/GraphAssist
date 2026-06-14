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

## 一括変換（convert）

PNG を WebP に変換し、長辺を 1024px に揃えます。

```bash
uv run python tools/graphassist/graphassist.py convert samples/source/your.png generated/images/out --long-edge 1024 --format webp
```

成功時、`generated/images/out.webp` が作成されます。

## 編集ジョブ（job）

ImageJob JSON でリサイズと枠線を適用します。まず dry-run で確認します。

```bash
uv run python tools/graphassist/graphassist.py job samples/jobs/resize_border.json --dry-run
uv run python tools/graphassist/graphassist.py job samples/jobs/resize_border.json
```

詳細は [edit-job.md](image/edit-job.md) を参照してください。
