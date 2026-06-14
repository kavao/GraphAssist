# dna_kernel overview

English · [日本語](../../ja/dna-kernel/README.md)

dna_kernel is a minimal kernel for injecting **self-evolving rule governance** into creative and development projects that use LLM harnesses (Claude Code, Cursor, and similar tools).

The root `README.md` belongs to the host project.
Detailed dna_kernel documentation lives under `docs/en/dna-kernel/` (English, default display) and `docs/ja/dna-kernel/` (Japanese editorial source).

## Why it exists

The more instructions you add for an LLM, the more contradictions accumulate—and “done” spoken in chat is not evidence of completion.
This kernel addresses both problems structurally:

- **Single source of rules**: Put conceptual definitions in one place; other instructions reference them
- **Completion constraints**: Do not treat work as done until files are written and verified
- **Append-only history**: Audit logs forbid overwrites so work facts cannot be rewritten

## What the kernel includes

```text
dna_kernel/
  README.md                  ← short entry (English, default display)
  README.ja.md               ← short entry (Japanese, editorial source)
  manifest.md                ← file roles and transplant paths
  rulesync.jsonc             ← rulesync config (targets, features)
  .rulesync/
    rules/                   ← canonical concepts and governance rules
    skills/                  ← LLM execution procedures
  docs/
    README.md                ← documentation index (EN links first)
    en/dna-kernel/           ← English (default display, translation)
    ja/dna-kernel/           ← Japanese (editorial source)
  tools/
    README.md
    kernel/
      workspace_audit_log.py
      json_weighted_pick.py
```

## README handling

In a host project, keep the root `README.md` for that project’s own introduction and usage.
Place dna_kernel docs under `docs/ja/dna-kernel/` and `docs/en/dna-kernel/` without moving or overwriting the host README.

For new projects without a README, ask whether to create one before proceeding.

## Common commands

Initial setup:

```bash
uv run python init.py
```

Regenerate rules:

```bash
corepack pnpm dlx rulesync generate --dry-run
corepack pnpm dlx rulesync generate
uv run python tools/kernel/user_prefs.py sync
```

Append an audit log entry:

```bash
uv run python tools/kernel/workspace_audit_log.py append "work summary"
```

## Further reading

- Onboarding and injection: [onboarding.md](onboarding.md)
- Governance pattern: [self-evolving-governance.md](self-evolving-governance.md)
- File manifest: [../../../manifest.md](../../../manifest.md)
