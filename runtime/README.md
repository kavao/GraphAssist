# runtime（Git 管理外の設置先）

このディレクトリは **実行バイナリ・フォント・AI 重み** など、Git に載せない資産の設置先です。

```text
runtime/
  bin/                 graphassist.exe 等
  assets/
    fonts/             描画用 TTF/OTF
    weights/           将来: 背景除去などのモデル
  manifest.local.json  setup-runtime 実行後に生成（インストール記録）
```

## 初回セットアップ

```powershell
.\scripts\setup-runtime.ps1
```

```bash
./scripts/setup-runtime.sh
```

**何度実行しても構いません**（更新・再取得用）。

詳細: [docs/ja/setup/runtime.md](../docs/ja/setup/runtime.md)

## 環境変数

| 変数 | 説明 |
|------|------|
| `GRAPHASSIST_RUNTIME` | runtime ルート（默认: プロジェクト直下の `runtime/`） |
| `GRAPHASSIST_BIN` | CLI バイナリを直接指定 |

## Git

`runtime/**` は `.gitignore` 対象（本 README を除く場合は `!runtime/README.md`）。
