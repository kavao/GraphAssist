---
name: ga-lineart
description: LineArt JSON を生成・検証し、graphassist lineart render / validate / Batch lineart.render で SVG・PNG・検証レポートを扱う
---

# LineArt

## 目的

LLM が **LineArt JSON** を生成し、Python CLI が検証して SVG / PNG にレンダリングする。
SVG 全文を LLM が手書きせず、shape / layer / metadata / gradient / group などの構造化 JSON を正本にする。

## いつ使うか

| 状況 | 使うコマンド |
|------|--------------|
| LineArt JSON 1 件を SVG にする | `graphassist lineart render` |
| SVG と PNG を同時に作る | `graphassist lineart render --png` |
| metadata 参照と geometry 正規化を検証する | `graphassist lineart validate --report` |
| render 入力を検証し report も保存する | `graphassist lineart render --validate-report` |
| LineArt PNG を ImageJob で後処理する | `graphassist run` の `lineart.render` → `job` |
| Batch 内で検証 report を保存する | `graphassist run` の `lineart.validate` |
| 複数種類の処理を混ぜる | [ga-batch-runner](../ga-batch-runner/SKILL.md) |

## 手順

1. ユーザーの指示から、図形、レイヤー、色、線、メタデータを抽出する。
2. **SVG 全文や任意シェルは生成しない。**
3. `version`, `canvas`, `definitions`, `layers` を持つ LineArt JSON を書く。
4. JSON を保存する。
   - サンプル・正本: `samples/lineart/*.json`
   - 生成途中: `generated/lineart/*.json`
5. dry-run で検証する。

```bash
uv run graphassist lineart render samples/lineart/icon_minimal.json generated/vector/icon_minimal.svg --dry-run
```

6. metadata 参照と geometry 正規化を検証する。

```bash
uv run graphassist lineart validate samples/lineart/icon_minimal.json --report generated/logs/icon_minimal_validation.json --dry-run
uv run graphassist lineart validate samples/lineart/icon_minimal.json --report generated/logs/icon_minimal_validation.json
```

7. render dry-run と同時に report を保存する。

```bash
uv run graphassist lineart render samples/lineart/icon_minimal.json generated/vector/icon_minimal.svg --dry-run --validate-report generated/logs/icon_minimal_validation.json
```

8. 問題なければ SVG を生成する。

```bash
uv run graphassist lineart render samples/lineart/icon_minimal.json generated/vector/icon_minimal.svg
```

9. PNG が必要な場合は `--png` を指定する。

```bash
uv run graphassist lineart render samples/lineart/icon_minimal.json generated/vector/icon_minimal.svg --png generated/images/icon_minimal.png --png-width 512
```

10. 複数ステップでは Batch manifest を使う。

```bash
uv run graphassist run samples/jobs/lineart_icon_pipeline.json --dry-run
uv run graphassist run samples/jobs/lineart_icon_pipeline.json
```

11. `generated/vector/`, `generated/images/`, `generated/logs/` を確認し、査証ログに追記する。

## LineArt JSON の最小構造

```json
{
  "version": "1.0",
  "canvas": {
    "width": 128,
    "height": 128,
    "background": "transparent"
  },
  "definitions": {
    "gradients": {},
    "clip_paths": {}
  },
  "layers": [
    {
      "id": "main_layer",
      "shapes": [
        {
          "id": "panel_01",
          "type": "rect",
          "x": 20,
          "y": 20,
          "width": 88,
          "height": 88,
          "fill": {"type": "solid", "color": "#f6f8fa"},
          "stroke": {"color": "#1f2328", "width": 3}
        }
      ]
    }
  ]
}
```

## shape type

| type | 用途 |
|------|------|
| `rect` | 矩形・角丸矩形 |
| `ellipse` | 円・楕円 |
| `polygon` | 多角形 |
| `star` | 星形 |
| `path` | M/L/Q/C/Z の明示パス |
| `smooth_path` | 点列から Catmull-Rom 曲線へ変換 |
| `group` | 子 shape をまとめて transform / clip / opacity |

## style / metadata

- `fill`: `"none"`、`{"type":"solid","color":"#RRGGBB"}`、`{"type":"gradient","ref":"id"}`
- `stroke`: `color`, `width`, `join`, `cap`
- `definitions.gradients`: `linear` / `radial`
- `definitions.clip_paths`: clip 用 shape 群
- metadata: `role`, `tags`, `container_id`, `connects_to`, `validation`

