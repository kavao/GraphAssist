# 設置・ランタイム（runtime）

[English](../en/setup/runtime.md) · 日本語

GraphAssist は **ソース（Git）** と **設置（runtime）** を分けます。

| レイヤ | パス | Git |
|--------|------|-----|
| ソース | `tools/graphassist/`（将来 `src/graphassist/`） | 管理する |
| 設置 | `runtime/` | **管理しない** |
| 出力 | `generated/` | 管理しない |

## 初回セットアップ（再実行可）

```powershell
.\scripts\setup-runtime.ps1
```

```bash
chmod +x scripts/setup-runtime.sh
./scripts/setup-runtime.sh
```

実行内容:

- `runtime/bin/`, `runtime/assets/fonts/`, `runtime/assets/weights/` を作成
- `runtime/manifest.local.json` にインストール状態を記録
- バイナリ未配置時は **ソース実行** へフォールバック

## バイナリの配置

Release から取得した `graphassist.exe` を:

```text
runtime/bin/graphassist.exe
```

に置きます（Git にはコミットしません）。

## フォント

ImageJob `text` 用フォントは **runtime** に置きます:

```text
runtime/assets/fonts/DejaVuSans.ttf
```

後方互換: `assets/fonts/` も参照可能（移行期間）。

## 将来の AI 重み

背景白抜き等の重みは枠だけ用意:

```text
runtime/assets/weights/<component-id>/
```

`.rulesync/metadata/runtime-manifest.jsonc` で `optional` / `enabled: false` として宣言。コア CLI（Pillow）は未インストールでも動作します。

## CLI の優先順位

1. 環境変数 `GRAPHASSIST_BIN`
2. `runtime/bin/graphassist.exe`（存在する場合）
3. 開発: `uv run python tools/graphassist/graphassist.py`

## 環境変数

| 変数 | 説明 |
|------|------|
| `GRAPHASSIST_RUNTIME` | runtime ルート（默认 `<project>/runtime`） |
| `GRAPHASSIST_BIN` | CLI バイナリのフルパス |

## 取り込みプロジェクト

1. GraphAssist の rulesync / ソースを注入
2. 取り込み先 `.gitignore` に `runtime/**` を追加
3. `setup-runtime` を実行
4. スキルは runtime バイナリを優先

## 設計詳細

開発者向け: [_workingspace/plans/deployment-design.md](../../../_workingspace/plans/deployment-design.md)

## 参照

- [operations.md](../image/operations.md)
- [quickstart.md](../quickstart.md)
