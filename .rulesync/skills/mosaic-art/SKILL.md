---
name: mosaic-art
description: MosaicArt CharGrid JSON の生成・decode・encode・JS エクスポート
---

# Mosaic Art（CharGrid）

## 目的

LLM が **文字グリッド + パレット** でピクセルアートを定義し、`graphassist mosaic` で PNG にレンダリングする。

## LLM が生成する正本

**MosaicArt JSON v1.0**（JS `const` ではなく JSON を正本とする）。

必須フィールド:

- `version`: `"1.0"`
- `width`, `height`: グリッドサイズ
- `transparent`: 通常 `"."`
- `palette`: 1 文字キー → `#RRGGBB`（**16 色以内**を推奨）
- `rows`: 高さと同数の文字列、各文字列長 = `width`

## decode（プレビュー）

```bash
uv run python tools/graphassist/graphassist.py mosaic decode \
  samples/mosaic/finale_rocket.json \
  generated/images/preview.png \
  --cell-size 8
```

## encode（既存画像 → 編集用 JSON）

```bash
uv run python tools/graphassist/graphassist.py mosaic encode \
  samples/source/icon.png \
  generated/mosaic/icon.json \
  --grid 24x24 \
  --max-colors 16
```

## JS エクスポート（チャット向け）

```bash
uv run python tools/graphassist/graphassist.py mosaic export \
  samples/mosaic/finale_rocket.json \
  --format js \
  --name FINALE_ROCKET
```

## 記号設計のヒント

- 略称を使う（`B`=body, `W`=window, `R`=red 等）と LLM が編集しやすい
- 行の長さをすべて揃える（パディングは `transparent` 文字）
- ImageJob レタッチは [image-job-runner スキル](../image-job-runner/SKILL.md)

## 複数命令（Batch manifest）

複数ステップは [batch-runner スキル](../batch-runner/SKILL.md) を使う（詳細は [batch.md](../../docs/ja/image/batch.md)）。

```bash
uv run python tools/graphassist/graphassist.py run samples/jobs/mosaic_pipeline.json --dry-run
```

## 参照

- [docs/ja/image/mosaic.md](../../docs/ja/image/mosaic.md)
- [docs/ja/image/batch.md](../../docs/ja/image/batch.md)
- [docs/en/image/mosaic.md](../../docs/en/image/mosaic.md)
- [docs/en/image/batch.md](../../docs/en/image/batch.md)
- [samples/mosaic/finale_rocket.json](../../samples/mosaic/finale_rocket.json)
- [samples/jobs/mosaic_pipeline.json](../../samples/jobs/mosaic_pipeline.json)
