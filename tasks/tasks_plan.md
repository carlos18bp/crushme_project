# Tasks Plan - CrushMe

## Active

- [ ] Integrate the Base Vue `c580ea8` standards snapshot, explicit CrushMe
  profile, provenance manifest, and automated drift gate.
- [ ] Run and integrate `qa --apply` across backend, frontend-unit, and E2E
  without production data, fake data, or a staging clone.
- [ ] Deploy Wave 7 stage 1 in a separately authorized maintenance window with
  fresh backups, Torch-free daemon verification, and a production runtime
  probe.
- [ ] Observe Wave 7 stage 1 for 48 hours and one representative WooCommerce
  sync with zero translation errors, OOM events, or restart loops.
- [ ] Execute Wave 7 stage 2 only after observation: remove Argos/Torch/Stanza/
  spaCy, rebuild the canonical backend venv, delete old models, and recertify.
- [ ] Close the Wave 6 production observation after 2026-08-21 15:13:06 UTC,
  re-run the closing health/log/backup/capacity gates, and promote the fleet
  lifecycle only if the complete interval is green.

## Deferred Decisions

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
- [x] Merged frame-protection PR #11, rotated the Django signing key, deployed
  Wave 3, and passed the production post-deploy checks.
- [x] Restored the real COP/USD preference and geolocation flow instead of the
  temporary forced-COP behavior.
- [x] Added behavior tests across backend, frontend-unit, and hermetic E2E;
  validated all touched tests with zero junk-only or unvalidated flows.
- [x] Merged Wave 4 through PR #12, passed all six CI jobs, and deployed it
  with fresh database/media backups and a green production post-deploy gate.
- [x] Merged Wave 5 through PR #13, deployed dependency-aware health,
  independent backups, hardened runtime configuration, lazy Argos loading,
  and passed restore plus production headroom gates.
- [x] Merged Wave 6 dependency closure through PR #14, pinned five reachable
  secure transitives, removed 18 stale venv packages, and passed all required
  project CI jobs.
- [x] Completed the immediate Wave 6 AI, QA, vulnerability, deployment,
  restore, public-contract, service, and capacity certification without
  creating a staging coordinate.
- [x] Restricted production backup artifacts to owner-only access and added a
  regression contract so Django storage cannot override the secure systemd
  umask with permissive defaults.
- [x] Merged Wave 7 stage-1 code through PR #17 with a CPU-only/int8 isolated
  CTranslate2 daemon, explicit Argos rollback, focused tests, and six green CI
  jobs; deployment remains pending.
- [x] Merged toolkit translation-runtime PR #41 after the approved complete
  local CI substitute and propagated commit `3d8ff16` across the fleet.
