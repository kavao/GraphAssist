# ImageJob 編集ガイド

[English](../en/image/edit-job.md) · 日本語

ImageJob は、1 枚の画像に対する編集手順を JSON で記述し、`graphassist job` で実行する形式です。  
LLM は ImageJob JSON を生成し、Python 側が Pydantic で検証して Pillow で実行します。

## パス制限

| 種別 | 許可パス |
|------|----------|
| 入力・overlay | `samples/source/` 配下のみ（catalog の PNG mirror 含む） |
| 出力 | `generated/` 配下のみ |

絶対パス、`..` による親参照は拒否されます。

## 最小例

Job ルート: `input` **または** `input_asset`（土台の catalog id）、`output`、`operations`

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
uv run graphassist job samples/jobs/resize_border.json --dry-run
```

問題なければ本番実行します。

```bash
uv run graphassist job samples/jobs/resize_border.json
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
| `composite` | `overlay` **または** `overlay_asset`（カタログ id）、`x`, `y`, `anchor`（`center` で中心锚点） |
| `text` | `content`, `font`, `size`, `color`, `x`, `y`, `stroke_color`, `stroke_width` |
| `trim` | `background`, `padding`, `tolerance` |
| `flatten` | `background` |
| `adjust` | `brightness`, `contrast`, `saturation`（各 0..3、1.0 = 変更なし） |
| `grayscale` | `mode`: `luminance`（Rec.601、**analyze と同系**） |
| `sepia` | `strength`（0..1、1.0 = フルセピア） |
| `curve` | `mode`: `gamma`（`gamma` 0.1..5）または `levels`（`black`, `white`） |
| `quantize` | `colors`（2..256）, `dither`（bool） |
| `posterize` | `bits`（1..8） |
| `blur` | `kind`: `gaussian` / `box`, `radius`（0..50） |
| `sharpen` | `kind`: `enhance`（`amount`）または `unsharp`（`radius`, `percent`, `threshold`） |
| `to_mosaic` | `grid`（`WxH` または `[w,h]`）, `max_colors`, `mosaic_output`（**末尾のみ**） |

`fill` / `color` / `background`: 名前または `#RRGGBB`（`transparent`, `white`, `black`, `red`, `green`, `blue`, `gray`）

## トーン調整例（adjust / curve / quantize）

```json
{
  "version": "1.0",
  "input": "samples/source/job_test_base.png",
  "output": "generated/images/tone_pipeline_out.png",
  "operations": [
    {"type": "adjust", "brightness": 1.15, "contrast": 1.05},
    {"type": "curve", "mode": "gamma", "gamma": 1.1},
    {"type": "quantize", "colors": 16, "dither": false}
  ]
}
```

実行前後の明るさ確認には [analyze](operations.md#analyze) の `--compare` を使います。サンプル: `samples/jobs/adjust_brighten.json`, `samples/jobs/tone_pipeline.json`

## 合成例

パス指定（従来）:

```json
{
  "type": "composite",
  "overlay": "samples/source/badge.png",
  "x": 24,
  "y": 24,
  "anchor": "top_left"
}
```

カタログ id 指定（materialize 済み、または実行時に自動 fetch）:

```json
{
  "type": "composite",
  "overlay_asset": "ornament-fleur-de-lis-simple",
  "x": 24,
  "y": 24
}
```

id は `.rulesync/metadata/asset-catalog.jsonc` のホワイトリストのみ。一覧: `samples/jobs/catalog/index.json`

## 土台の catalog id（input_asset）

```json
{
  "version": "1.0",
  "input_asset": "ui-panel-dark",
  "output": "generated/images/card.png",
  "operations": []
}
```

`input` と `input_asset` は **どちらか一方**。materialize 後に `samples/source/catalog/ui-panel-dark.png` として解決されます。

## anchor: center

`x`, `y` を overlay の中心锚点として扱います。

```json
{
  "type": "composite",
  "overlay_asset": "ornament-fleur-de-lis-simple",
  "x": 200,
  "y": 300,
  "anchor": "center"
}
```

例: `samples/jobs/demo_catalog_anchor_center.json`

## CharGrid 作品への text 重ね

ピクセル絵（MosaicArt）に日本語タイトル等を載せるときは、**CharGrid 行への直接埋め込みではなく Batch で `mosaic.decode` → `job`（`text`）** を使います。

```bash
uv run graphassist run samples/jobs/birds_on_trunk_pipeline.json
```

試行スクリプトは [_workingspace/_scratch/](../../../_workingspace/_scratch/README.md) に置き、正本は Batch manifest へ昇格します（[workspace-scratch スキル](../../../.rulesync/skills/workspace-scratch/SKILL.md)）。

## 禁止事項（LLM 向け）

- ImageMagick / 生シェルコマンドの生成・実行
- 許可外パスへの読み書き
- 未定義の operation type

## 関連

- [batch.md](batch.md) — mosaic と job を 1 JSON にまとめる Batch manifest
- [mosaic.md](mosaic.md) — CharGrid（ピクセルアート）
