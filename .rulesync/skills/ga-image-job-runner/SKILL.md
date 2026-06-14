---
name: ga-image-job-runner
description: ImageJob JSON を生成・dry-run・実行する。LLM は Pillow コマンドや ImageMagick を直接出さない
---

# Image Job Runner

## 目的

自然言語の画像編集指示を **ImageJob JSON** に変換し、`graphassist job` で Pillow 実行する。

## 手順

1. ユーザーの指示から operations を抽出する。
2. **ImageMagick や生シェルは生成しない。**
3. `version`, `input`（または `input_asset`）, `output`, `operations` を持つ JSON を書く。
   - 入力: `samples/source/` 配下、または catalog `input_asset`
   - 出力: `generated/` 配下
   - **カタログ素材** → [ga-catalog-assets スキル](../ga-catalog-assets/SKILL.md)
4. JSON をファイルに保存する（例: `samples/jobs/task.json`）。
   - **1 枚への編集のみ** → 下記 ImageJob 形式
   - **mosaic と job の混在など複数ステップ** → [ga-batch-runner スキル](../ga-batch-runner/SKILL.md) の `commands` 形式
   - 試行スクリプト → [_workingspace/_scratch/](../../_workingspace/_scratch/README.md)（[workspace-scratch スキル](../workspace-scratch/SKILL.md)）
5. dry-run で確認する。

```bash
uv run graphassist job samples/jobs/task.json --dry-run
```

6. 問題なければ本番実行する。

```bash
uv run graphassist job samples/jobs/task.json
```

7. `generated/logs/` のログを確認する。
8. 査証ログに追記する（dna_kernel）。

## JSON 例

```json
{
  "version": "1.0",
  "input": "samples/source/sample.png",
  "output": "generated/images/sample_out.png",
  "operations": [
    {"type": "resize", "width": 1024},
    {"type": "border", "size": 20, "color": "white"}
  ]
}
```

## 禁止事項

- `magick`, `convert`（ImageMagick）, `rm`, `curl`, 任意シェルの生成
- 絶対パス、`..` パス
- 許可外 operation type

## カタログ素材（composite.overlay）

→ [ga-catalog-assets スキル](../ga-catalog-assets/SKILL.md)（正本）

1. `samples/jobs/catalog/index.json` から id を確認
2. materialize: Batch `assets.materialize` または `uv run graphassist assets fetch`
3. Job で **`overlay_asset`** / **`input_asset`**（推奨）または path 指定

```json
{"type": "composite", "overlay_asset": "ornament-fleur-de-lis-simple", "x": 16, "y": 8}
```

**新規 URL / id の追加は LLM 禁止** — manifest は人間が更新。

## トーン調整 operations（Phase T）

明るさ・減色・ぼかし等は ImageJob `operations` に載せる。一括フォルダ変換は [ga-image-processing スキル](../ga-image-processing/SKILL.md) の `convert --brightness` 等。

| type | 用途 |
|------|------|
| `adjust` | brightness / contrast / saturation |
| `curve` | gamma または levels |
| `quantize` | 色数削減 |
| `posterize` | 階調削減 |
| `grayscale` | Rec.601 輝度（`analyze` と同系） |
| `sepia` | strength 0..1 |
| `blur` | gaussian / box |
| `sharpen` | enhance / unsharp |
| `to_mosaic` | ラスタ → MosaicArt JSON（**末尾のみ**）→ [ga-mosaic-art スキル](../ga-mosaic-art/SKILL.md) |

before/after 確認 → [ga-image-analysis スキル](../ga-image-analysis/SKILL.md) の `analyze --compare`

サンプル: `samples/jobs/adjust_brighten.json`, `samples/jobs/tone_pipeline.json`

複数ステップは [ga-batch-runner スキル](../ga-batch-runner/SKILL.md) を使う。

## 参照

- [docs/ja/image/edit-job.md](../../docs/ja/image/edit-job.md)（編集正本）
- [samples/jobs/README.md](../../samples/jobs/README.md) — Demo 一覧
- [samples/jobs/resize_border.json](../../samples/jobs/resize_border.json)
