# Tasks Plan - CrushMe

## Active

- [ ] Land Wave 0 foundation PR.
- [ ] Land Wave 1 AI ecosystem and methodology PR.
- [ ] Land Wave 2 repository and test-platform PR.
- [ ] Land Wave 3 dependency/security PR and controlled deployment.
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
