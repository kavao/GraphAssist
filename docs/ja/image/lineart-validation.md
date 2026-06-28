# LineArt Validation Report / Repair Loop

[English](../../en/image/lineart-validation.md) · 日本語

このページは、LineArt の幾何検証結果を JSON レポートとして保存し、そのレポートを LLM の自己修正ループへ渡すための初期仕様です。Validation Report JSON v0.1 は「何が壊れているか」を構造化し、Repair Loop v0.1 は「どの範囲を何回まで修正するか」を定義します。

## このドキュメントを使う場面

LineArt JSON を生成したあと、重なり、はみ出し、接続ミス、意図しない交差などを機械的に確認したいときに使います。

最小限の指示文は次のようにできます。

```text
LineArt JSON を検証して、修正ループ用のレポートを作ってください。
```

このように入力すると、アシスタントは LineArt JSON を検証し、問題点を Validation Report JSON として保存する流れを組みます。実装後は `lineart validate --report` が同じ形式を出力します。

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
| `summary` | error / warning / info の件数です。 |
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

## メタデータとの関係

LineArt Metadata は「何を意図しているか」を shape 側に持たせます。Validation Report は「実際に何が問題だったか」を出力します。Repair Loop は、その差分を LLM に戻して修正させます。

```text
metadata: label_01 should be inside panel_01
validation: label_01 is outside panel_01
repair: move label_01 into panel_01
```

## 更新方針

このページは、幾何検証の実装に合わせて逐次更新します。新しい issue type を追加するときは、まず `issues[].type` と `repair_hint.action` に小さく追加し、複数の検証器で共通化できる段階で schema へ昇格します。
