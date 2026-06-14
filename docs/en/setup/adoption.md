# Adopting GraphAssist in another project (source injection)

English · [日本語](../../ja/setup/adoption.md)

This guide explains how to add GraphAssist to an existing repository so **LLMs can drive ImageJob / Batch JSON** and Python executes it safely.

**Default:** use **pattern B (source injection)**. The CLI alone can run, but **without rulesync (rules and ga-* skills), you lose most of the “LLM writes JSON, Python runs it” value**. Plan to ship **source + rulesync + samples** together.

---

## Which pattern to use

| Pattern | What you ship | When |
|---------|-----------------|------|
| **B. Source injection (recommended)** | `src/graphassist/` + `.rulesync/` + `samples/` in the same repo | **The normal case** — add LLM-assisted image work to a game, tool, or asset repo |
| A. Runtime only | Binary and fonts via `setup-runtime` | Source lives elsewhere. **Pattern B still runs setup-runtime** for fonts/binary |
| C. dna_kernel only | Governance (`tools/kernel/`, concepts) | No image CLI needed. See [dna_kernel onboarding](../dna-kernel/onboarding.md) |

The rest of this page is **pattern B**.

---

## Why rulesync belongs in the bundle

| Piece | Role |
|-------|------|
| `src/graphassist/` | Pillow engine and CLI (validated execution) |
| `.rulesync/rules/graphassist.md` | LLM constraints, paths, skill routing |
| `.rulesync/skills/ga-*` | Canonical workflows for ImageJob, Batch, mosaic, analyze, catalog |
| `samples/jobs/` | Repeatable Job / Batch examples |

Without rulesync, adopters only hunt CLI flags manually — the **safe JSON pipeline** does not engage.

---

## What to copy (checklist)

Place these under the **injection root** (a user-specified subdirectory in a monorepo — do not expand to the whole monorepo without approval). Per-file mapping: [manifest.md](../../../manifest.md).

### Required (pattern B)

| Path | Contents |
|------|----------|
| `src/graphassist/` | Entire CLI, engine, schema tree |
| `.rulesync/rules/graphassist.md` | GraphAssist LLM rule |
| `.rulesync/skills/ga-*` | All image skills (`ga-image-job-runner`, `ga-batch-runner`, `ga-mosaic-art`, `ga-image-processing`, `ga-image-analysis`, `ga-catalog-assets`) |
| `.rulesync/metadata/` | `graphassist.json`, `runtime-manifest.jsonc`, `asset-catalog.jsonc` |
| `rulesync.jsonc` | **Merge** with existing config if present (below) |
| `scripts/setup-runtime.ps1`, `scripts/setup-runtime.sh`, `scripts/runtime_fetch.py` | Runtime bootstrap |
| `samples/jobs/` | Job / Batch samples |
| `samples/mosaic/` | CharGrid samples (when using mosaic) |
| `samples/jobs/catalog/` | Catalog index (when using catalog assets) |
| `assets/fonts/README.md` | Font documentation |
| `assets/fonts/DejaVuSans.ttf`, `assets/fonts/PixelMplus12-Regular.ttf` | **Git-bundled fonts** (basic tests work right after clone) |
| `runtime/README.md` | Runtime directory readme |
| `pyproject.toml` | Copy as-is for greenfield; **merge** deps and scripts into an existing project (below) |

### dna_kernel governance (recommended if missing)

| Path | Contents |
|------|----------|
| `.rulesync/rules/concepts.md` etc. | Completion rules, audit log, testing |
| `.rulesync/skills/workspace-audit-log/` etc. | Operational skills |
| `tools/kernel/` | Audit log, user-locale, etc. |
| `_workingspace/` | Audit/plans layout (structure in Git; contents ignored) |

Details: [dna_kernel onboarding](../dna-kernel/onboarding.md)

### Optional

