# convert ガイド

[English](../en/image/convert.md) · 日本語

ディレクトリまたは単一ファイルの一括変換。

```bash
uv run graphassist convert samples/source/ generated/images/batch \
  --long-edge 1024 --format webp
```

## 主なオプション

| オプション | 説明 |
|------------|------|
| `--format` | `png` / `jpeg` / `webp` |
| `--long-edge N` | 長辺を N にリサイズ |
| `--width` / `--height` | 固定サイズ |
| `--square` | 正方形キャンバス |
| `--square-fill` | `transparent` / `white` / `black` |
| `--quality` | JPEG/WebP 品質 |
| `--dpi` | 出力 DPI |
| `--strip-exif` | JPEG EXIF 削除 |
| `--numbered` | 連番ファイル名 |
| `--brightness` | 明るさ係数（0..3） |
| `--contrast` | コントラスト係数（0..3） |
| `--saturation` | 彩度係数（0..3） |
| `--gamma` | ガンマ補正（0.1..5） |
| `--quantize N` | 色数を N に減色（2..256） |
| `--blur R` | ガウシアンぼかし半径（0..50） |
| `--grayscale` | Rec.601 輝度グレースケール |
| `--sepia S` | セピア調（強度 0..1） |

トーン系フラグはリサイズ（`--long-edge` 等）の**後**に適用されます。順序: adjust → curve → grayscale → sepia → quantize → blur。

```bash
uv run graphassist convert samples/source/ generated/images/out \
  --long-edge 1024 --format webp --brightness 1.1 --gamma 1.05
```

## 参照

- [operations.md](operations.md)
- [quickstart.md](../quickstart.md)
