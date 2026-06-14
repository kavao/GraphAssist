# GraphAssist dna_kernel manifest

このファイルは、各ファイルの役割と、導入先プロジェクトへ移植・注入するときの推奨配置先を示します。

## .rulesync/rules/（概念・ガバナンスの正本）

rulesync が各 LLM ツールの設定ファイルへ変換します。

| ファイル | 役割 | 導入先での配置先 |
|----------|------|--------------------------|
| `.rulesync/rules/concepts.md` | 正本・副本・完了条件の概念定義 | `.rulesync/rules/concepts.md` |
| `.rulesync/rules/rule-authoring.md` | ルール追加時の分類・置き場の作法 | `.rulesync/rules/rule-authoring.md` |
| `.rulesync/rules/docs-writing.md` | docs/ ドキュメント記述ルール（`docs/**/*.md` に適用） | `.rulesync/rules/docs-writing.md` |
| `.rulesync/rules/git.md` | git コミットメッセージ・ブランチ運用ルール | `.rulesync/rules/git.md` |

## .rulesync/skills/（LLM 向けの実行手順）

rulesync が各 LLM ツールのスキル設定へ変換します。

| ファイル | 役割 | 導入先での配置先 |
|----------|------|--------------------------|
| `.rulesync/skills/workspace-audit-log/SKILL.md` | 査証ログ追記の手順 | `.rulesync/skills/workspace-audit-log/` |
| `.rulesync/skills/workspace-diary/SKILL.md` | 横断ナレッジ日記の手順 | `.rulesync/skills/workspace-diary/` |
| `.rulesync/skills/output-discipline/SKILL.md` | ファイル出力→確認→報告の完了規律 | `.rulesync/skills/output-discipline/` |
| `.rulesync/skills/pre-work-check/SKILL.md` | 作業前の必須確認パターン | `.rulesync/skills/pre-work-check/` |
| `.rulesync/skills/backup-before-edit/SKILL.md` | 上書き前の旧版退避パターン | `.rulesync/skills/backup-before-edit/` |
| `.rulesync/skills/approval-flow/SKILL.md` | dry-run→承認→実行→確認の承認フロー | `.rulesync/skills/approval-flow/` |
| `.rulesync/skills/weighted-pick/SKILL.md` | JSON 重み付き乱数選択の手順 | `.rulesync/skills/weighted-pick/` |
| `.rulesync/skills/project-context/SKILL.md` | プロジェクト文脈の要約・引き継ぎ | `.rulesync/skills/project-context/` |
| `.rulesync/skills/project-onboarding/SKILL.md` | 新規作成・既存注入と overview.md 作成フロー | `.rulesync/skills/project-onboarding/` |
| `.rulesync/skills/code-testing/SKILL.md` | コード変更時のテスト実行・デグレード防止 | `.rulesync/skills/code-testing/` |
| `.rulesync/skills/user-locale/SKILL.md` | 会話言語と user-locale 副本 | `.rulesync/skills/user-locale/` |
| `.rulesync/skills/content-placement/SKILL.md` | 執筆前の正本・副本判断 | `.rulesync/skills/content-placement/` |
| `.rulesync/skills/image-processing/SKILL.md` | 一括 CLI | `.rulesync/skills/image-processing/` |
| `.rulesync/skills/image-job-runner/SKILL.md` | ImageJob JSON | `.rulesync/skills/image-job-runner/` |
| `.rulesync/skills/batch-runner/SKILL.md` | Batch manifest | `.rulesync/skills/batch-runner/` |
| `.rulesync/skills/mosaic-art/SKILL.md` | CharGrid | `.rulesync/skills/mosaic-art/` |
| `.rulesync/metadata/graphassist.json` | GraphAssist バージョン正本 | `.rulesync/metadata/graphassist.json` |
| `.rulesync/metadata/runtime-manifest.jsonc` | runtime 取得対象一覧 | 同左 |

## rulesync.jsonc（rulesync 設定）

| ファイル | 役割 | 導入先での配置先 |
|----------|------|--------------------------|
| `rulesync.jsonc` | targets・features の指定 | プロジェクトルート |
| `LICENSE` | MIT ライセンス正本 | プロジェクトルート |

## scripts/（設置 bootstrap）

