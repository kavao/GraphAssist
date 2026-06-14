---
name: user-locale
description: "ホーム config から会話言語を読取り、user_prefs.py sync で IDE 向け user-locale 副本を再生成する"
targets: ["*"]
---

## 目的

話者ごとに LLM との**基本会話言語**を切り替える。
会話言語と docs / ハーネスの**書き込み正本**は別軸（`content-placement` 参照）。
**git コミットメッセージ**は英語固定（`rules/git.md`）。案を出すときは英語の下に、会話言語での説明を付ける。

## 正本と副本

| 種類 | 置き場 |
|------|--------|
| 設定正本 | `~/.config/dna-kernel/config.toml` |
| プロジェクト上書き | `.dna-kernel.local.toml`（gitignore） |
| IDE 向け副本 | `.cursor/rules/user-locale.mdc`, `.claude/rules/user-locale.md`（gitignore 配下） |

秘密（API キー等）は `.env` のみ。ホーム config には置かない。

## 優先順位（会話言語）

1. チャットでの明示（「英語で」「日本語で」）
2. `.dna-kernel.local.toml` の `conversation.language`
3. ホーム config の `conversation.language`
4. OS locale 等（`user_prefs.py` が判定）

## 標準手順（正本）

`corepack pnpm dlx rulesync generate` の**後**に必ず sync する（`delete: true` で副本が消えるため）。

```bash
corepack pnpm dlx rulesync generate --dry-run
corepack pnpm dlx rulesync generate
uv run python tools/kernel/user_prefs.py sync
```

初回のみ、ホーム config テンプレ:

```bash
uv run python tools/kernel/user_prefs.py init-config
```

## 適用する場面

- ルール変更後に rulesync generate した直後
- ユーザーが会話言語を変えた直後
- セッション開始時に user-locale 副本の有無を確認するとき

## 手順

1. 必要なら `user_prefs.py init-config` でホーム config を作成する。
2. `user_prefs.py show conversation.language` で解決結果（値と出典）を確認する。
3. `user_prefs.py sync`（または `--dry-run` で対象パス確認）を実行する。
4. `.cursor/rules/user-locale.mdc` 等が存在することを Read で確認する。

## 禁止

- 副本（user-locale）だけ手編集して完了扱いにしない。設定変更はホーム config または local へ。
- rulesync generate 後に sync を省略しない（次回 generate で副本が消える）。

## 関連

- 配置判断: `skills/content-placement/SKILL.md`
- docs バイリンガル: `rules/docs-writing.md` §0
- 出力規律: `skills/output-discipline/SKILL.md`
- コミットメッセージの言語: `rules/git.md`
