---
name: ga-mosaic-art
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
uv run graphassist mosaic decode \
  samples/mosaic/finale_rocket.json \
  generated/images/preview.png \
  --cell-size 8
```

## encode（既存画像 → 編集用 JSON）

```bash
uv run graphassist mosaic encode \
  samples/source/icon.png \
  generated/mosaic/icon.json \
  --grid 24x24 \
  --max-colors 16
```

## ImageJob `to_mosaic`（レタッチ後 → CharGrid）

ImageJob の **最終 operation** としてラスタを MosaicArt JSON へ（`mosaic encode` 相当）。

```json
{
  "type": "to_mosaic",
  "grid": "16x16",
  "max_colors": 16,
  "mosaic_output": "generated/mosaic/icon.json"
}
```

- **末尾のみ** — 以降に operation を置かない
- Job `output` は PNG、`mosaic_output` が JSON

サンプル: [to_mosaic_pipeline.json](../../samples/jobs/to_mosaic_pipeline.json) — [ga-image-job-runner スキル](../ga-image-job-runner/SKILL.md)

## JS エクスポート（チャット向け）

```bash
uv run graphassist mosaic export \
  samples/mosaic/finale_rocket.json \
  --format js \
  --name FINALE_ROCKET
```

## 記号設計のヒント

- 略称を使う（`B`=body, `W`=window, `R`=red 等）と LLM が編集しやすい
- 行の長さをすべて揃える（パディングは `transparent` 文字）
- ImageJob レタッチは [ga-image-job-runner スキル](../ga-image-job-runner/SKILL.md)
- 日本語タイトル等の読みやすい文字は **ImageJob `text`** に委譲する（CharGrid 直埋めは非推奨）
- 合成試行は [_workingspace/_scratch/](../../_workingspace/_scratch/README.md) → 正本へ昇格（[workspace-scratch スキル](../workspace-scratch/SKILL.md)）

## Mosaic + Job（タイトル付き）

絵本体は MosaicArt JSON、タイトル・装飾は Batch 内の `job` で重ねる。

```bash
uv run graphassist run samples/jobs/birds_on_trunk_pipeline.json
```

正本: `samples/mosaic/birds_on_trunk.json` + `samples/jobs/birds_on_trunk_pipeline.json`

## 複数 JSON の合成（merge）

2 つ以上の MosaicArt を 1 グリッドに重ねるときは **merge ツール** を使う（手書き blit や scratch Python は避ける）。

```bash
# 汎用: レイヤー PATH@X,Y を順に重ねる
uv run graphassist mosaic merge generated/mosaic/merged.json \
  --canvas 50x26 \
  --layer samples/mosaic/parakeet.json@8,6 \
  --layer samples/mosaic/parrot.json@24,3 \
  --title my_scene

# birds デモ: parakeet + parrot + 幹 preset
uv run graphassist mosaic compose-birds generated/mosaic/birds_on_trunk_merged.json
# または
uv run python scripts/merge_birds_on_trunk.py
```

正本 `samples/mosaic/birds_on_trunk.json` は上記 compose の出力と **おおむね同等**（palette remap 付き）。試行は [_workingspace/_scratch/](../../_workingspace/_scratch/README.md) → 成功後 `samples/mosaic/` または Batch へ昇格。

## 複数命令（Batch manifest）

複数ステップは [ga-batch-runner スキル](../ga-batch-runner/SKILL.md) を使う（詳細は [batch.md](../../docs/ja/image/batch.md)）。

```bash
uv run graphassist run samples/jobs/mosaic_pipeline.json --dry-run
```

## 参照

- [docs/ja/image/mosaic.md](../../docs/ja/image/mosaic.md)
- [docs/ja/image/batch.md](../../docs/ja/image/batch.md)
- [docs/en/image/mosaic.md](../../docs/en/image/mosaic.md)
- [docs/en/image/batch.md](../../docs/en/image/batch.md)
- [samples/mosaic/finale_rocket.json](../../samples/mosaic/finale_rocket.json)
- [samples/jobs/mosaic_pipeline.json](../../samples/jobs/mosaic_pipeline.json)
