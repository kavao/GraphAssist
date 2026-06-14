---
name: image-processing
description: graphassist convert による一括変換・リサイズ・形式変換
---

# Image Processing（一括 CLI）

## 目的

ディレクトリまたは単一ファイルの **一括 convert** を `graphassist convert` で実行する。

## 手順

1. 入力パス（ファイルまたはディレクトリ）と出力先を決める。
2. 必要なオプション（`--long-edge`, `--format` 等）を付けて実行する。

```bash
uv run python tools/graphassist/graphassist.py convert samples/source/ generated/images/batch --long-edge 1024 --format webp
```

3. 出力ファイルの存在とサイズを確認する。
4. 査証ログに追記する。

## 単一ファイル例

```bash
uv run python tools/graphassist/graphassist.py convert samples/source/icon.png generated/images/icon --long-edge 512 --format png --square --square-fill transparent
```

## レタッチ（1 枚編集）の場合

一括 convert ではなく **ImageJob** を使う → [image-job-runner スキル](../image-job-runner/SKILL.md)

## 参照

- [docs/ja/quickstart.md](../../docs/ja/quickstart.md)
- [docs/en/quickstart.md](../../docs/en/quickstart.md)
