# 将来サンプル（Phase A 以降）

ここにある JSON は **現バージョンでは実行できません**。Phase 実装後に `samples/jobs/` へ昇格してください。

## materialize → job → analyze（Phase A）

`graphassist analyze` 実装後の Batch パイプライン例:

```json
{
  "version": "1.0",
  "commands": [
    {
      "type": "assets.materialize",
      "ids": ["ui-panel-dark", "ornament-fleur-de-lis-simple"]
    },
    {
      "type": "job",
      "input_asset": "ui-panel-dark",
      "output": "generated/images/demo_catalog_card.png",
      "operations": [
        {
          "type": "composite",
          "overlay_asset": "ornament-fleur-de-lis-simple",
          "x": 200,
          "y": 280,
          "anchor": "center"
        }
      ]
    },
    {
      "type": "analyze",
      "input": "generated/images/demo_catalog_card.png",
      "output": "generated/logs/demo_catalog_card_profile.json"
    }
  ]
}
```

設計・CLI: [docs/ja/image/operations.md](../../../docs/ja/image/operations.md#analyze)
