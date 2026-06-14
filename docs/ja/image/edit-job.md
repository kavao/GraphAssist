# ImageJob 編集ガイド

[English](../en/image/edit-job.md) · 日本語

ImageJob は、1 枚の画像に対する編集手順を JSON で記述し、`graphassist job` で実行する形式です。  
LLM は ImageJob JSON を生成し、Python 側が Pydantic で検証して Pillow で実行します。

## パス制限

| 種別 | 許可パス |
|------|----------|
| 入力・overlay | `samples/source/` 配下のみ |
| 出力 | `generated/` 配下のみ |

絶対パス、`..` による親参照は拒否されます。

## 最小例

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

## 実行手順

まず dry-run で手順と出力先を確認します。

```bash
uv run python tools/graphassist/graphassist.py job samples/jobs/resize_border.json --dry-run
```

問題なければ本番実行します。

```bash
uv run python tools/graphassist/graphassist.py job samples/jobs/resize_border.json
```

実行後、`generated/logs/` に JSONL / Markdown / replay スクリプトが保存されます。

## operations（v1.0）

| type | 主なフィールド |
|------|----------------|
| `resize` | `width`, `height`, `long_edge`（いずれか） |
| `crop` | `width`, `height`, `x`, `y` |
| `extend` | `left`, `right`, `top`, `bottom`, `fill` |
| `rotate` | `degrees`, `fill` |
| `border` | `size`, `color` |
| `composite` | `overlay`, `x`, `y`, `anchor` |
| `text` | `content`, `font`, `size`, `color`, `x`, `y`, `stroke_color`, `stroke_width` |
| `trim` | `background`, `padding`, `tolerance` |
| `flatten` | `background` |

`fill` / `color` / `background`: 名前または `#RRGGBB`（`transparent`, `white`, `black`, `red`, `green`, `blue`, `gray`）

## 合成例

```json
{
  "type": "composite",
  "overlay": "samples/source/badge.png",
  "x": 24,
  "y": 24,
  "anchor": "top_left"
}
```

## 禁止事項（LLM 向け）

- ImageMagick / 生シェルコマンドの生成・実行
- 許可外パスへの読み書き
- 未定義の operation type

## 関連

- [batch.md](batch.md) — mosaic と job を 1 JSON にまとめる Batch manifest
- [mosaic.md](mosaic.md) — CharGrid（ピクセルアート）
