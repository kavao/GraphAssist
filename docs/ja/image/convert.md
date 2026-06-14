# convert ガイド

[English](../en/image/convert.md) · 日本語

ディレクトリまたは単一ファイルの一括変換。

```bash
uv run python tools/graphassist/graphassist.py convert samples/source/ generated/images/batch \
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

## 参照

- [operations.md](operations.md)
- [quickstart.md](../quickstart.md)