| ファイル | 役割 |
|----------|------|
| `scripts/setup-runtime.ps1` | runtime 骨格作成（再実行可） |
| `scripts/setup-runtime.sh` | 同上（Unix） |

## runtime/（Git 管理外・設置先）

| パス | 内容 |
|------|------|
| `runtime/bin/` | graphassist.exe |
| `runtime/assets/fonts/` | 描画フォント |
| `runtime/assets/weights/` | 将来: AI 重み |
| `runtime/manifest.local.json` | インストール記録 |
| `runtime/README.md` | 説明（Git に含める） |

設計: [_workingspace/plans/deployment-design.md](_workingspace/plans/deployment-design.md) · [docs/ja/setup/runtime.md](docs/ja/setup/runtime.md)

## docs/（人間向けの説明）

rulesync の管理外。人間が読む説明ドキュメント。

| ファイル | 役割 | 導入先での配置先（例） |
|----------|------|-------------------------------|
| `docs/README.md` | 言語索引（**EN リンクを先**） | `docs/README.md` |
| `docs/ja/**` | 日本語編集正本 | `docs/ja/` |
| `docs/en/**` | 英語対訳・表示用 | `docs/en/` |
| `docs/dna-kernel/README.md` | 旧パス互換リダイレクト | `docs/dna-kernel/README.md` |
| `docs/ja/dna-kernel/` | dna_kernel 詳細（編集正本） | `docs/ja/dna-kernel/` |
| `docs/en/dna-kernel/` | dna_kernel 詳細（英訳） | `docs/en/dna-kernel/` |
| `README.md` | 入口（英語・表示デフォルト） | プロジェクトルート |
| `README.ja.md` | 入口（日本語・編集正本） | プロジェクトルート |
| `_workingspace/plans/overview.md` | プロジェクト文脈・方向性（ローカル計画） | `_workingspace/plans/` |
| `_workingspace/plans/2026-06-14-work-plan.md` | フェーズ別作業計画 | `_workingspace/plans/` |

## tools/graphassist/（GraphAssist ソース — 将来 `src/graphassist/`）

| ファイル | 役割 | 導入先での配置先（例） |
|----------|------|-------------------------------|
| `tools/graphassist/graphassist.py` | CLI エントリ（Pillow のみ） | `tools/graphassist/graphassist.py` |
| `tools/graphassist/version.py` | バージョン定数（組み込み・CLI 共用） | `tools/graphassist/version.py` |
| `tools/graphassist/convert_cmd.py` | convert 処理 | `tools/graphassist/convert_cmd.py` |
| `tools/graphassist/engine/canvas.py` | RGBA load/save・基本変換 | `tools/graphassist/engine/canvas.py` |
| `tools/graphassist/README.md` | 画像ツールの配置・利用手順 | `tools/graphassist/README.md` |

### バイナリ・runtime（Git 管理外）

| 項目 | 方針 |
|------|------|
| 設置先 | **`runtime/`**（`setup-runtime` で初期化） |
| 実行形式 | PyInstaller one-file exe（~35 MB） |
| フォント・重み | `runtime/assets/` |
| 取得 | Release / bootstrap（[runtime-manifest.jsonc](.rulesync/metadata/runtime-manifest.jsonc)） |
| ソース | `tools/graphassist/`（将来 `src/graphassist/`） |
| 非採用 | OpenCV / ImageMagick |

## tools/kernel/（実働コード）

### コア（どのプロジェクトにも移植できる）

| ファイル | 役割 | 導入先での配置先（例） |
|----------|------|-------------------------------|
| `tools/kernel/workspace_audit_log.py` | 査証ログ・日記への追記書き込み | `tools/kernel/workspace_audit_log.py` |
| `tools/kernel/user_prefs.py` | 会話言語・user-locale 副本 sync | `tools/kernel/user_prefs.py` |
| `tools/kernel/json_weighted_pick.py` | JSON 重み付き乱数選択 | `tools/kernel/json_weighted_pick.py` |

## 最小セット（どれか1つから始めるなら）

- **ルールだけ**: `.rulesync/rules/concepts.md` + `rulesync.jsonc` + `npx rulesync generate` 実行
- **ログまで**: 上記に `tools/kernel/workspace_audit_log.py` を追加
- **画像処理まで**: 上記に `tools/graphassist/graphassist.py` と `.rulesync/skills/image-processing/SKILL.md` を追加
