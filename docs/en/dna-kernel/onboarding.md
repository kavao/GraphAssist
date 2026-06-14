# dna_kernel onboarding and injection

English · [日本語](../../ja/dna-kernel/onboarding.md)

dna_kernel supports three work modes:

| Mode | Purpose | README handling |
|------|---------|-----------------|
| New project setup | Bootstrap a location without overview or README yet | Ask before creating a project README |
| Existing project injection | Add dna_kernel to an existing project | Do not touch the existing README; put dna_kernel docs under `docs/ja/dna-kernel/` and `docs/en/dna-kernel/` |
| DNA_KERNEL development | Modify the dna_kernel package itself | Skip onboarding questions; edit directly |

## Existing project injection

Preserving the existing layout takes priority.

When the user specifies an injection root directory, treat that directory as the root.
Do not automatically expand to a monorepo parent or Git root.

Example:

```text
K:\projects\my-app\packages\discord-bot\
```

If that path is given, place the following under `packages/discord-bot/`:

```text
.rulesync/
rulesync.jsonc
docs/ja/dna-kernel/
docs/en/dna-kernel/
tools/kernel/
_workingspace/
```

Principles:

- Do not overwrite the existing `README.md`
- Do not copy `images/title.png` into the host project; it is for the dna_kernel repository README title only
- Review `.gitignore`, `pyproject.toml`, `tools/`, and `docs/` before appending
- Put detailed dna_kernel docs in `docs/ja/dna-kernel/` (source) and sync `docs/en/dna-kernel/` (translation)
- Add `.rulesync/`, `rulesync.jsonc`, and `tools/kernel/` as canonical sources and working tools
- Ignore rulesync outputs (`.claude/`, `.cursor/`, `.codex/`, `.agents/`, `.kilo/`, `AGENTS.md`, `CLAUDE.md`)

Recommended flow:

1. Check for existing README, docs, tools, `.rulesync/`, and `rulesync.jsonc`
2. Present the planned changes and obtain approval
3. Place docs in `docs/ja/dna-kernel/` and sync English under `docs/en/dna-kernel/`
4. Add or merge `.rulesync/` and `rulesync.jsonc`
5. Add required tools under `tools/kernel/`
6. Update `.gitignore` for rulesync outputs and `_workingspace/`
7. Run `corepack pnpm dlx rulesync generate --dry-run` and review the output
8. After approval, run `corepack pnpm dlx rulesync generate`
9. Run `uv run python tools/kernel/user_prefs.py sync` to regenerate conversation-language rules
10. If needed, ask whether to create `overview.md` and gather project purpose, deliverables, and constraints

## New project setup

First check whether `overview.md` exists.
If not, ask before creating it, then confirm rulesync and uv setup after approval.

Basic commands:

```bash
corepack enable
uv run python init.py
corepack pnpm dlx rulesync generate --dry-run
corepack pnpm dlx rulesync generate
uv run python tools/kernel/user_prefs.py sync
```

Running `corepack pnpm dlx rulesync` alone currently shows help only.
Use the `generate` subcommand to produce outputs. Run `user_prefs.py sync` **after** `generate`.

## Conversation language and home config

**Conversation language** (chat with the LLM) is separate from **docs editorial source** (`docs/ja/` then sync to `docs/en/`). Even when chatting in Japanese, follow the bilingual docs policy in `docs-writing`.

| Setting | Location | In git |
|---------|----------|--------|
| Conversation language and authoring defaults | `~/.config/dna-kernel/config.toml` | No (per machine) |
| Project override | `.dna-kernel.local.toml` | No (gitignore) |
| API keys, secrets | `.env` | No |

Create the home config template:

```bash
uv run python tools/kernel/user_prefs.py init-config
```

Check resolved conversation language:

```bash
uv run python tools/kernel/user_prefs.py show conversation.language
```

Before writing files, declare placement with the `content-placement` skill (use together with `user-locale`).

## .gitignore example

```gitignore
# rulesync outputs
# Canonical sources live in rulesync.jsonc and .rulesync/; exclude generated tool configs
.claude/
.cursor/
.codex/
.kilo/
.agents/
AGENTS.md
CLAUDE.md

# workspace (local working files)
_workingspace/**
!_workingspace/**/
!_workingspace/**/.gitkeep
_backup/
_old/

# user-locale: project-local override
.dna-kernel.local.toml
```