metadata は Phase LV の幾何検証と Repair Loop の入力になる。図解・フローチャートでは `role`, `container_id`, `connects_to` をなるべく付ける。

## validate レポート

`lineart validate --report` は Validation Report JSON v0.1 を `generated/logs/` に保存する。
現時点では LV0.1-LV2.5 として metadata 参照整合性、geometry 正規化、線分交差、重なり、包含、接続距離、layer order warning を確認する。
Repair Loop LR2 として `RepairLoopConfig` schema、停止条件、`locked_ids` / `editable_ids`、warning 許容、同一 issue 反復停止、blocked scope 停止も Pydantic で検証する。

```bash
uv run graphassist lineart validate samples/lineart/icon_minimal.json --report generated/logs/icon_minimal_validation.json
```

## 修正入力フロー

Validation Report JSON を LLM 修正入力として返すときは、自然文だけで指摘しない。
次の順で、保存済み JSON のパスと修正制約を短く返す。

1. `lineart validate --report` または Batch `lineart.validate` で report を保存する。
2. report の `validation_result`, `summary`, `issues[]`, `repair_hint` を確認する。
3. ユーザーへ次を返す。
   - `lineart_document`: 修正対象 LineArt JSON
   - `validation_report`: 保存済み report JSON
   - `repair_loop`: `mode`, `max_iterations`, `stop_when`, `repair_scope`
   - `repair_focus`: 優先 issue type と対象 id
4. 修正時は `locked_ids` を変更せず、`editable_ids` が指定されていればその範囲だけを変更する。
5. 修正後、同じ validate command を再実行して report を更新する。

修正入力の最小形:

```json
{
  "lineart_document": "samples/lineart/repair_loop_issues.json",
  "validation_report": "generated/logs/lineart_repair_loop_validation.json",
  "repair_loop": {
    "version": "0.1",
    "mode": "patch_preferred",
    "max_iterations": 3,
    "stop_when": {
      "errors": 0,
      "allow_warnings": true,
      "repeated_issue_limit": 2
    },
    "repair_scope": {
      "locked_ids": [],
      "editable_ids": []
    },
    "inputs": {
      "lineart_document": "samples/lineart/repair_loop_issues.json",
      "validation_report": "generated/logs/lineart_repair_loop_validation.json"
    }
  },
  "repair_focus": ["outside_container", "connector_misaligned", "line_intersection"]
}
```

## Batch 連携

LineArt PNG を ImageJob で後処理するときは `lineart.render` の `png_output` を直後の `job.input` にする。

```json
{
  "version": "1.0",
  "commands": [
    {
      "type": "lineart.render",
      "input": "samples/lineart/icon_minimal.json",
      "output": "generated/vector/lineart_icon.svg",
      "png_output": "generated/images/lineart_icon_base.png",
      "png_width": 128
    },
    {
      "type": "job",
      "input": "generated/images/lineart_icon_base.png",
      "output": "generated/images/lineart_icon.png",
      "operations": [
        {"type": "extend", "left": 8, "right": 8, "top": 8, "bottom": 8, "fill": "transparent"}
      ]
    }
  ]
}
```

## パス制限

| 種別 | 許可パス |
|------|----------|
| LineArt JSON 入力 | `samples/lineart/`, `generated/lineart/` |
| SVG 出力 | `generated/vector/` |
| PNG 出力 | `generated/images/` |
| 検証レポート | `generated/logs/` |
| Batch manifest | `samples/jobs/` |

## 禁止事項

- SVG 全文を LLM が直接生成して正本扱いする
- ImageMagick、任意シェル、外部エディタ操作を生成する
- 絶対パス、`..` パス、許可外ディレクトリへの出力
- `generated/` の中間 PNG を `samples/source/` にコピーして正本化する
- LineArt JSON をチャットに貼っただけで完了扱いする

## 参照

- [docs/ja/image/lineart.md](../../docs/ja/image/lineart.md)（編集正本）
- [docs/en/image/lineart.md](../../docs/en/image/lineart.md)
- [docs/ja/image/lineart-metadata.md](../../docs/ja/image/lineart-metadata.md)
- [docs/ja/image/lineart-validation.md](../../docs/ja/image/lineart-validation.md)
- [docs/ja/image/batch.md](../../docs/ja/image/batch.md)
- [samples/lineart/icon_minimal.json](../../samples/lineart/icon_minimal.json)
- [samples/jobs/lineart_icon_pipeline.json](../../samples/jobs/lineart_icon_pipeline.json)
