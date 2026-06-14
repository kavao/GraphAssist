# CharGrid（MosaicArt）ガイド

[English](../en/image/mosaic.md) · 日本語

**MosaicArt JSON** は、1 文字 = 1 セルのピクセルアートを LLM が生成しやすい中間形式です。  
`graphassist mosaic` で **JSON ↔ 画像** の相互変換と **JS スニペット** のエクスポートができます。

## パス制限

| 種別 | 許可パス |
|------|----------|
| encode 入力 | `samples/source/` |
| MosaicArt JSON（decode / export 入力） | `samples/mosaic/`, `generated/mosaic/` |
| encode 出力 JSON | `generated/mosaic/` |
| decode 出力画像 | `generated/` |

## MosaicArt JSON（v1.0）

```json
{
  "version": "1.0",
  "width": 8,
  "height": 10,
  "transparent": ".",
  "palette": {
    "B": "#d7c6eb",
    "W": "#65d8ff",
    "F": "#ffae42",
    "R": "#ff5f4d"
  },
  "rows": ["...BB...", "..BBBB.."]
}
```

- 各行の長さは `width` と一致
- `rows` の行数は `height` と一致
- `palette` は最大 32 色（デフォルト 16 色運用を推奨）
- `transparent` 文字はパレットキーに使えない

## decode（JSON → 画像）

```bash
uv run python tools/graphassist/graphassist.py mosaic decode \
  samples/mosaic/finale_rocket.json \
  generated/images/finale_rocket.png \
  --cell-size 8
```

`--cell-size` はプレビュー倍率です。1 なら 1 セル = 1 ピクセルです。

## encode（画像 → JSON）

```bash
uv run python tools/graphassist/graphassist.py mosaic encode \
  samples/source/icon.png \
  generated/mosaic/icon.json \
  --grid 32x32 \
  --max-colors 16
```

nearest-neighbor 縮小 + 量子化のため **ロスあり** です。ラウンドトリップ完全一致は期待しないでください。

## export（JS スニペット）

```bash
uv run python tools/graphassist/graphassist.py mosaic export \
  samples/mosaic/finale_rocket.json \
  --format js \
  --name FINALE_ROCKET
```

チャット向けに `const FINALE_ROCKET = [...]` 形式を stdout に出力します。

## サンプル

- [samples/mosaic/finale_rocket.json](../../../samples/mosaic/finale_rocket.json) — ロケット 8×10

## 参照

- [edit-job.md](edit-job.md) — ImageJob による 1 枚編集
- [batch.md](batch.md) — 1 JSON に複数命令（Batch manifest）
- [quickstart.md](../quickstart.md)
