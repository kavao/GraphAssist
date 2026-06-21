# 他プロジェクトへの取り込み（ソース注入）

[English](../../en/setup/adoption.md) · 日本語

このガイドを読むと、既存リポジトリへ **GraphAssist をソースごと載せ、LLM から ImageJob / Batch で使える**状態まで持っていけます。

**原則:** **パターン B（ソース注入）** を採用します。CLI 本体だけを置いても動きますが、**rulesync（ルール・ga-* スキル）が無いと「JSON まで書かせて Python が実行する」価値がほとんど出ません**。取り込みは **ソース + rulesync + samples** をセットで想定してください。

---

## パターンの選び方

| パターン | 内容 | いつ使うか |
|----------|------|------------|
| **B. ソース注入（推奨・原則）** | `src/graphassist/` + `.rulesync/` + `samples/` 等を同リポジトリに載せる | **通常はこれ**。ゲーム・ツール・素材リポジトリへ LLM 連携付き画像処理を足す |
| A. runtime のみ | `setup-runtime` でバイナリ・フォントだけ取得 | ソースは別管理。B の一部として setup は **B でも実行する** |
| C. dna_kernel のみ | ガバナンス（`tools/kernel/`, concepts）だけ | 画像 CLI は不要なとき。[dna-kernel 導入](../dna-kernel/onboarding.md) を参照 |

以降は **パターン B** の手順です。

---

## なぜ rulesync をセットで取るか

GraphAssist の本体価値は次の組み合わせにあります。

| 要素 | 役割 |
|------|------|
| `src/graphassist/` | Pillow エンジン・CLI（検証付き実行） |
| `.rulesync/rules/graphassist.md` | LLM 向け禁止事項・パス制限・スキル導線 |
| `.rulesync/skills/ga-*` | ImageJob / Batch / mosaic / analyze / catalog の**手順正本** |
| `samples/jobs/` | 再現可能な Job・Batch の例 |

rulesync 無しだと、利用者は CLI コマンドを都度調べるだけになり、**firstplan の「LLM は JSON まで、Python が実行」**が機能しません。

---

## 取り込むもの（チェックリスト）

注入先ルート（monorepo なら **ユーザー指定のサブディレクトリ**）に、次を載せます。ファイル単位の一覧はリポジトリ正本 [manifest.md](../../../manifest.md) を参照してください。

### 必須（パターン B）

| パス | 内容 |
|------|------|
| `src/graphassist/` | CLI・engine・schema **ディレクトリごと** |
| `.rulesync/rules/graphassist.md` | GraphAssist LLM ルール |
| `.rulesync/skills/ga-*` | 画像系スキル一式（`ga-image-job-runner`, `ga-batch-runner`, `ga-mosaic-art`, `ga-image-processing`, `ga-image-analysis`, `ga-catalog-assets`） |
| `.rulesync/metadata/` | `graphassist.json`, `runtime-manifest.jsonc`, `asset-catalog.jsonc` |
| `rulesync.jsonc` | 既存がある場合は **targets / features を統合**（後述） |
| `scripts/setup-runtime.ps1`, `scripts/setup-runtime.sh`, `scripts/runtime_fetch.py` | runtime bootstrap |
| `samples/jobs/` | Job / Batch サンプル |
| `samples/mosaic/` | CharGrid サンプル（mosaic 利用時） |
| `samples/jobs/catalog/` | カタログ索引（catalog 利用時） |
| `assets/fonts/README.md` | フォント説明 |
| `assets/fonts/DejaVuSans.ttf`, `assets/fonts/PixelMplus12-Regular.ttf` | **Git 同梱フォント**（clone 直後から基本テスト可） |
| `runtime/README.md` | runtime ディレクトリの説明 |
| `pyproject.toml` | 新規ならそのまま。既存なら **依存と scripts をマージ**（後述） |

### dna_kernel ガバナンス（未導入なら推奨）

GraphAssist リポジトリは dna_kernel 前提です。取り込み先にまだ無ければ、あわせて次も検討します。

| パス | 内容 |
|------|------|
| `.rulesync/rules/concepts.md` 他 | 完了条件・査証ログ・テスト規律 |
| `.rulesync/skills/workspace-audit-log/` 等 | 運用スキル |
| `tools/kernel/` | 査証ログ・user-locale 等 |
| `_workingspace/` | 査証ログ・計画（構造のみ Git、中身は ignore） |

詳細: [dna-kernel 導入・注入](../dna-kernel/onboarding.md)

### 任意

