---
name: ga-image-processing
description: graphassist convert による一括変換・リサイズ・形式変換
---

# Image Processing（一括 CLI）

## 目的

ディレクトリまたは単一ファイルの **一括 convert** を `graphassist convert` で実行する。

GraphAssist のコンセプトは **繰り返しの、創造性のない画像作業をツールに任せる** こと。同じ変換を毎回手で行うより、CLI 引数や Batch manifest にパイプラインを残して再実行する。

## 実行コマンドの優先順位

1. `$env:GRAPHASSIST_BIN` / `GRAPHASSIST_BIN`
2. `runtime/bin/graphassist.exe`（存在する場合）
3. 開発: `uv run graphassist`

初回・更新: `scripts/setup-runtime.ps1`（[runtime ガイド](../../docs/ja/setup/runtime.md)）

## 手順

1. 入力パス（ファイルまたはディレクトリ）と出力先を決める。
2. 必要なオプション（`--long-edge`, `--format`, `--brightness`, `--grayscale`, `--sepia` 等）を付けて実行する。

```bash
uv run graphassist convert samples/source/ generated/images/batch --long-edge 1024 --format webp
uv run graphassist convert samples/source/icon.png generated/images/icon --brightness 1.15 --gamma 1.05
```

3. 出力ファイルの存在とサイズを確認する。
4. 査証ログに追記する。

## 単一ファイル例

```bash
uv run graphassist convert samples/source/icon.png generated/images/icon --long-edge 512 --format png --square --square-fill transparent
```

## レタッチ（1 枚編集）の場合

一括 convert ではなく **ImageJob** を使う → [ga-image-job-runner スキル](../ga-image-job-runner/SKILL.md)

## ユーティリティ CLI

| コマンド | 用途 |
|----------|------|
| `trim` | 余白除去 |
| `diff` | 差分確認 |
| `inspect` | メタデータ検査 |
| `contact-sheet` / `sheet-pack` / `sheet-split` | スプライトシート |
| `palette` | 色抽出 |

詳細: [operations.md](../../docs/ja/image/operations.md)

## 複数ステップ（mosaic + job 混在）

**Batch manifest** → [ga-batch-runner スキル](../ga-batch-runner/SKILL.md)

## CharGrid（ピクセルアート）

→ [ga-mosaic-art スキル](../ga-mosaic-art/SKILL.md)

## 参照

- [docs/ja/quickstart.md](../../docs/ja/quickstart.md)
- [docs/en/quickstart.md](../../docs/en/quickstart.md)
