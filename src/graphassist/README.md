# GraphAssist 画像 CLI

配置: `src/graphassist/`（OnGen の `tools/sound/` と同型。肥大化に備え CLI・engine・schema をここに集約）

エントリ: `graphassist.py`（Pillow のみ。ImageMagick は使用しない）

## クイックスタート

```bash
# プロジェクトルートから
uv run graphassist convert samples/source/input.png generated/images/out --long-edge 1024 --format webp
```

## モジュール

| パス | 役割 |
|------|------|
| `graphassist.py` | CLI エントリ |
| `convert_cmd.py` | `convert` サブコマンド |
| `engine/` | Pillow 編集エンジン |
| `schema/` | ImageJob（Phase 2） |
| `job_runner.py` | JSON 実行（Phase 2） |

## サブコマンド

| コマンド | 状態 |
|----------|------|
| `convert` | Phase 1 |
| `job` | Phase 2（ImageJob） |
