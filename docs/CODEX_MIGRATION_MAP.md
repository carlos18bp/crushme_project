# Codex Migration Map — Plugin Model → Native Skills

Documents the transition completed in commit `b77e4c8b` (April 2026).

## What Changed

CrushMe migrated from the **Codex plugin/marketplace model** to the **native repo skills model**. The native model is the correct Codex approach: skills live in the repo itself and require no external plugin registry.

## Before → After

### Project Config

| Before | After |
|--------|-------|
| No `.codex/config.toml` | `.codex/config.toml` with project-scoped defaults |

### Skills Runtime

| Before | After |
|--------|-------|
| `.agents/plugins/marketplace.json` | removed |
| `plugins/crushme_project-codex/.codex-plugin/plugin.json` | removed |
| `plugins/crushme_project-codex/skills/<skill>/SKILL.md` | `.agents/skills/<skill>/SKILL.md` |
| (no metadata files) | `.agents/skills/<skill>/agents/openai.yaml` |

### Documentation References

| Before | After |
|--------|-------|
| `plugins/crushme_project-codex/skills/` | `.agents/skills/` |
| `plugins/crushme_project-codex/.codex-plugin/` | `.codex/` |

### Claude Compatibility Layer

| Before | After |
|--------|-------|
| `.claude/skills/<skill>/SKILL.md` only | `.claude/skills/<skill>/SKILL.md` + `agents/openai.yaml` |
| no `debug` skill in `.claude/skills/` | `.claude/skills/debug/` added |
| verbose generic SKILL.md content | CrushMe-specific, concise SKILL.md content |
| large monolithic `CLAUDE.md` | slim compatibility mirror pointing to `AGENTS.md` |

### `AGENTS.md` / `README.md` References

| Before | After |
|--------|-------|
| `plugins/crushme_project-codex/skills/*` | `.agents/skills/*` |
| `Plugin manifest: plugins/crushme_project-codex/.codex-plugin/plugin.json` | `Project config: .codex/config.toml` |

## Skill Inventory — Canonical Names

All 17 skills now live at `.agents/skills/<name>/`:

| Skill | Category | Manual-only |
|-------|----------|-------------|
| `plan` | Planning | — |
| `implement` | Implementation | — |
| `debug` | Diagnosis | — |
| `debugme` | Diagnosis (alias) | — |
| `methodology-setup` | Maintenance | — |
| `test-quality-gate` | Testing | — |
| `backend-test-coverage` | Testing | — |
| `frontend-unit-test-coverage` | Testing | — |
| `frontend-e2e-test-coverage` | Testing | — |
| `e2e-user-flows-check` | Testing | — |
| `new-feature-checklist` | Testing | — |
| `fix-broken-tests` | Testing | — |
| `human` | Output format | — |
| `git-commit` | Operations | ✅ |
| `git-sync` | Operations | ✅ |
| `deploy-and-check` | Operations | ✅ |
| `blog-ai-weekly` | Operations | ✅ |

## Skills NOT Carried Forward

These existed only in the old plugin and were intentionally dropped:

- `backend-test-coverage-goal` — merged into `backend-test-coverage`
- `frontend-unit-test-coverage-goal` — merged into `frontend-unit-test-coverage`
- `frontend-e2e-test-coverage-goal` — merged into `frontend-e2e-test-coverage`
- `not-forget-fake-data-and-test` — merged into `new-feature-checklist`

## Files Removed

```
.agents/plugins/marketplace.json
```

## Files Added

```
.codex/config.toml
.agents/skills/*/SKILL.md          (17 skills)
.agents/skills/*/agents/openai.yaml (17 files)
.claude/skills/debug/SKILL.md
.claude/skills/debug/agents/openai.yaml
.claude/skills/*/agents/openai.yaml (15 new files — sync with .agents/)
```
