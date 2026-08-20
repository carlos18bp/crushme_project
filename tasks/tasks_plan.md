# Tasks Plan - CrushMe

## Active

- [ ] Land Wave 2 repository and test-platform PR.
- [ ] Land Wave 3 dependency/security PR and controlled deployment.
- [ ] Add the concurrent JWT refresh regression test with Wave 3 auth
  hardening; its implementation does not exist on the Wave 2 baseline.
- [ ] Land Wave 4 QA PR.
- [ ] Land Wave 5 production operations/performance PR and deployment.
- [ ] Complete Wave 6 certification and lifecycle promotion.

## Deferred Decisions

- [ ] Re-evaluate the translation dependency chain only with measured production
  reachability and memory evidence.
- [ ] Split `crushme_app` only if future growth creates a concrete ownership or
  deployment boundary; the modernization does not introduce that refactor.

## Completed

- [x] Removed the accidental `crushme_project_staging` clone and fleet
  coordinate without touching production data or services.
- [x] Recovered disk space while preserving backups, media, Argos, Playwright,
  and the production venv.
- [x] Established a temporary Git worktree while production remains on `main`.
- [x] Landed Wave 0 foundation through PR #4.
- [x] Synchronized Codex, Claude Code, Windsurf, shared skills, project guidance,
  and Memory Bank in Wave 1.
