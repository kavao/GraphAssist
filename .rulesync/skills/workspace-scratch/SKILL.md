---
name: workspace-scratch
description: >-
  一時 Python・試行データは _workingspace/_scratch/ に置き、セッション終了時に削除または
  scripts/gen_*.py / Batch へ昇格する。samples/source/ への中間配置は禁止。
---
# Workspace Scratch（一時作業）

## 目的

試行錯誤用ファイルを **固定の一時領域** に集約し、正本（`samples/`・`scripts/gen_*.py`）と中間ゴミを混同しない。

## 置き場

| 種類 | パス | Git |
|------|------|-----|
| 一時 Python・試行データ | `_workingspace/_scratch/` | 管理外 |
| ツール出力・Batch 中間 | `generated/` | 管理外 |
| 再現スクリプト | `scripts/gen_*.py` | **管理** |
| 完成パイプライン | `samples/jobs/*.json`（Batch） | **管理** |

README 正本: [_workingspace/_scratch/README.md](../../_workingspace/_scratch/README.md)

## 手順

1. 探索・合成試行は `_workingspace/_scratch/` にのみ書く（`_workingspace/` 直下や `scripts/` への ad hoc 禁止）。
2. 中間 PNG / JSON を `samples/source/` にコピーしない。Batch 連鎖は [ga-batch-runner スキル](../ga-batch-runner/SKILL.md) の `generated/` → 次 `job` を使う。
3. 再現が必要になったら昇格する:
   - 1 コマンド化 → `samples/jobs/*_pipeline.json`
   - 土台再生成 → `scripts/gen_*.py`
4. セッション終了時: scratch を削除。残す場合は [workspace-audit-log スキル](../workspace-audit-log/SKILL.md) で理由を追記。
5. `.rulesync/skills/` を編集したら `corepack pnpm dlx rulesync generate` で副本へ反映する。

## mosaic / job との関係

- CharGrid 合成の試行 → scratch → 成功後 `samples/mosaic/*.json` または merge ツール（計画 MP2）
- タイトル・装飾 → ImageJob / Batch（CharGrid 直埋めの日本語は非推奨）

## 参照

- [ga-mosaic-art スキル](../ga-mosaic-art/SKILL.md)
- [ga-image-job-runner スキル](../ga-image-job-runner/SKILL.md)
- [20260615-mosaic-pipeline-plan.md](../../_workingspace/plans/20260615-mosaic-pipeline-plan.md)