| Path | Contents |
|------|----------|
| `tests/` | When running regression tests in adoptee CI |
| `docs/ja/`, `docs/en/` | When you want docs in-repo (**GitHub upstream is often enough** — below) |
| `samples/source/` | Small sample inputs only; large assets stay in the adoptee project |

### Do not copy

| Path | Reason |
|------|--------|
| `runtime/bin/*.exe`, `runtime/assets/**` | Fetched by `setup-runtime` (not in Git) |
| `generated/**` | Output directory (gitignore) |
| `.cursor/`, `.claude/`, `AGENTS.md`, etc. | rulesync **generated** configs (canonical: `.rulesync/`) |
| `dist/`, `build/` | Local build artifacts |
| Promo images for GraphAssist README | Not needed in adoptee repos |

---

## Integrating into an existing project

1. **Pick the injection root** — honor a user-specified directory; do not auto-expand to monorepo or Git root.
2. **Get approval** — show planned adds/merges (`.rulesync/`, `pyproject.toml`, `.gitignore`).
3. **Copy files or add a submodule** — same layout as the checklist. Submodules still follow **pattern B paths**.
4. **Merge `pyproject.toml`** — at minimum:

```toml
dependencies = [
  "pillow>=10.0",
  "numpy>=2.0",
  "pydantic>=2.0",
]
# [project.scripts]
# graphassist = "graphassist.graphassist:main"
```

Adjust hatch `packages` / `extraPaths` to match the adoptee layout.

5. **Append `.gitignore`** — `generated/**`, `runtime/**`, rulesync outputs, bundled font exceptions, etc. Reference: [`.gitignore`](../../../.gitignore) in the GraphAssist repo.
6. **If `.rulesync/` already exists** — merge `ga-*` skills and `graphassist.md`. Extend `rulesync.jsonc` `targets`; ensure `features` includes `"rules"` and `"skills"`.
7. **Install deps** — `uv sync` (or the adoptee Python workflow).
8. **rulesync generate** — `corepack pnpm dlx rulesync generate --dry-run` → approve → `generate`. Then `uv run python tools/kernel/user_prefs.py sync` when dna_kernel is present.
9. **Runtime setup** — run `setup-runtime` per [runtime.md](runtime.md).
10. **Verify** — below.

Do **not** overwrite the adoptee `README.md`. Link to `docs/` or add a single line (see [project-onboarding](../../../.rulesync/skills/project-onboarding/SKILL.md)).

---

## Verification after adoption

```bash
uv run graphassist --version
uv run graphassist job samples/jobs/resize_border.json --dry-run
uv run graphassist run samples/jobs/birds_on_trunk_pipeline.json --dry-run
```

Optional (if you copied `tests/`):

```bash
uv run python -m unittest discover -s tests -q
```

---

## Using GitHub as upstream reference

After adoption, treat the **upstream repo** as the living source for docs, samples, and design.

| Reference | Use |
|-----------|-----|
| [github.com/kavao/GraphAssist](https://github.com/kavao/GraphAssist) | Canonical source, issues, releases |
| [docs/ on GitHub](https://github.com/kavao/GraphAssist/tree/main/docs) | Quickstart, CLI, ImageJob, Batch (JA / EN) |
| [manifest.md](https://github.com/kavao/GraphAssist/blob/main/manifest.md) | File roles and transplant paths |
| [Releases](https://github.com/kavao/GraphAssist/releases) | CLI binary for `runtime/bin` (also used by setup-runtime in pattern B) |

You often **do not need to copy all of `docs/`** — bookmark upstream docs instead. If you edit docs in the adoptee repo, follow the bilingual rule: **`docs/ja/` first, then sync `docs/en/`** ([docs-writing](../../../.rulesync/rules/docs-writing.md)).

---

## See also

- [Runtime setup](runtime.md) — binary, fonts, environment variables
- [Quickstart](../quickstart.md)
- [dna_kernel onboarding](../dna-kernel/onboarding.md)
- Developer design notes: [_workingspace/plans/deployment-design.md](../../../_workingspace/plans/deployment-design.md) (local plans)
