# dna_kernel 導入・注入フロー

[English](../../en/dna-kernel/onboarding.md) · 日本語

dna_kernel には、次の3つの作業モードがあります。

| モード | 用途 | README の扱い |
|--------|------|---------------|
| 新規プロジェクト作成モード | まだ概要や README がない場所へ立ち上げる | 作成するか確認してからプロジェクト用 README を作る |
| 既存プロジェクト注入モード | すでにあるプロジェクトへ dna_kernel を追加する | 既存 README は触らず、dna_kernel 説明は `docs/ja/dna-kernel/` と `docs/en/dna-kernel/` へ置く |
| DNA_KERNEL 開発モード | dna_kernel 本体を修正する | 導入質問を省略して直接修正する |

## 既存プロジェクト注入モード

既存プロジェクトでは、既存の構成を壊さないことを優先します。

ユーザーが注入先ディレクトリを明示した場合、そのディレクトリを注入先ルートとして扱います。
monorepo の上位ディレクトリや Git ルートへ自動的には広げません。

例:

```text
K:\共有\10_プログラム\node\grokbot_news\packages\discord-bot\
```

このパスを指定された場合、以下は `packages/discord-bot/` 配下へ置きます。

```text
.rulesync/
rulesync.jsonc
docs/ja/dna-kernel/
docs/en/dna-kernel/
tools/kernel/
_workingspace/
```

基本方針:

- 既存の `README.md` を上書きしない
- `images/title.png` は dna_kernel 本体 README 用のタイトル画像であり、注入先プロジェクトへは**取り込まない**
- 既存の `.gitignore`, `pyproject.toml`, `tools/`, `docs/` は内容を確認してから追記する
- dna_kernel の詳しい説明は `docs/ja/dna-kernel/`（編集正本）と `docs/en/dna-kernel/`（対訳）へ置く
- `.rulesync/`, `rulesync.jsonc`, `tools/kernel/` を正本・実働ツールとして追加する
- rulesync 生成物（`.claude/`, `.cursor/`, `.codex/`, `.agents/`, `.kilo/`, `AGENTS.md`, `CLAUDE.md`）は ignore する

推奨フロー:

1. 既存の README・docs・tools・.rulesync・rulesync.jsonc の有無を確認する
2. 注入してよいか、変更予定を提示して了承を得る
3. `docs/ja/dna-kernel/` に説明文書を置き、`docs/en/dna-kernel/` に英訳を同期する
4. `.rulesync/` と `rulesync.jsonc` を追加または統合する
5. `tools/kernel/` に必要なツールを置く
6. `.gitignore` に rulesync 生成物と `_workingspace/` の扱いを追記する
7. `corepack pnpm dlx rulesync generate --dry-run` で生成内容を確認する
8. 了承後に `corepack pnpm dlx rulesync generate` を実行する
9. `uv run python tools/kernel/user_prefs.py sync` で会話言語副本を再生成する
10. 必要なら `overview.md` を作るか確認し、プロジェクトの目的・成果物・制約を聞く

## 新規プロジェクト作成モード

新規プロジェクトでは、最初に `overview.md` の有無を確認します。
なければ作成するかを確認し、了承後に rulesync と uv の導入状況を確認します。

導入の基本コマンド:

```bash
corepack enable
uv run python init.py
corepack pnpm dlx rulesync generate --dry-run
corepack pnpm dlx rulesync generate
uv run python tools/kernel/user_prefs.py sync
```

`corepack pnpm dlx rulesync` だけでは、現在の rulesync ではヘルプが表示されるだけです。
生成には `generate` サブコマンドを使います。`generate` の**後**に `user_prefs.py sync` を実行します。

## 会話言語とホーム config

**会話言語**（LLM とのチャット）と **docs の編集正本**（`docs/ja/` → `docs/en/` 同期）は別軸です。日本語で会話していても、docs は `docs-writing` のバイリンガル方針に従います。

| 設定 | 置き場 | git 管理 |
|------|--------|----------|
| 会話言語・執筆既定 | `~/.config/dna-kernel/config.toml` | ×（個人マシン） |
| プロジェクト上書き | `.dna-kernel.local.toml` | ×（gitignore） |
| API キー等 | `.env` | × |

初回テンプレ作成:

```bash
uv run python tools/kernel/user_prefs.py init-config
```

会話言語の確認:

```bash
uv run python tools/kernel/user_prefs.py show conversation.language
```

執筆前は `content-placement` スキルで種類と正本を宣言します（`user-locale` と併用）。

## .gitignore 例

```gitignore
# rulesync 生成物
# 正本は rulesync.jsonc と .rulesync/ に置き、各ツール向け生成物は除外する
.claude/
.cursor/
.codex/
.kilo/
.agents/
AGENTS.md
CLAUDE.md

# ワークスペース（ローカル作業ファイル）
_workingspace/**
!_workingspace/**/
!_workingspace/**/.gitkeep
_backup/
_old/

# user-locale: プロジェクト local 上書き
.dna-kernel.local.toml
```
