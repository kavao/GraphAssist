# Asset catalog

装飾 SVG/PNG の取得定義は `.rulesync/metadata/asset-catalog.jsonc` です。

## 取得

```powershell
.\scripts\setup-runtime.ps1
uv run graphassist assets fetch
uv run graphassist assets materialize --id ornament-fleur-de-lis-simple
uv run graphassist assets list --format json
```

SVG → PNG には `resvg-py`（`uv sync --extra catalog` または dev 依存）。

## ライセンス方針

| ライセンス | 採用 |
|------------|------|
| CC0 1.0 | ✅ |
| Public domain | ✅ |
| MIT / Apache-2.0 | ✅（要 copyright 明記） |
| CC-BY | △（`attribution` 必須時のみ） |
| 再配布不可・NC のみ | ❌ |

取得後の NOTICES は setup / `assets fetch` 後に `assets/catalog/NOTICES.md` に自動生成されます。

リポジトリ同梱 seed: `assets/catalog/seeds/`（`release.local` 経由で mirror）

## 索引

LLM は `samples/jobs/catalog/index.json` を参照してください。

## 参照

- manifest: `.rulesync/metadata/asset-catalog.jsonc`
- 操作: [docs/ja/image/operations.md](../../docs/ja/image/operations.md)
