# tools（GraphAssist）

自己発展型ルールガバナンスを「実働」させるためのツールです。

## kernel/（dna_kernel コア）

プロジェクトの種類に関わらず使えるツールです。

- **追記ログ（auditability）**
  - `kernel/workspace_audit_log.py`
  - 追記先: `_workingspace/log/YYYYMM.md`, `_workingspace/diary/YYYYMM.md`
  - 依存: なし（標準ライブラリのみ）
- **重み付き乱数選択（weighted-pick）**
  - `kernel/json_weighted_pick.py`
  - 依存: なし（標準ライブラリのみ）

## graphassist/（GraphAssist 画像処理）

- `graphassist/graphassist.py` — CLI エントリ（`convert`, `job` 等）
- `graphassist/convert_cmd.py`, `graphassist/engine/` — 内部モジュール（CLI から利用）
