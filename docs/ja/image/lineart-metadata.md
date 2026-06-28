# LineArt Metadata

[English](../../en/image/lineart-metadata.md) · 日本語

LineArt Metadata は、LineArt JSON の各 shape に役割・接続・包含・検証期待値を添えるための薄い共通情報です。レンダリングそのものを複雑にせず、後続の幾何検証や LLM への修正フィードバックが同じ情報を読めるようにします。

## このドキュメントを使う場面

LineArt JSON で図解、フローチャート、UI モックアップ、ロゴ案などを作るときに使います。

最小限の指示文は次のようにできます。

```text
LineArt JSON にメタデータを付けてください。
```

このように入力すると、アシスタントは各 shape に `role`、`tags`、`container_id`、`connects_to`、`validation` などを必要に応じて追加します。ユーザーは、生成された JSON と、将来の `lineart validate` が出す検証レポートを確認できます。

## 基本方針

初期版では、制約 DSL を作り込みすぎません。全 shape が持てる共通メタデータを薄く定義し、幾何検証はその情報を読む構成にします。

すぐ決めるフィールド:

- `id`
- `role`
- `name`
- `label`
- `tags`
- `description`
- `locked`
- `visible`

幾何検証のために薄く入れるフィールド:

- `container_id`
- `connects_to`
- `allow_overlap`
- `expected_position`
- `validation`

後回しにするもの:

- 複雑な制約式
- 自動レイアウト制約
- ブーリアン前提の幾何条件
- 優先度付き解決ルール

## 推奨フィールド

| フィールド | 型 | 用途 |
|------------|----|------|
| `id` | string | shape を一意に参照します。 |
| `role` | string | shape の役割を表します。例: `container`, `node`, `connector`, `label`, `glyph` |
| `name` | string | 人間向けの短い名前です。 |
| `label` | string | 図中に表示されるラベルや説明です。 |
| `tags` | string[] | 任意の分類です。例: `annotation`, `primary`, `debug` |
| `description` | string | 生成意図や検証の補足です。 |
| `locked` | boolean | LLM 修正時に動かしたくない shape を示します。 |
| `visible` | boolean | 表示対象かどうかを示します。 |
| `container_id` | string | この shape が入るべき親領域の `id` です。 |
| `connects_to` | object | 矢印や線が接続する対象を示します。 |
| `allow_overlap` | boolean | 他 shape との重なりを許可するかを示します。 |
| `expected_position` | object | 内側、近傍、整列などの期待位置を示します。 |
| `validation` | object | 検証条件と重要度をまとめます。 |

## role の初期案

| role | 意味 |
|------|------|
| `container` | パネル、枠、閉じた領域 |
| `node` | フローチャートや構成図の要素 |
| `connector` | 矢印、接続線 |
| `label` | 対象を説明する文字 |
| `annotation` | 補足線、注釈、強調 |
| `glyph` | FontVector 由来の文字アウトライン |
| `decorative` | 検証対象から外してよい装飾 |
| `background` | 背景や下地 |

## ラベルの例

```json
{
  "id": "label_01",
  "type": "text",
  "role": "label",
  "tags": ["annotation"],
  "container_id": "panel_01",
  "allow_overlap": false,
  "validation": {
    "expected": {
      "inside": "panel_01",
      "near": {
        "target": "icon_03",
        "max_distance": 24
      }
    },
    "severity": "error"
  }
}
```

## 接続線の例

```json
{
  "id": "arrow_01",
  "type": "path",
  "role": "connector",
  "connects_to": {
    "from": "node_a",
    "to": "node_b"
  },
  "validation": {
    "expected": {
      "touches": ["node_a", "node_b"],
      "no_intersections": true
    },
    "severity": "error"
  }
}
```

## FontVector との関係

FontVector から生成した文字アウトラインには、`role: "glyph"` を付けます。文字全体をまとめる group には `role: "label"` や `role: "decorative"` を付け、用途に応じて検証対象にします。

```json
{
  "id": "glyph_title_G",
  "type": "path",
  "role": "glyph",
  "tags": ["fontvector", "title"],
  "source_text": "GraphAssist",
  "container_id": "title_group"
}
```

## 更新方針

このページは、LineArt の実装に合わせて逐次更新します。新しい検証項目を増やすときは、まずこのメタデータに既存フィールドで表現できるかを確認し、足りない場合だけフィールドを追加します。

変更時の優先順位:

1. 既存フィールドで表現する。
2. `validation.expected` の中に小さく追加する。
3. 複数の shape type で必要になったら共通フィールドへ昇格する。
4. 複雑な制約式は後続の制約 DSL として分ける。
