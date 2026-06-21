---
name: content-placement
description: "執筆前に成果物の種類と編集正本・同期副本を宣言し、会話言語と混同しない"
targets: ["*"]
---

## 目的

ドキュメント・ルール・計画などを書く**前**に、種類と正本・副本を機械的に決める。
「日本語で話している」＝「JA だけ書けばよい」と誤判定しない。

**本文は書かない**。判断と参照リンクのみ（`rule-authoring` 準拠）。

## 2つの軸

| 軸 | 決めること | 参照 |
|----|-----------|------|
| 会話言語 | チャットの言語 | `skills/user-locale/SKILL.md` |
| 書き込み正本 | 何をどこに書くか | 本スキル + `rule-authoring` / `docs-writing` |

会話言語の設定は**書き込み正本を上書きしない**。

## 判定フロー

1. 秘密・API キーか → `.env`（触らない／ユーザー操作）
2. 読者は誰か
   - **LLM ハーネス** → `.rulesync/`
     - 定義・禁止・完了 → `concepts.md` 正本、スキルはリンク
     - 作業手順 → `.rulesync/skills/` 正本
   - **人間が操作** → `docs/ja/` 正本 → `docs/en/` 同期
   - **開発者のみ** → `_workingspace/plans/` 等（EN 不要）
   - **プロジェクト全体** → `overview.md`
3. dna_kernel 本体の入口 → `README.ja.md` 正本 → `README.md` 同期

## 執筆前の宣言（必須）

執筆・更新に入る前に、次をチャットまたは作業メモに出す。

```text
【配置判断】
- 種類: （概念 / スキル / 操作説明 / 計画 / 入口 / …）
- 編集正本: （パス）
- 同期副本: （パス、なければ「なし」）
- 会話言語: （ja|en、出典: user_prefs / 明示指示 / …）
- 触らない: （今回更新しない正本）
- 完了条件: （例: JA 更新 → EN 同期 → Read 確認 → 査証ログ）
```

`user_prefs.py show conversation.language` で会話言語の出典を確認できる。

## 典型例（日本語話者）

| 依頼 | 種類 | 編集正本 | 同期副本 |
|------|------|----------|----------|
| 導入手順を docs に | 操作説明 | `docs/ja/...` | `docs/en/...` |
| 完了条件をルール化 | 概念 | `concepts.md` | スキルはリンク |
| pre-work 手順追加 | スキル | `.rulesync/skills/...` | rulesync 生成物 |
| 設計メモ | 計画 | `_workingspace/plans/` | なし |
| 本体 README | 入口 | `README.ja.md` | `README.md` |

### 計画ファイル命名

`_workingspace/plans/` に新規ファイルを置くとき、名前は **[graphassist ルール](../rules/graphassist.md) §計画ファイル** の `YYYYMMDD-<slug>.md` に従う。

- **起票日** = 新規作成した日（JST）。既存ファイルの大改訂のみではリネームしない（必要なら `-v1` 等で別ファイル化）。
- 詳細・入口一覧: `_workingspace/plans/README.md`
- **公開 docs へリンクしない**: 計画の内容を読者向けに出す場合は `docs/ja/` 正本へ書く（[docs-writing](../rules/docs-writing.md) §計画書へのリンク禁止）

英語話者でも **docs 編集正本は `docs/ja/`**。会話が en でも EN 同期が必要なら `content-placement` の完了条件に含める。

## 適用する場面

- 新規ファイル作成・既存正本の更新依頼を受けたとき
- docs / rules / plans のどれに書くか迷うとき
- ユーザーが「ドキュメント書いて」とだけ言ったとき

## 適用しない場面

- チャットでの質問回答のみ（ファイル出力なし）
- 副本（rulesync 生成物・user-locale）の直接編集依頼（正本へ戻す）

## 関連

- 置き場の概念表: `rules/rule-authoring.md`
- docs 記述: `rules/docs-writing.md` §0
- 会話言語: `skills/user-locale/SKILL.md`
- 完了規律: `skills/output-discipline/SKILL.md`
