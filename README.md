# GraphAssist — Image Processing CLI

English · [日本語](README.ja.md)

**GraphAssist** is a **Pillow + NumPy** image processing CLI for LLM-assisted editors such as Cursor.

It reproduces image workflows from commands and ImageJob JSON without relying on LLMs or external APIs at runtime. ImageMagick is not used.

Governance is powered by [dna_kernel](https://github.com/kavao/dna_kernel) (rulesync, audit logs, completion discipline).

## Setup

```bash
pip install -r requirements.txt
```

Or:

```bash
uv sync
```

## 30-Second Quickstart

Batch convert (resize + WebP):

```bash
uv run python tools/graphassist/graphassist.py convert samples/source/your.png generated/images/out --long-edge 1024 --format webp
```

Edit job (ImageJob JSON):

```bash
uv run python tools/graphassist/graphassist.py job samples/jobs/resize_border.json --dry-run
uv run python tools/graphassist/graphassist.py job samples/jobs/resize_border.json
```

The `generated/` directory is gitignored.

## Rulesync (dna_kernel)

After editing rule sources in `.rulesync/`:

```bash
corepack pnpm dlx rulesync generate --dry-run
corepack pnpm dlx rulesync generate
uv run python tools/kernel/user_prefs.py sync
```

## Audit Log

```bash
uv run python tools/kernel/workspace_audit_log.py append "work summary"
```

## Documentation

| Guide | Description |
|-------|-------------|
| [Docs index](docs/README.md) | Documentation entry (EN first) |
| [Quickstart (EN)](docs/en/quickstart.md) | Setup and first conversion |
| [ImageJob guide (EN)](docs/en/image/edit-job.md) | JSON edit pipeline |
| [クイックスタート (JA)](docs/ja/quickstart.md) | セットアップ |
| [ImageJob 編集 (JA)](docs/ja/image/edit-job.md) | JSON 編集 |
| [dna_kernel (EN)](docs/en/dna-kernel/README.md) | Governance |
| [Work plan](_workingspace/plans/work-plan.md) | Phase plan |

Edit docs in `docs/ja/` first, then sync `docs/en/`. See `.rulesync/rules/docs-writing.md` §0.

## Status

| Phase | Scope | Status |
|-------|-------|--------|
| 0 | dna_kernel injection | Done |
| 1 | `convert` CLI | Done |
| 2 | ImageJob + edit engine | Done |
| 3 | `composite` | Done |
| 5 | Skills | Done |
| 4 | `text` / fonts | Planned |
| 6–7 | trim, diff, inspect, sheets | Planned |

## License

MIT License — see [LICENSE](LICENSE).
