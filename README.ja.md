# GraphAssist — 画像処理 CLI

![GraphAssist](image/title.webp)

[English](README.md) · 日本語

**GraphAssist** は、Cursor などの LLM エディタ向けに、**Pillow + NumPy 中心の画像処理 CLI** を提供するプロジェクトです。

## コンセプト

**繰り返しの、創造性のない画像作業はツールに任せる** — リサイズ・形式変換・余白除去・サイズ揃えなど、手順は決まっているが地味でミスしやすい作業を CLI と ImageJob JSON に寄せます。やりたいことは JSON や引数で渡し、検証と実行は Python が担当します。

## セットアップ
### 1. Python 依存

```bash
uv sync
```

### 2. ランタイム（バイナリ・フォント — Git 外）

```powershell
.\scripts\setup-runtime.ps1
```

詳細: [設置・runtime](docs/ja/setup/runtime.md)

## 30秒クイックスタート

```bash
uv run graphassist convert samples/source/your.png generated/images/out --long-edge 1024 --format webp
uv run graphassist job samples/jobs/resize_border.json --dry-run
uv run graphassist mosaic decode samples/mosaic/finale_rocket.json generated/images/rocket.png --cell-size 8
```

`runtime/` と `generated/` は gitignore 対象です。

## ドキュメント

| ガイド | 内容 |
|--------|------|
| [ドキュメント索引](docs/README.md) | 入口 |
| [CLI リファレンス](docs/ja/image/operations.md) | 全サブコマンド |
| [設置・runtime](docs/ja/setup/runtime.md) | バイナリ・フォント・重み |
| [他プロジェクトへの取り込み](docs/ja/setup/adoption.md) | ソース + rulesync 注入（原則パターン B） |
| [ImageJob](docs/ja/image/edit-job.md) | JSON 編集 |
| [CharGrid](docs/ja/image/mosaic.md) | ピクセルアート |

## 開発状況

| Phase | 内容 | 状態 |
|-------|------|------|
| 0–3 | convert, ImageJob, composite | ✅ |
| 4–7 | text, trim, diff, inspect, sheet, palette | ✅ |
| M | CharGrid + Batch | ✅ |
| Post-7 | runtime 設置・`src/` 移行 | 進行中 |

## ライセンス

MIT License（[LICENSE](LICENSE) 参照）
