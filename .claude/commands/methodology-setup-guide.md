# Claude Compatibility Notes For CrushMe

Legacy reference only.

CrushMe now uses a Codex-native runtime:
- `AGENTS.md`
- scoped `AGENTS.md` files
- `.agents/skills/*`
- `.codex/config.toml`

Claude compatibility remains available through:
- `CLAUDE.md`
- scoped `CLAUDE.md` files
- `.claude/skills/*`
- `.claude/commands/*`

If you change a recurring workflow, update the native Codex skill first and mirror it into `.claude/` only when Claude users still need it.

Canonical docs:
- `docs/CODEX_METHODOLOGY_GUIDE.md`
- `docs/CODEX_SETUP.md`
- `docs/CODEX_MIGRATION_MAP.md`
