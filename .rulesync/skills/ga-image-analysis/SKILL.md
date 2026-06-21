---
name: ga-image-analysis
description: >-
  graphassist analyze で画像の明るさ・色・2枚比較（Phase A）と局所 metrics（Phase L --spatial）を
  JSON 取得する。作業後の品質確認・before/after 検証・余白/bbox/ROI 判断に使う。
targets: ["*"]
---

# Image Analysis

## 目的

LLM は画像バイナリを直接見られない。**数値 JSON** でトーン・配置・領域を根拠付きで述べる。

| Phase | CLI | 内容 |
|-------|-----|------|
| A | `analyze` | 全体 luminance / palette / compare verdict |
| L | `analyze --spatial` | content_bbox, edge_inset, 3×3 grid, ROI |

## いつ使うか

- 「2枚の明るさが違うか」→ `--compare`
- 「余白はどれくらいか」「どこから色があるか」→ `--spatial`
- Job / composite **後**の QA → Batch 末尾に `type: analyze`
- 変換（`adjust`）前後 → compare + `--spatial`

## コマンド

```bash
# 1枚 profile
uv run graphassist analyze samples/source/a.png --format json

# 2枚 compare
uv run graphassist analyze samples/source/a.png --compare samples/source/b.png

# 局所 metrics（Phase L）
uv run graphassist analyze generated/images/out.png --spatial --format json

# ログ保存
uv run graphassist analyze generated/images/out.png --spatial \
  --output generated/logs/out_profile.json
```

## Batch 例

`input` が `generated/` のときは **直前 command の `output` と同一**、`compare` が `generated/` のときは **それ以前の command output** と一致させる（[ga-batch-runner](../ga-batch-runner/SKILL.md)）。

job 後の profile:

```json
{
  "type": "analyze",
  "input": "generated/images/tone_after.png",
  "output": "generated/logs/tone_after_profile.json",
  "spatial": true
}
```

before/after compare（[tone_analyze_pipeline.json](../../samples/jobs/tone_analyze_pipeline.json)）:

```json
{
  "type": "analyze",
  "input": "generated/images/tone_after.png",
  "compare": "generated/images/tone_before.png",
  "output": "generated/logs/tone_compare.json"
}
```

## 読み方

- `verdict.brightness_significantly_different` — 明るさ差が閾値超え
- `verdict.brightness_relation` — `b_darker_than_a` 等（固定語彙）
- `spatial.content_bbox` — 非背景の外接矩形
- `spatial.edge_inset` — 四辺から content 開始までの px
- `spatial.tiles[].id` — `r0c0` 形式（3×3 grid）
- `thresholds` — 引用して報告（推測しない）

## 委譲

- 明るさを **直す** → ImageJob `adjust`（Phase T）または convert
- ピクセル差分 PNG → `graphassist diff`
- 素材取得 → [ga-catalog-assets スキル](../ga-catalog-assets/SKILL.md)

## 禁止

- JSON を読まず「明るい/暗い」とだけ述べる
- 数値の閾値を勝手に変えて報告する

## 関連

- 設計: `_workingspace/plans/20260614-image-metrics-design.md`
- 変換: `_workingspace/plans/20260614-image-transform-design.md`
- Batch: [ga-batch-runner スキル](../ga-batch-runner/SKILL.md)