| パス | 内容 |
|------|------|
| `tests/` | 回帰テストを取り込み先 CI で回す場合 |
| `docs/ja/`, `docs/en/` | 操作説明を同梱したい場合（**後述の GitHub 参照でも可**） |
| `samples/source/` | サンプル入力 PNG（小さいものだけ。大容量は取り込み先で用意） |

### 取り込まないもの

| パス | 理由 |
|------|------|
| `runtime/bin/*.exe`, `runtime/assets/**` | `setup-runtime` で取得（Git に載せない） |
| `generated/**` | 出力先（gitignore） |
| `.cursor/`, `.claude/`, `AGENTS.md` 等 | rulesync **生成物**（正本は `.rulesync/`） |
| `dist/`, `build/` | ローカルビルド |
| `images/title.webp` 等 | GraphAssist リポジトリ README 用の宣伝画像 |

---

## 既存プロジェクトへの統合手順

1. **注入先ルートを決める** — ユーザー指定ディレクトリをルートとし、monorepo 全体へ勝手に広げない。
2. **了承を得る** — 追加・マージ予定（`.rulesync/`, `pyproject.toml`, `.gitignore`）を提示する。
3. **ファイルをコピーまたは submodule 追加** — 上記チェックリストどおり。submodule にする場合も **パターン B と同じパス構成**にする。
4. **`pyproject.toml` をマージ** — 最低限、次を取り込み先に反映する。

```toml
dependencies = [
  "pillow>=10.0",
  "numpy>=2.0",
  "pydantic>=2.0",
]
# [project.scripts]
# graphassist = "graphassist.graphassist:main"
```

`[tool.hatch.build.targets.wheel]` の `packages = ["src/graphassist"]` や `extraPaths` も、既存構成に合わせて調整する。

5. **`.gitignore` を追記** — 取り込み先に無いブロックを追加する（`generated/**`, `runtime/**`, rulesync 生成物、同梱フォント例外など）。正本例: GraphAssist リポジトリの [`.gitignore`](../../../.gitignore)。
6. **既存 `.rulesync/` がある場合** — `ga-*` スキルと `graphassist.md` を **マージ**する。`rulesync.jsonc` の `targets` に利用ツールを足し、`features` に `"rules"`, `"skills"` が含まれることを確認する。
7. **依存インストール** — `uv sync`（または取り込み先の Python ワークフロー）。
8. **rulesync 生成** — `corepack pnpm dlx rulesync generate --dry-run` → 了承 → `generate`。続けて `uv run python tools/kernel/user_prefs.py sync`（dna_kernel 導入時）。
9. **runtime セットアップ** — [runtime.md](runtime.md) のとおり `setup-runtime` を実行（バイナリ・追加フォント）。
10. **動作確認** — 下記「取り込み後の確認」。

既存 `README.md` は **上書きしない**。GraphAssist の説明は `docs/ja/setup/` へ置くか、README に 1 行リンクを足す程度に留める（[project-onboarding](../../../.rulesync/skills/project-onboarding/SKILL.md) 方針）。

---

## 取り込み後の確認

```bash
uv run graphassist --version
uv run graphassist job samples/jobs/resize_border.json --dry-run
uv run graphassist run samples/jobs/birds_on_trunk_pipeline.json --dry-run
```

任意（テストを載せた場合）:

```bash
uv run python -m unittest discover -s tests -q
```

---

## 上流（GitHub）を参照する

取り込み後も、**最新の操作説明・サンプル・設計**は上流リポジトリを正とします。

| 参照先 | 用途 |
|--------|------|
| [github.com/kavao/GraphAssist](https://github.com/kavao/GraphAssist) | ソース正本・Issue / Release |
| [docs/（リポジトリ内）](https://github.com/kavao/GraphAssist/tree/main/docs) | クイックスタート・CLI・ImageJob・Batch（日英） |
| [manifest.md](https://github.com/kavao/GraphAssist/blob/main/manifest.md) | ファイル役割と移植先パス |
| [Releases](https://github.com/kavao/GraphAssist/releases) | `runtime/bin` 用バイナリ（ソース注入でも setup-runtime がここから取得） |

取り込み先に `docs/` を全部コピーしなくても、**GitHub の docs をブックマークして参照**すれば足りる場合が多いです。取り込み先で docs を編集する場合は [docs-writing](../../../.rulesync/rules/docs-writing.md) のバイリンガル方針（`docs/ja/` 正本 → `docs/en/` 同期）に従います。

---

## 関連ドキュメント

- [設置・runtime](runtime.md) — バイナリ・フォント・環境変数
- [クイックスタート](../quickstart.md)
- [dna-kernel 導入・注入](../dna-kernel/onboarding.md)
