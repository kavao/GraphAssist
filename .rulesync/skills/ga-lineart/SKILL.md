---
name: ga-lineart
description: LineArt JSON を生成・検証し、graphassist lineart render / validate / Batch lineart.render で SVG・PNG・検証レポートを扱う
---

# LineArt

## 目的

LLM が **LineArt JSON** を生成し、Python CLI が検証して SVG / PNG にレンダリングする。
SVG 全文を LLM が手書きせず、shape / layer / metadata / gradient / group などの構造化 JSON を正本にする。

## いつ使うか

| 状況 | 使うコマンド |
|------|--------------|
| LineArt JSON 1 件を SVG にする | `graphassist lineart render` |
| SVG と PNG を同時に作る | `graphassist lineart render --png` |
| metadata 参照と geometry 正規化を検証する | `graphassist lineart validate --report` |
| LineArt PNG を ImageJob で後処理する | `graphassist run` の `lineart.render` → `job` |
| 複数種類の処理を混ぜる | [ga-batch-runner](../ga-batch-runner/SKILL.md) |

## 手順

1. ユーザーの指示から、図形、レイヤー、色、線、メタデータを抽出する。
2. **SVG 全文や任意シェルは生成しない。**
3. `version`, `canvas`, `definitions`, `layers` を持つ LineArt JSON を書く。
4. JSON を保存する。
   - サンプル・正本: `samples/lineart/*.json`
   - 生成途中: `generated/lineart/*.json`
5. dry-run で検証する。

```bash
uv run graphassist lineart render samples/lineart/icon_minimal.json generated/vector/icon_minimal.svg --dry-run
```

6. metadata 参照と geometry 正規化を検証する。

```bash
uv run graphassist lineart validate samples/lineart/icon_minimal.json --report generated/logs/icon_minimal_validation.json --dry-run
uv run graphassist lineart validate samples/lineart/icon_minimal.json --report generated/logs/icon_minimal_validation.json
```

7. 問題なければ SVG を生成する。

```bash
uv run graphassist lineart render samples/lineart/icon_minimal.json generated/vector/icon_minimal.svg
```

8. PNG が必要な場合は `--png` を指定する。

```bash
uv run graphassist lineart render samples/lineart/icon_minimal.json generated/vector/icon_minimal.svg --png generated/images/icon_minimal.png --png-width 512
```

9. 複数ステップでは Batch manifest を使う。

```bash
uv run graphassist run samples/jobs/lineart_icon_pipeline.json --dry-run
uv run graphassist run samples/jobs/lineart_icon_pipeline.json
```

10. `generated/vector/`, `generated/images/`, `generated/logs/` を確認し、査証ログに追記する。

## LineArt JSON の最小構造

```json
{
  "version": "1.0",
  "canvas": {
    "width": 128,
    "height": 128,
    "background": "transparent"
  },
  "definitions": {
    "gradients": {},
    "clip_paths": {}
  },
  "layers": [
    {
      "id": "main_layer",
      "shapes": [
        {
          "id": "panel_01",
          "type": "rect",
          "x": 20,
          "y": 20,
          "width": 88,
          "height": 88,
          "fill": {"type": "solid", "color": "#f6f8fa"},
          "stroke": {"color": "#1f2328", "width": 3}
        }
      ]
    }
  ]
}
```

## shape type

| type | 用途 |
|------|------|
| `rect` | 矩形・角丸矩形 |
| `ellipse` | 円・楕円 |
| `polygon` | 多角形 |
| `star` | 星形 |
| `path` | M/L/Q/C/Z の明示パス |
| `smooth_path` | 点列から Catmull-Rom 曲線へ変換 |
| `group` | 子 shape をまとめて transform / clip / opacity |

## style / metadata

- `fill`: `"none"`、`{"type":"solid","color":"#RRGGBB"}`、`{"type":"gradient","ref":"id"}`
- `stroke`: `color`, `width`, `join`, `cap`
- `definitions.gradients`: `linear` / `radial`
- `definitions.clip_paths`: clip 用 shape 群
- metadata: `role`, `tags`, `container_id`, `connects_to`, `validation`

metadata は Phase LV の幾何検証と Repair Loop の入力になる。図解・フローチャートでは `role`, `container_id`, `connects_to` をなるべく付ける。

## validate レポート

`lineart validate --report` は Validation Report JSON v0.1 を `generated/logs/` に保存する。
現時点では LV0.1-LV2.4 として metadata 参照整合性、geometry 正規化、線分交差、重なり、包含、接続距離を確認する。レイヤー順は後続 LV2.5 以降で扱う。

```bash
uv run graphassist lineart validate samples/lineart/icon_minimal.json --report generated/logs/icon_minimal_validation.json
```

## Batch 連携

LineArt PNG を ImageJob で後処理するときは `lineart.render` の `png_output` を直後の `job.input` にする。

```json
{
  "version": "1.0",
  "commands": [
    {
      "type": "lineart.render",
      "input": "samples/lineart/icon_minimal.json",
      "output": "generated/vector/lineart_icon.svg",
      "png_output": "generated/images/lineart_icon_base.png",
      "png_width": 128
    },
    {
      "type": "job",
      "input": "generated/images/lineart_icon_base.png",
      "output": "generated/images/lineart_icon.png",
      "operations": [
        {"type": "extend", "left": 8, "right": 8, "top": 8, "bottom": 8, "fill": "transparent"}
      ]
    }
  ]
}
```

## パス制限

| 種別 | 許可パス |
|------|----------|
| LineArt JSON 入力 | `samples/lineart/`, `generated/lineart/` |
| SVG 出力 | `generated/vector/` |
| PNG 出力 | `generated/images/` |
| 検証レポート | `generated/logs/` |
| Batch manifest | `samples/jobs/` |

## 禁止事項

- SVG 全文を LLM が直接生成して正本扱いする
- ImageMagick、任意シェル、外部エディタ操作を生成する
- 絶対パス、`..` パス、許可外ディレクトリへの出力
- `generated/` の中間 PNG を `samples/source/` にコピーして正本化する
- LineArt JSON をチャットに貼っただけで完了扱いする

## 参照

- [docs/ja/image/lineart.md](../../docs/ja/image/lineart.md)（編集正本）
- [docs/en/image/lineart.md](../../docs/en/image/lineart.md)
- [docs/ja/image/lineart-metadata.md](../../docs/ja/image/lineart-metadata.md)
- [docs/ja/image/lineart-validation.md](../../docs/ja/image/lineart-validation.md)
- [docs/ja/image/batch.md](../../docs/ja/image/batch.md)
- [samples/lineart/icon_minimal.json](../../samples/lineart/icon_minimal.json)
- [samples/jobs/lineart_icon_pipeline.json](../../samples/jobs/lineart_icon_pipeline.json)
