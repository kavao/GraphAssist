# LineArt SVG レンダリング

[English](../../en/image/lineart.md) · 日本語

このガイドでは、LineArt JSON を SVG にレンダリングする最小手順を説明します。LineArt は、LLM が直接 SVG を書かず、構造化 JSON を Python 側で検証・変換して SVG を出力するためのベクター描画形式です。

## このドキュメントを使う場面

LineArt JSON のサンプルを SVG として確認したいときに使います。

最小限の指示文は次のようにできます。

```text
この LineArt JSON を SVG にレンダリングしてください。
```

このように入力すると、アシスタントは `graphassist lineart render` を使い、まず dry-run で入力と出力先を確認してから SVG を生成します。

LineArt 図版そのものを作ってほしい場合は、次の一言で依頼できます。

```text
LineArt で簡単なアイコンを作ってください。
```

このように入力すると、アシスタントは LineArt JSON を `samples/lineart/` または `generated/lineart/` に保存し、dry-run 後に SVG または PNG を生成します。複数ステップが必要な場合は Batch manifest を作り、`lineart.render` から ImageJob へつなぎます。

ユーザーが確認できる主な成果物は次のとおりです。

| 成果物 | 保存先 |
|--------|--------|
| LineArt JSON | `samples/lineart/` または `generated/lineart/` |
| SVG | `generated/vector/` |
| PNG | `generated/images/` |
| Batch manifest | `samples/jobs/` |
| 実行ログ | `generated/logs/` |

## コマンド

サンプル LineArt JSON を検証し、出力先だけ確認します。

```powershell
# 確認（dry-run）— SVG はまだ書き込まない
uv run graphassist lineart render samples/lineart/icon_minimal.json generated/vector/icon_minimal.svg --dry-run
```

問題がなければ SVG を生成します。

```powershell
# 本番実行 — generated/vector/ に SVG を保存する
uv run graphassist lineart render samples/lineart/icon_minimal.json generated/vector/icon_minimal.svg
```

実行後、`generated/vector/icon_minimal.svg` を確認できます。

PNG も同時に生成したい場合は `--png` を指定します。

```powershell
# SVG と PNG を生成 — PNG は generated/images/ に保存する
uv run graphassist lineart render samples/lineart/icon_minimal.json generated/vector/icon_minimal.svg --png generated/images/icon_minimal.png --png-width 512
```

PNG ラスタライズには optional backend の `resvg-py` または `cairosvg` を使います。未導入の場合は `uv sync --extra catalog` で導入できます。

## 入出力パス

| 種類 | 許可パス |
|------|----------|
| 入力 LineArt JSON | `samples/lineart/`, `generated/lineart/` |
| 出力 SVG | `generated/vector/` |
| 出力 PNG | `generated/images/` |

絶対パスと `..` を含む親ディレクトリ参照は使えません。

## 最小 JSON

```json
{
  "version": "1.0",
  "canvas": {
    "width": 128,
    "height": 128,
    "background": "transparent"
  },
  "layers": [
    {
      "id": "main_layer",
      "shapes": [
        {
          "id": "wave_01",
          "type": "smooth_path",
          "role": "annotation",
          "points": [[32, 72], [52, 48], [76, 80], [96, 56]],
          "interpolation": "catmull_rom",
          "closed": false,
          "stroke": {
            "color": "#3a86ff",
            "width": 5,
            "join": "round",
            "cap": "round"
          }
        }
      ]
    }
  ]
}
```

`path` は `M`, `L`, `Q`, `C`, `Z` の命令列を使えます。`smooth_path` は点列を Catmull-Rom 補間で cubic Bezier に変換します。

## グラデーション

グラデーションは `definitions.gradients` に定義し、shape の `fill` から参照します。

```json
{
  "definitions": {
    "gradients": {
      "panel_gradient": {
        "type": "linear",
        "from": [20, 20],
        "to": [108, 108],
        "stops": [
          {"offset": 0, "color": "#ffffff"},
          {"offset": 1, "color": "#dbeafe"}
        ]
      }
    }
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
          "fill": {"type": "gradient", "ref": "panel_gradient"}
        }
      ]
    }
  ]
}
```

`type` は `linear` または `radial` を使えます。`stops[].offset` は `0` から `1` の範囲で、昇順に並べます。

## Group・Transform・Clip

複数の shape をまとめて移動・回転・拡大縮小したい場合は `group` を使います。`clip_path` は `definitions.clip_paths` に定義し、shape または group から参照します。

```json
{
  "definitions": {
    "clip_paths": {
      "badge_clip": {
        "shapes": [
          {"id": "badge_clip_rect", "type": "rect", "x": 70, "y": 78, "width": 28, "height": 24}
        ]
      }
    }
  },
  "layers": [
    {
      "id": "main_layer",
      "shapes": [
        {
          "id": "group_01",
          "type": "group",
          "opacity": 0.85,
          "clip_path": "badge_clip",
          "transform": {
            "translate": [0, 0],
            "rotate": -8,
            "rotate_origin": [84, 90],
            "scale": 1
          },
          "shapes": [
            {"id": "bar_01", "type": "rect", "x": 72, "y": 84, "width": 24, "height": 6}
          ]
        }
      ]
    }
  ]
}
```

`transform` は `translate`、`rotate`、`rotate_origin`、`scale` を指定できます。`opacity` は `0` から `1` の範囲です。

## 関連ページ

- shape の `role` や `container_id` は [lineart-metadata.md](lineart-metadata.md) を参照してください。
- 検証レポートと修正ループは [lineart-validation.md](lineart-validation.md) を参照してください。
