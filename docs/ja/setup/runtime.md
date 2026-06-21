# 設置・ランタイム（runtime）

[English](../en/setup/runtime.md) · 日本語

GraphAssist は **ソース（Git）** と **設置（runtime）** を分けます。

| レイヤ | パス | Git |
|--------|------|-----|
| ソース | `src/graphassist/` | 管理する |
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
- GitHub Releases から CLI バイナリを取得（ネットワーク必須）
- **フォントを取得** — Git 同梱済み（DejaVu / PixelMplus12）を runtime へコピーし、追加で日本語（Noto / 美咲）、英語（Inter / Roboto / Source Sans 3）、Windows では Meiryo をシステムからコピー（`assets/fonts/` にもミラー、`NOTICES.md` 自動生成）
- `runtime/manifest.local.json` にインストール状態を記録
- 取得失敗時は **ソース実行** へフォールバック（バイナリ）、フォント optional はスキップ可

強制再取得:

```powershell
.\scripts\setup-runtime.ps1 -Force
```

## バイナリの配置

通常は `setup-runtime` が [GitHub Releases](https://github.com/kavao/GraphAssist/releases) から取得します。手動配置する場合:

```text
runtime/bin/graphassist.exe
```

に置きます（Git にはコミットしません）。

## フォント

**Git 同梱（最小）:** `assets/fonts/DejaVuSans.ttf` と `PixelMplus12-Regular.ttf` は clone 直後から利用可能です（birds デモ・基本テスト向け）。

`setup-runtime` が ImageJob `text` 用の追加フォントを **`runtime/assets/fonts/`** に配置し、`assets/fonts/` へミラーします。

| フォント | 用途 | 取得 |
|----------|------|------|
| `DejaVuSans.ttf` | Latin 等 | **Git 同梱** / setup |
| `PixelMplus12-Regular.ttf` | ピクセル風日本語 | **Git 同梱** / setup |
| `NotoSansJP-Regular.otf` | 日本語（推奨） | ダウンロード（OFL） |
| `misaki_gothic.ttf` | 8×8 ドット日本語 | ダウンロード |
| `InterVariable.ttf` | 英語 UI | ダウンロード（OFL） |
| `Roboto-Regular.ttf` | 英語 UI | ダウンロード（Apache 2.0） |
| `SourceSans3-Regular.ttf` | 英語 UI | ダウンロード（OFL） |
| `Meiryo.ttc` | Windows 向け optional | システムフォントからコピーのみ |

著作権・ライセンス: [assets/fonts/README.md](../../../assets/fonts/README.md) および setup 後の `assets/fonts/NOTICES.md`

JSON では従来どおり `assets/fonts/...` を指定します。`resolve_font` が runtime を優先参照します。

## 素材カタログ（CC0 / Public domain）

`setup-runtime` が `.rulesync/metadata/asset-catalog.jsonc` の SVG を取得し、`samples/source/catalog/` に SVG + PNG を配置します。

```powershell
.\scripts\setup-runtime.ps1
# カタログのみ
uv run python scripts/runtime_fetch.py --catalog-only
# 特定 id のみ
uv run graphassist assets fetch --id ornament-fleur-de-lis-simple
```

SVG の PNG 化には **resvg-py** が必要です（dev 依存に含む。本番のみなら `uv sync --extra catalog`）。

索引: [samples/jobs/catalog/index.json](../../../samples/jobs/catalog/index.json)  
著作権: setup 後の `assets/catalog/NOTICES.md`

## 将来の AI 重み

背景白抜き等の重みは枠だけ用意:

```text
runtime/assets/weights/<component-id>/
```

`.rulesync/metadata/runtime-manifest.jsonc` で `optional` / `enabled: false` として宣言。コア CLI（Pillow）は未インストールでも動作します。

## CLI の優先順位

1. 環境変数 `GRAPHASSIST_BIN`
2. `runtime/bin/graphassist.exe`（存在する場合）
3. 開発: `uv run graphassist`

## 環境変数

| 変数 | 説明 |
|------|------|
| `GRAPHASSIST_RUNTIME` | runtime ルート（デフォルト: `<project>/runtime`） |
| `GRAPHASSIST_BIN` | CLI バイナリのフルパス |

## 取り込みプロジェクト

**原則はパターン B（ソース注入）** — `src/graphassist/` + rulesync + samples を同リポジトリに載せます。CLI だけでは LLM 連携の価値が出にくいため、**rulesync（`graphassist.md` + ga-* スキル）をセットで取り込んでください**。

詳細チェックリスト・統合手順・GitHub 参照: **[他プロジェクトへの取り込み](adoption.md)**

取り込み後の共通ステップ:

1. 取り込み先 `.gitignore` に `runtime/**`, `generated/**`, rulesync 生成物を追加
2. `uv sync` → `corepack pnpm dlx rulesync generate`（dna_kernel 導入時）
3. 本ページの **初回セットアップ**（`setup-runtime`）を実行
4. スキルは `runtime/bin` → `uv run graphassist` の優先順位で CLI を参照

## 設計詳細

runtime の設計判断（ソース vs バイナリ・フォント方針）は本ページおよび [adoption.md](adoption.md) を参照。詳細なローカル設計メモは `_workingspace/plans/`（Git 外・リンク不可）に置く。

## 参照

- [operations.md](../image/operations.md)
- [quickstart.md](../quickstart.md)
