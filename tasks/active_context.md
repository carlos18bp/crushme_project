# Active Context - CrushMe

## Current Focus

Close QA across backend, frontend-unit, and E2E after the Base Vue standards
convergence. A focused product-card i18n regression found during hermetic E2E is
being fixed before QA resumes. Production deployment remains a separate future
operation.

## Current Coordinate

- Runtime checkout: `/home/ryzepeck/webapps/crushme_project` on clean `main`;
  repository head `8ea34f2`, deployed application release `1d476d8`.
- Authoring isolation: fresh temporary Git worktrees only; no database, domain,
  environment file, socket, service, or permanent staging coordinate.
- Domain: `crushme.com.co` and `www.crushme.com.co`.
- Data: MySQL `crushme`, Redis cache DB 1, Huey DB 2.
- Runtime services: `crushme_project.service` and `crushme-huey.service`.
- Candidate service: `crushme-translation.service`; it is not installed in
  production until Wave 7 stage 1 deploys.

## Wave State

- Wave 7 stage 1 merged through PR #17 as `3217c5f` after 23 focused backend
  tests, QA verification, dependency audits, reproducible model hashes, a 156
  MiB Torch-free daemon proof, and all six application CI jobs.
- Toolkit translation-runtime PR #41 merged as `3d8ff16` after the approved
  complete local CI substitute and propagated to all reachable fleet hosts.
- Base Vue standards source is fixed at `c580ea8`; canonical files, a CrushMe
  profile, and a hash gate merged through PR #18 as `8ea34f2`.
- Wave 5 PR #13 is deployed. Health, daily backup, journald observability,
  restore, and capacity gates passed; web-memory headroom improved from 25.2%
  to 81.1% without raising the 650 MiB limit.
- Wave 6 PR #14 is deployed. Five secure reachable transitives are pinned and
  18 stale historical packages were removed from the production venv.
- Frontend audit is clean. Backend audits report only the tested, documented
  Stanza mitigation required by Argos; `pip check` passes.
- Public application/MySQL/Redis health, English translation, PayPal/Wompi
  config, service journals, timer, restore 1/1/1, and a 32-request capacity
  probe passed after the final restart.
- The final web/Huey restart completed at 2026-08-20 15:13:06 UTC. The earliest
  valid observation close is 2026-08-21 15:13:06 UTC.
- The host full audit is yellow only because of two unrelated Aviation service
  override warnings; all CrushMe state and restore checks are green.

## Active Decisions

- Release one PR per wave directly to `main`.
- Keep only the active Codex and Claude Code ecosystems; Windsurf was retired
  fleet-wide through PR #9.
- Preserve function-based DRF views, the single frontend HTTP client, and all
  established business flows.
- Keep Stanza chunking disabled by forcing Argos MiniSBD on CPU; any attempt to
  re-enable Stanza blocks release until the dependency advisory is fixed.
- Accept the revoked credential in shared Git history instead of rewriting
  history; current-tree and new-secret scanning remain mandatory.
- Never run QA, E2E, or fake-data commands against production data.
- Keep missing flows explicit. Wave 4 does not convert uncovered behavior into
  exemptions or draft credit.
- Keep the 650M/450M service limits; earn headroom by avoiding unnecessary
  heavyweight imports rather than masking usage with larger limits.
- Isolate CTranslate2 in `backend/venv_translation`, hardcode CPU/int8 and one
  thread, and reject any runtime that can import Torch.
- Keep Argos rollback explicit during stage 1; never auto-fallback from a dead
  translation socket into a constrained Gunicorn/Huey process.
- Keep backup availability independent from Huey and preserve the weekly fleet
  snapshot as a second mechanism.
- Keep fleet lifecycle `modernizing` and retain Wave 3 through Wave 6 rollback
  artifacts until the full observation interval passes.

## Next Gate

Merge the focused product-card stock-label fix, then complete and integrate
`qa --apply` for backend, frontend-unit, and E2E. No deployment is part of
either gate. Wave 7 deployment later requires fresh recovery artifacts and
starts a new 48-hour translation observation; lifecycle remains `modernizing`
until all observation gates close.
