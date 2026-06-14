# 画像処理ガイド

[English](../en/image/README.md) · 日本語

GraphAssist は **繰り返しの、創造性のない画像作業をツールに任せる** ことをコンセプトに、CLI と ImageJob / Batch でパイプラインを再実行可能にします（[overview.md](../../../_workingspace/plans/overview.md#コンセプト)）。

| ガイド | 内容 |
|--------|------|
| [quickstart.md](../quickstart.md) | セットアップと最初の変換 |
| [convert.md](convert.md) | 一括 convert |
| [operations.md](operations.md) | 全サブコマンド・operations |
| [edit-job.md](edit-job.md) | ImageJob 編集 |
| [mosaic.md](mosaic.md) | CharGrid（MosaicArt）相互コンバート |
| [batch.md](batch.md) | Batch manifest（1 JSON・複数命令） |

実装正本: `src/graphassist/`（Pillow のみ）
