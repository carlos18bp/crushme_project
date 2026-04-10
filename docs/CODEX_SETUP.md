# Codex Setup — CrushMe

> Comprehensive guide: `docs/CODEX_METHODOLOGY_GUIDE.md`

## Runtime Surfaces

| Surface | Path | Role |
|---------|------|------|
| Always-on instructions | `AGENTS.md`, `backend/AGENTS.md`, `frontend/AGENTS.md` | Canonical repo rules |
| Native skills | `.agents/skills/<skill>/SKILL.md` | Reusable workflows |
| Skill metadata | `.agents/skills/<skill>/agents/openai.yaml` | Display name + invocation policy |
| Project config | `.codex/config.toml` | Codex project defaults |
| Memory bank | `docs/methodology/*`, `tasks/*` | Long-lived project context |
| Compatibility (read-only) | `CLAUDE.md`, `.claude/`, `.windsurf/` | Mixed-tool team support only |

## `.codex/config.toml` Fields

```toml
approval_policy        = "never"           # never auto-approve; always confirm
sandbox_mode           = "workspace-write" # Codex can write to repo files
model                  = "gpt-5.4"
model_reasoning_effort = "high"
project_doc_max_bytes  = 65536
web_search             = "live"
```

## Activation

1. Open Codex at `/home/ryzepeck/webapps/crushme_project`.
2. Confirm these paths exist:
   - `.agents/skills/` (17 skills)
   - `.codex/config.toml`
3. Restart Codex if skills were added or renamed during the current session.

## Smoke Tests

```
Use $plan to outline a small change in this repo.
Use $debug to diagnose this sample error in read-only mode.
Use $implement to add a single new field to an existing model.
Use $methodology-setup to refresh memory files after a structural change.
```

## Manual-Only Skills

These skills require explicit invocation — they never run automatically:

| Skill | Guard |
|-------|-------|
| `deploy-and-check` | `disable-model-invocation: true` + `allow_implicit_invocation: false` |
| `git-commit` | same |
| `git-sync` | same |
| `blog-ai-weekly` | same |

## Notes

- `debug` is the canonical diagnosis workflow.
- `debugme` is a legacy alias kept for compatibility with older prompts.
- `human` skill: responds in conversational Spanish instead of a technical breakdown.
- This repo uses native skills (`.agents/skills/`) — the old plugin registry (`.agents/plugins/`) was removed.
