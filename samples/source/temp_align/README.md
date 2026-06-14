# temp_align（ローカル入力）

`temp_align.json` / `temp_align_webp.json` 用の**入力置き場**です。

- PNG は **Git に含めません**（`.gitignore`）
- 実行前に `shot01.png` … `shot04.png` をここに置く（名前は Job JSON に合わせる）
- 元素材は `_workingspace/_temp/` などローカル作業領域に置いてよい

## 実行

```bash
uv run graphassist run samples/jobs/temp_align.json
uv run graphassist run samples/jobs/temp_align_webp.json
```

出力は `generated/images/temp_align/` および `generated/images/temp_align_webp/` です。
