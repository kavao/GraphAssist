---
name: image-job-runner
description: ImageJob JSON を生成・dry-run・実行する。LLM は Pillow コマンドや ImageMagick を直接出さない
---

# Image Job Runner

## 目的

自然言語の画像編集指示を **ImageJob JSON** に変換し、`graphassist job` で Pillow 実行する。

## 手順

1. ユーザーの指示から operations を抽出する。
2. **ImageMagick や生シェルは生成しない。**
3. `version`, `input`, `output`, `operations` を持つ JSON を書く。
   - 入力: `samples/source/` 配下
   - 出力: `generated/` 配下
4. JSON をファイルに保存する（例: `samples/jobs/task.json`）。
5. dry-run で確認する。

```bash
uv run python tools/graphassist/graphassist.py job samples/jobs/task.json --dry-run
```

6. 問題なければ本番実行する。

```bash
uv run python tools/graphassist/graphassist.py job samples/jobs/task.json
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

## 参照

- [docs/image/edit-job.md](../../docs/ja/image/edit-job.md)（編集正本）
- [samples/jobs/resize_border.json](../../samples/jobs/resize_border.json)
