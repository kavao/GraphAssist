# CLI リファレンス（operations）

[English](../en/image/operations.md) · 日本語

`graphassist` サブコマンド一覧。パス制限の詳細は各ガイドを参照。

## サブコマンド

| コマンド | 用途 |
|----------|------|
| `convert` | 一括リサイズ・形式変換 |
| `job` | ImageJob JSON 実行 |
| `run` | Batch manifest（複数命令） |
| `mosaic` | CharGrid encode / decode / export |
| `trim` | 自動余白除去 |
| `diff` | 2 枚の差分画像 |
| `inspect` | 解像度・モード・破損チェック |
| `contact-sheet` | サムネイル一覧シート |
| `sheet-pack` | 複数 PNG → スプライトシート |
| `sheet-split` | スプライトシート → 複数 PNG |
| `palette` | 支配色抽出 |

## ImageJob operations

| type | 概要 |
|------|------|
| `resize` | 拡大縮小 |
| `crop` | 矩形トリミング |
| `extend` | キャンバス拡張 |
| `rotate` | 回転 |
| `border` | 枠線 |
| `composite` | 画像合成 |
| `text` | フォント描画（`assets/fonts/`） |
| `trim` | 余白除去 |
| `flatten` | 透明を背景色で潰す |

色: 名前（`white` 等）または `#RRGGBB`

## 例

```bash
uv run graphassist trim samples/source/icon.png generated/images/icon_trim.png
uv run graphassist diff before.png after.png generated/images/diff.png
uv run graphassist inspect samples/source/icon.png --format json
uv run graphassist contact-sheet samples/source generated/images/sheet.png --cols 4
uv run graphassist palette samples/source/icon.png --max-colors 8
```

## 参照

- [convert.md](convert.md)
- [edit-job.md](edit-job.md)
- [mosaic.md](mosaic.md)
- [batch.md](batch.md)
