# GraphAssist — 画像処理 CLI

[English](README.md) · 日本語

**GraphAssist** は、Cursor などの LLM エディタ向けに、**Pillow + NumPy 中心の画像処理 CLI** を提供するプロジェクトです。

LLM や外部 API に頼らず、**Pillow + NumPy** でコマンドと ImageJob JSON から画像処理を再現します。ImageMagick は使用しません。

運用基盤は [dna_kernel](https://github.com/kavao/dna_kernel)（rulesync、査証ログ、完了規律）です。

## セットアップ

```bash
pip install -r requirements.txt
```

または:

```bash
uv sync
```

## 30秒クイックスタート

一括変換（リサイズ + WebP）:

```bash
uv run python tools/graphassist/graphassist.py convert samples/source/your.png generated/images/out --long-edge 1024 --format webp
```

編集ジョブ（ImageJob JSON）:

```bash
uv run python tools/graphassist/graphassist.py job samples/jobs/resize_border.json --dry-run
uv run python tools/graphassist/graphassist.py job samples/jobs/resize_border.json
```

`generated/` は gitignore 対象です。

## ルール反映（dna_kernel）

ルール正本（`.rulesync/`）を変更したあと:

```bash
corepack pnpm dlx rulesync generate --dry-run
corepack pnpm dlx rulesync generate
uv run python tools/kernel/user_prefs.py sync
```

## 査証ログ追記

```bash
uv run python tools/kernel/workspace_audit_log.py append "作業内容"
```

## ドキュメント

| ガイド | 内容 |
|--------|------|
| [ドキュメント索引](docs/README.md) | 入口（表示は EN 先） |
| [クイックスタート](docs/ja/quickstart.md) | セットアップ（編集正本） |
| [ImageJob 編集](docs/ja/image/edit-job.md) | JSON 編集（編集正本） |
| [Quickstart (EN)](docs/en/quickstart.md) | English quickstart |
| [ImageJob (EN)](docs/en/image/edit-job.md) | English ImageJob guide |
| [dna_kernel 詳細](docs/ja/dna-kernel/README.md) | ガバナンス（編集正本） |
| [作業計画](_workingspace/plans/work-plan.md) | フェーズ別計画 |

ユーザー向け docs は **`docs/ja/` を編集正本**とし、同内容を `docs/en/` に同期します。`.rulesync/rules/docs-writing.md` §0 を参照。

## 開発状況

| Phase | 内容 | 状態 |
|-------|------|------|
| 0 | dna_kernel 注入 | 完了 |
| 1 | `convert` CLI | 完了 |
| 2 | ImageJob + 編集エンジン | 完了 |
| 3 | `composite` | 完了 |
| 5 | スキル | 完了 |
| 4 | `text` / フォント | 未着手 |
| 6–7 | trim, diff, inspect, sheet | 未着手 |

## ライセンス

MIT License（[LICENSE](LICENSE) 参照）
