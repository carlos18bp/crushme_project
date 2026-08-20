# Active Context - CrushMe

## Current Focus

Keep the merged Base Vue and three-layer QA baseline stable while Wave 7 waits
for a separately authorized production deployment and observation window. The
product-card i18n regression found by hermetic E2E is fixed.

## Current Coordinate

- Runtime checkout: `/home/ryzepeck/webapps/crushme_project` on clean `main`;
  deployed application release `1d476d8`.
- Authoring isolation: fresh temporary Git worktrees only; no database, domain,
  environment file, socket, service, or permanent staging coordinate.
- Domain: `crushme.com.co` and `www.crushme.com.co`.
- Data: MySQL `crushme`, Redis cache DB 1, Huey DB 2.
- Runtime services: `gunicorn.service`, `gunicorn.socket`, and
  `crushme-huey.service`.
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
- Product-card stock actions now use the canonical localized label; PR #19
  merged as `2dec475` after seven green CI checks and a component regression.
- Three-layer QA PR #20 merged as `8f173b3` after seven green PR checks and a
  green post-merge run covering backend, frontend unit/build, hermetic E2E, and
  MySQL compatibility.
- The refreshed registry records 64 real browser flows and 176 outcomes. The
  QA wave added five live E2E behaviors; all ten tests in the touched specs pass
  against isolated SQLite with zero junk-only or unvalidated flows.
- The deterministic audit remains yellow by design: 40 flows are still missing
  complete browser coverage and one negative outcome class remains open. No
  gap was converted into an exemption or draft credit.
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

Obtain separate maintenance authorization for the Wave 7 stage-1 production
deployment, create fresh recovery artifacts, validate the Torch-free daemon,
run one representative WooCommerce sync, and complete the 48-hour observation.
Lifecycle remains `modernizing` until all observation gates close.
