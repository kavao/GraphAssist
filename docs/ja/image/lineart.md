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

## 入出力パス

| 種類 | 許可パス |
|------|----------|
| 入力 LineArt JSON | `samples/lineart/`, `generated/lineart/` |
| 出力 SVG | `generated/vector/` |

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

## 関連ページ

- shape の `role` や `container_id` は [lineart-metadata.md](lineart-metadata.md) を参照してください。
- 検証レポートと修正ループは [lineart-validation.md](lineart-validation.md) を参照してください。
