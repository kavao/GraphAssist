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
uv run graphassist mosaic decode \
  samples/mosaic/finale_rocket.json \
  generated/images/finale_rocket.png \
  --cell-size 8
```

`--cell-size` はプレビュー倍率です。1 なら 1 セル = 1 ピクセルです。

## encode（画像 → JSON）

```bash
uv run graphassist mosaic encode \
  samples/source/icon.png \
  generated/mosaic/icon.json \
  --grid 32x32 \
  --max-colors 16
```

nearest-neighbor 縮小 + 量子化のため **ロスあり** です。ラウンドトリップ完全一致は期待しないでください。

## export（JS スニペット）

```bash
uv run graphassist mosaic export \
  samples/mosaic/finale_rocket.json \
  --format js \
  --name FINALE_ROCKET
```

チャット向けに `const FINALE_ROCKET = [...]` 形式を stdout に出力します。

## サンプル

| JSON | 内容 | decode 例 |
|------|------|-----------|
| [finale_rocket.json](../../../samples/mosaic/finale_rocket.json) | ロケット 8×10 | `uv run graphassist mosaic decode samples/mosaic/finale_rocket.json generated/images/finale_rocket.png --cell-size 8` |
| [parakeet.json](../../../samples/mosaic/parakeet.json) | インコ（単体） | `… parakeet.json generated/images/parakeet.png --cell-size 8` |
| [parrot.json](../../../samples/mosaic/parrot.json) | オウム（単体） | `… parrot.json generated/images/parrot.png --cell-size 8` |
| [birds_on_trunk.json](../../../samples/mosaic/birds_on_trunk.json) | 2 羽 + 幹（合成） | `… birds_on_trunk.json generated/images/birds_on_trunk_base.png --cell-size 8` |

タイトル付き完成 PNG は Batch 正本 [birds_on_trunk_pipeline.json](../../../samples/jobs/birds_on_trunk_pipeline.json) を使います（下記）。

## Mosaic + テキスト

読みやすい日本語タイトルは **CharGrid 行への直接埋め込みではなく ImageJob `text`** で重ねます。  
1 コマンド再現は Batch manifest（`mosaic.decode` → `job`）を正本とします。

```bash
uv run graphassist run samples/jobs/birds_on_trunk_pipeline.json
```

詳細は [batch.md](batch.md) の「直前 command の output を job input に」節を参照してください。

## 参照

- [edit-job.md](edit-job.md) — ImageJob による 1 枚編集
- [batch.md](batch.md) — 1 JSON に複数命令（Batch manifest）
- [quickstart.md](../quickstart.md)
