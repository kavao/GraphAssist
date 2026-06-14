# Fonts

ImageJob `text` は `assets/fonts/` 以下のパスを指定します。実体は **`setup-runtime` が `runtime/assets/fonts/` に取得**し、`assets/fonts/` にミラーします。

## 初回セットアップ

```powershell
.\scripts\setup-runtime.ps1
```

```bash
./scripts/setup-runtime.sh
```

取得後、`assets/fonts/NOTICES.md` に著作権・ライセンス一覧が自動生成されます。

## 取得フォント一覧

| ID | ファイル | 用途 | 取得 | ライセンス |
|----|----------|------|------|------------|
| `noto-sans-jp` | `NotoSansJP-Regular.otf` | 日本語（推奨・約 16 MB） | DL | SIL OFL 1.1 |
| `misaki-gothic` | `misaki_gothic.ttf` | 8×8 ドット日本語 | DL | 美咲フォント License（無保証・自由利用） |
| `pixelmplus12` | `PixelMplus12-Regular.ttf` | ピクセル風日本語 | DL | M+ FONT LICENSE |
| `dejavu-sans` | `DejaVuSans.ttf` | Latin 等（基本） | DL | DejaVu / Bitstream Vera License |
| `inter` | `InterVariable.ttf` | 英語 UI（可変フォント） | DL | SIL OFL 1.1 |
| `roboto` | `Roboto-Regular.ttf` | 英語 UI | DL | Apache 2.0 |
| `source-sans-3` | `SourceSans3-Regular.ttf` | 英語 UI | DL | SIL OFL 1.1 |
| `meiryo` | `Meiryo.ttc` | Windows 向け optional | システムコピーのみ | 再配布不可（Microsoft 所有） |

定義の正本: `.rulesync/metadata/runtime-manifest.jsonc`（`copyright` / `license_name` / `source_url` を含む）

## 著作権・ライセンス

各フォントの著作権表示とライセンス全文（取得可能なもの）は setup 時に次へ保存されます。

- `assets/fonts/NOTICES.md` — 一覧（自動生成）
- `assets/fonts/*-LICENSE` — ライセンス全文（DL 可能なもの）

### 日本語

| フォント | 著作権 | 出典 |
|----------|--------|------|
| Noto Sans JP | Copyright (c) 2014-2021 Adobe, Google, and contributors | [notofonts/noto-cjk](https://github.com/notofonts/noto-cjk) |
| 美咲ゴシック | Copyright (C) 2002-2021 Num Kadoma | [littlelimit.net/misaki.htm](https://littlelimit.net/misaki.htm) |
| PixelMplus12 | Copyright (C) 2013 itouhiro; Copyright (C) 2002-2013 M+ FONTS PROJECT | [itouhiro/PixelMplus](https://github.com/itouhiro/PixelMplus) |
| Meiryo | Copyright (c) Microsoft Corporation | Windows システムフォント（**再配布不可**・optional） |

### 英語

| フォント | 著作権 | 出典 |
|----------|--------|------|
| DejaVu Sans | Copyright (c) 2003 Bitstream, Inc. / Dejavu Fonts Team | [dejavu-fonts.github.io](https://dejavu-fonts.github.io/) |
| Inter | Copyright (c) 2016-2020 The Inter Project Authors | [rsms.me/inter](https://rsms.me/inter/) |
| Roboto | Copyright 2011 Google Inc. | [googlefonts/roboto](https://github.com/googlefonts/roboto) |
| Source Sans 3 | Copyright 2010-2022 Adobe | [adobe-fonts/source-sans](https://github.com/adobe-fonts/source-sans) |

## JSON 例

横書き（英語 UI）:

```json
{"type": "text", "content": "Hello", "font": "assets/fonts/InterVariable.ttf", "size": 48, "color": "white", "x": 10, "y": 10}
```

縦書き（日本語・ゴシック）:

```json
{"type": "text", "content": "残業エクステンド", "font": "assets/fonts/NotoSansJP-Regular.otf", "size": 48, "color": "#f0e040", "x": 320, "y": 48, "direction": "vertical", "line_spacing": 1.2}
```

ピクセル風:

```json
{"type": "text", "content": "STAGE 1", "font": "assets/fonts/PixelMplus12-Regular.ttf", "size": 16, "color": "white", "x": 8, "y": 8}
```

ドット風（美咲）:

```json
{"type": "text", "content": "残業", "font": "assets/fonts/misaki_gothic.ttf", "size": 16, "color": "white", "x": 8, "y": 8}
```

デモ Job: `samples/jobs/demo_zangyo_extend.json`

フォントバイナリ（`.ttf` / `.otf` / `.ttc`）と `*-LICENSE` は `.gitignore` 対象です。`NOTICES.md` は setup 時に再生成されます。
