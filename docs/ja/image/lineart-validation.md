# LineArt Validation Report / Repair Loop

[English](../../en/image/lineart-validation.md) · 日本語

このページは、LineArt の幾何検証結果を JSON レポートとして保存し、そのレポートを LLM の自己修正ループへ渡すための初期仕様です。Validation Report JSON v0.1 は「何が壊れているか」を構造化し、Repair Loop v0.1 は「どの範囲を何回まで修正するか」を定義します。

## このドキュメントを使う場面

LineArt JSON を生成したあと、重なり、はみ出し、接続ミス、意図しない交差などを機械的に確認したいときに使います。

最小限の指示文は次のようにできます。

```text
LineArt JSON を検証して、修正ループ用のレポートを作ってください。
```

このように入力すると、アシスタントは LineArt JSON を検証し、問題点を Validation Report JSON として保存する流れを組みます。現在は `lineart validate --report` で、metadata の参照整合性と geometry 正規化の結果を同じ形式で出力できます。

LineArt JSON を検証し、レポートを保存します。

```bash
# 確認（dry-run）— 入力 JSON とレポート保存先を検証する
uv run graphassist lineart validate samples/lineart/icon_minimal.json --report generated/logs/icon_minimal_validation.json --dry-run

# 本番実行 — Validation Report JSON v0.1 を保存する
uv run graphassist lineart validate samples/lineart/icon_minimal.json --report generated/logs/icon_minimal_validation.json
```

実行後、`generated/logs/` に検証レポートが保存されます。
SVG レンダリングの dry-run と同時に report を保存したい場合は、`lineart render --validate-report` を使います。

```bash
# 確認と report 保存 — SVG/PNG は書かず、Validation Report JSON v0.1 を保存する
uv run graphassist lineart render samples/lineart/icon_minimal.json generated/vector/icon_minimal.svg --dry-run --validate-report generated/logs/icon_minimal_validation.json
```

## 全体フロー

```text
LineArt JSON
  ↓
幾何検証
  ↓
Validation Report JSON v0.1
  ↓
Repair Loop v0.1
  ↓
LLM が JSON を修正
  ↓
再検証
```

## Validation Report JSON v0.1

Validation Report は、検証結果を LLM と人間の両方が読みやすい形で保存します。自然文だけで指摘せず、対象 object、位置、計測値、修正ヒントを JSON に入れます。

```json
{
  "version": "0.1",
  "validation_result": "failed",
  "source": {
    "document_id": "flow_01",
    "input_path": "samples/lineart/flow_01.json"
  },
  "summary": {
    "errors": 1,
    "warnings": 1,
    "info": 0
  },
  "issues": [
    {
      "issue_id": "LV-0001",
      "type": "connector_misaligned",
      "severity": "error",
      "object_ids": ["arrow_01", "node_a", "node_b"],
      "position": [320, 180],
      "metric": {
        "distance_to_target": 18.5,
        "max_allowed_distance": 4
      },
      "message": "arrow_01 does not touch node_b.",
      "repair_hint": {
        "action": "move_endpoint",
        "target": "arrow_01",
        "anchor": "to",
        "toward": "node_b"
      }
    }
  ]
}
```

## report のフィールド

| フィールド | 用途 |
|------------|------|
| `version` | レポート形式のバージョンです。初期値は `"0.1"` です。 |
| `validation_result` | `passed`, `failed`, `warning_only` のいずれかです。 |
| `source` | 検証した LineArt JSON の識別情報です。 |
| `summary` | error / warning / info の件数と、正規化した geometry 数です。 |
| `issues[]` | 検出した問題の配列です。 |

## issue のフィールド

| フィールド | 用途 |
|------------|------|
| `issue_id` | レポート内で一意な ID です。 |
| `type` | `overlap`, `outside_container`, `connector_misaligned` などの問題種別です。 |
| `severity` | `error`, `warning`, `info` のいずれかです。 |
| `object_ids` | 問題に関係する shape id の配列です。 |
| `position` | 問題の代表位置です。省略できます。 |
| `metric` | 距離、面積、しきい値などの数値情報です。 |
| `message` | 人間向けの短い説明です。 |
| `repair_hint` | LLM が修正方針を選ぶための構造化ヒントです。 |

## repair_hint の初期案

| フィールド | 用途 |
|------------|------|
| `action` | `move`, `move_endpoint`, `resize`, `reroute`, `reorder_layer`, `keep_clear` などの修正種別です。 |
| `target` | 修正対象の shape id です。 |
| `anchor` | 接続線の `from` / `to` など、部分修正の対象です。 |
| `toward` | 近づける対象の shape id です。 |
| `delta` | `[dx, dy]` などの移動量です。 |
| `constraints` | 修正時に守る条件です。 |

