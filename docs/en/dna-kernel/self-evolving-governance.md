# Self-evolving rule governance

English · [日本語](../../ja/dna-kernel/self-evolving-governance.md)

## What this is

An operating pattern for LLM-harness projects where **rules do not bloat or contradict**, **completion stays unambiguous**, and **history is not rewritten**.

Instead of relying on “keep saying it in chat and it will be followed,” three structures constrain LLM behavior.

## Three structures

### 1. Conceptual source (Policy-as-Code)

Put only “short definitions, prohibitions, and completion conditions” in `rules/concepts.md`.
Skills and other rules link to those concepts and describe “how they apply in this task” only.

**Effect**: Contradictions have one origin; change impact stays manageable.

For the difference between conversation language (home config) and editorial sources, see [Conversation language and home config in onboarding.md](onboarding.md#conversation-language-and-home-config).

### 2. Completion constraints

“Done” means the artifact exists on disk and is confirmed by re-read or automated verification.
Even if the LLM says it wrote something, do not treat the task as complete until write and verification finish.

**Effect**: Prevents “shown in chat but not saved” and “production run before dry-run.”

### 3. Append-only audit log

After work, append to `_workingspace/log/YYYYMM.md`. Overwrites and deletions are forbidden.
Using `workspace_audit_log.py` appends via a command that cannot alter existing lines.

**Effect**: Work facts remain; disputes over “did it or not” are reduced.

## How rules evolve

1. When a new work pattern appears, add a short definition to `concepts.md`
2. Replace duplicated text in skills and instructions with links to that definition
3. Record the change in the audit log

Repeating this makes the rule set **thinner as it grows**: concept text stays in one place; each skill only references it.

## Minimal kernel (what to transplant)

| Element | File | Role |
|---------|------|------|
| Concept source | `rules/concepts.md` | Unified definitions, prohibitions, completion conditions |
| Rule authoring | `rules/rule-authoring.md` | How to add rules without duplication |
| Audit log | `tools/kernel/workspace_audit_log.py` | Append-only work record |
| Automated checks | `tools/kernel/novel_project_check.py` | Optional completion verification |

**Minimum**: Concept source plus audit log tool already helps.
Automated check tools strengthen completion constraints.

## What to put in LLM entry files

Add these two lines to `CLAUDE.md` / `AGENTS.md`:

```
- The rule source is `rules/concepts.md` (or the equivalent path after transplant). Update it first.
- After work, append to the audit log with `tools/kernel/workspace_audit_log.py`.
```

Then follow “completion conditions” and “audit log principles” in `concepts.md`.
