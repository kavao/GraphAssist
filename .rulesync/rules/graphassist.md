---
targets: ["*"]
description: "GraphAssist LLM 向け — JSON パイプライン・スキル導線・禁止事項（firstplan AGENTS.md の後継）"
globs: ["**/*"]
---

# GraphAssist — LLM 実行ルール

GraphAssist では **LLM は検証済み JSON を書き、Python CLI が実行する**。  
ImageMagick / Pillow の生 API / 任意シェルは LLM が直接生成しない。

完了規律・査証ログ・テストの横断正本は [concepts.md](concepts.md)。手順の詳細は各 **ga-*** スキルへ委譲する。

## 基本方針

- ユーザーの自然言語指示 → **ImageJob JSON** または **Batch manifest JSON** に変換する。
- 実行は `uv run graphassist …`（`job` / `run` / `mosaic` / `convert` / `analyze` 等）。
- 本番前に **`--dry-run`** で検証する（Batch / Job / 課金系は必須）。
- 出力画像は `generated/`、ログは `generated/logs/`。作業事実は [workspace-audit-log スキル](../skills/workspace-audit-log/SKILL.md) で `_workingspace/log/` へ追記。
- コード変更後は [code-testing スキル](../skills/code-testing/SKILL.md) でテストを通す。

## パス制限

| 種別 | 許可 |
|------|------|
| 入力画像 | `samples/source/`、`samples/mosaic/`、カタログ materialize 後、`generated/`（Batch 連鎖） |
| 出力 | `generated/` 配下のみ |
| Job / Batch 正本 | `samples/jobs/*.json`（試行のみ `_workingspace/_scratch/` → [workspace-scratch](../skills/workspace-scratch/SKILL.md)） |
| フォント | `assets/fonts/`（`resolve_font` が runtime → legacy を参照） |

禁止: 絶対パス、`..` による親ディレクトリ参照、許可外ディレクトリへの書き込み。

## 実行エンジン

- **Pillow + NumPy のみ**（ImageMagick / OpenCV は採用しない）。
- LLM が `magick`, `convert`（IM）, `ffmpeg` 等の外部画像コマンドを生成しない。
- 一時試行は `_workingspace/_scratch/`。再現が必要なら `samples/jobs/`（Batch）へ昇格。

## スキル導線（タスク → 正本）

| やりたいこと | スキル | CLI 例 |
|--------------|--------|--------|
| 1 枚の編集（resize / text / composite 等） | [ga-image-job-runner](../skills/ga-image-job-runner/SKILL.md) | `graphassist job` |
| フォルダ一括変換・trim 等 | [ga-image-processing](../skills/ga-image-processing/SKILL.md) | `graphassist convert` |
| mosaic + job + analyze の複数ステップ | [ga-batch-runner](../skills/ga-batch-runner/SKILL.md) | `graphassist run` |
| CharGrid JSON の作成・decode・merge | [ga-mosaic-art](../skills/ga-mosaic-art/SKILL.md) | `graphassist mosaic` |
| 品質確認・before/after 比較 | [ga-image-analysis](../skills/ga-image-analysis/SKILL.md) | `graphassist analyze` |
| CC0 素材の id 参照・overlay | [ga-catalog-assets](../skills/ga-catalog-assets/SKILL.md) | Batch `assets.materialize` |

**カタログ id の新規追加** や **runtime-manifest の変更** は LLM 禁止 — 人間が manifest を更新する。

## フォント

- **Git 同梱（clone 直後）:** `DejaVuSans.ttf`, `PixelMplus12-Regular.ttf`（birds デモ・基本テスト向け）
- **追加フォント（Noto / 美咲 / Inter 等）:** `scripts/setup-runtime.ps1` または `runtime_fetch.py`
- Job JSON では `assets/fonts/...` を指定（詳細: [assets/fonts/README.md](../../assets/fonts/README.md)）

## 禁止事項（要約）

- `rm`, `curl`, `wget`, 任意 `powershell -c` / `bash -c` を含むコマンド生成
- LLM 生成の生シェルをそのまま本番実行
- 許可外 operation type・未登録 catalog id
- チャット貼り付けだけで「画像生成完了」と報告（[concepts.md](concepts.md) の完了扱い）

## 参照

- 操作一覧: `docs/ja/image/operations.md`（編集正本）→ `docs/en/image/operations.md`
- クイックスタート: `docs/ja/quickstart.md`
- 設置・runtime: `docs/ja/setup/runtime.md`
- 計画・overview: `_workingspace/plans/overview.md`, `work-plan.md`