## Repair Loop v0.1

Repair Loop は、Validation Report を受け取った LLM がどの範囲をどの条件で修正するかを定義します。

```json
{
  "version": "0.1",
  "mode": "patch_preferred",
  "max_iterations": 3,
  "stop_when": {
    "errors": 0,
    "allow_warnings": true
  },
  "repair_scope": {
    "locked_ids": ["logo_mark"],
    "editable_ids": ["arrow_01", "label_01"]
  },
  "inputs": {
    "lineart_document": "current document JSON",
    "validation_report": "Validation Report JSON v0.1"
  }
}
```

## Repair Loop の方針

- まず targeted patch を優先し、全体再生成は最後の手段にします。
- `locked_ids` に入った shape は動かしません。
- `errors` が 0 になったら停止します。
- `warning` を許容するかは `stop_when.allow_warnings` で決めます。
- 同じ `issue_id` または同じ `type` が残り続ける場合は、最大試行回数で停止します。

LR2 では、この方針を `RepairLoopConfig` として Pydantic schema 化しています。
`mode`, `max_iterations`, `stop_when`, `repair_scope`, `inputs` を検証し、修復対象 issue が `locked_ids` に触れる場合は blocked として扱います。
`editable_ids` を指定した場合は、その範囲だけを修復候補にします。
修復可能な issue がなく blocked のみ残る場合は `blocked_by_scope` として停止します。
同じ issue type と object ids が繰り返される場合は、`stop_when.repeated_issue_limit` で停止判定できます。

## LLM 修正入力として返す形

Validation Report を LLM に戻すときは、自然文だけで「ここを直す」と伝えず、保存済み JSON のパスと修正制約を一緒に渡します。
これにより、同じ入力で再検証でき、`locked_ids` や `editable_ids` の制約も保持できます。

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

サンプルとして、複数の issue を意図的に含む [repair_loop_issues.json](../../../samples/lineart/repair_loop_issues.json) と、検証 report を出力する [lineart_repair_loop_validate.json](../../../samples/jobs/lineart_repair_loop_validate.json) を用意しています。

## メタデータとの関係

LineArt Metadata は「何を意図しているか」を shape 側に持たせます。Validation Report は「実際に何が問題だったか」を出力します。Repair Loop は、その差分を LLM に戻して修正させます。

```text
metadata: label_01 should be inside panel_01
validation: label_01 is outside panel_01
repair: move label_01 into panel_01
```

## 現在の実装範囲

LV0.1-LV4.2 と LR2 では、次の処理を行います。

- `role`, `container_id`, `connects_to`, `validation.expected` を読み、参照先 shape が存在するか確認します。
- `rect`, `ellipse`, `polygon`, `star`, `path`, `smooth_path`, `group` を point / polyline / polygon / bbox に正規化します。
- `smooth_path`, `Q`, `C` の曲線はポリラインへサンプリングします。
- `validation.expected.no_intersections: true` がある shape について、意図しない線分交差を `line_intersection` として報告します。
- `allow_overlap: false` がある閉じた shape について、bbox ベースの重なりを `overlap` として報告します。
- `container_id` または `validation.expected.inside` がある shape について、bbox が container 内に収まるか確認し、外れていれば `outside_container` として報告します。
- `connects_to` がある connector について、始点・終点が接続対象 bbox に近いか確認し、離れていれば `connector_misaligned` として報告します。
- role と bbox / containment から不自然な描画順を検出し、`layer_order` として報告します。
  - `background` が他の図形より前面に描かれている場合
  - `container` が内包 shape より前面に描かれている場合
  - `decorative` が `connector` を覆う可能性がある場合
- `lineart validate --report` で Validation Report JSON v0.1 を `generated/logs/` へ保存します。
- `lineart render --validate-report` で、SVG/PNG render と同じ入力に対する Validation Report JSON v0.1 を保存します。
- Batch `lineart.validate` command で、複数ステップの中に検証 report 出力を組み込めます。
- Repair Loop JSON v0.1 の schema、停止条件、locked / editable scope、同一 issue 反復停止を検証します。
- Validation Report JSON を LLM 修正入力として返すための JSON 形と fixture を用意します。

## 更新方針

このページは、幾何検証の実装に合わせて逐次更新します。新しい issue type を追加するときは、まず `issues[].type` と `repair_hint.action` に小さく追加し、複数の検証器で共通化できる段階で schema へ昇格します。
