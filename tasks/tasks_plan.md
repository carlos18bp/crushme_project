# Tasks Plan - CrushMe

## Active

- [ ] Merge the frame-protection deployment blocker, rotate the Django signing
  key, and complete Wave 3 production deployment/post-deploy checks.
- [ ] Land Wave 4 QA coverage and test-quality PR.
- [ ] Land Wave 5 production operations/performance PR and deployment.
- [ ] Complete Wave 6 certification and lifecycle promotion after the required
  production observation window.

## Deferred Decisions

- [ ] Re-evaluate the Argos/Stanza translation dependency chain monthly and
  only change it with real translation regressions and memory measurements.
- [ ] Isolate frontend framework majors (Flowbite, Pinia, Vite, Vue I18n, and
  Vue Router) as compatibility projects rather than bundling them into security
  maintenance.
- [ ] Split `crushme_app` only if future growth creates a concrete ownership or
  deployment boundary.

## Completed

- [x] Removed the accidental `crushme_project_staging` clone and fleet
  coordinate without touching production data or services.
- [x] Recovered disk space while preserving backups, media, Argos, Playwright,
  and the production venv.
- [x] Established a temporary Git worktree while production remains on `main`.
- [x] Landed Wave 0 foundation through PR #4.
- [x] Synchronized Codex and Claude Code, shared skills, project guidance, and
  Memory Bank through PR #5; retired Windsurf through PR #9.
- [x] Landed repository cleanup, hermetic settings, guarded fake data,
  partitioned CI, lint, and test-quality foundations through PR #6.
- [x] Added a MySQL concurrent JWT refresh regression test.
- [x] Updated patch/minor dependencies and cleared all reachable critical/high
  dependency findings.
- [x] Hardened authentication, uploads, payments, integrations, headers,
  throttles, and secret scanning.
- [x] Created fresh database/media backups and completed restore rehearsals.
- [x] Rotated the exposed production database credential, revoked the former
  account, and synchronized the protected fleet credential source.
- [x] Passed all six Wave 3 CI gates and merged PR #10.
