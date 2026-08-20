# Active Context - CrushMe

## Current Focus

Waves 5 and 6 are merged and deployed. Immediate certification is complete;
the only modernization gate still open is the real 24-hour production
observation before lifecycle promotion.

## Current Coordinate

- Runtime checkout: `/home/ryzepeck/webapps/crushme_project` on clean `main`;
  deployed application release `1d476d8`.
- Authoring isolation: fresh temporary Git worktrees only; no database, domain,
  environment file, socket, service, or permanent staging coordinate.
- Domain: `crushme.com.co` and `www.crushme.com.co`.
- Data: MySQL `crushme`, Redis cache DB 1, Huey DB 2.
- Runtime services: `crushme_project.service` and `crushme-huey.service`.

## Wave State

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
- Keep backup availability independent from Huey and preserve the weekly fleet
  snapshot as a second mechanism.
- Keep fleet lifecycle `modernizing` and retain Wave 3 through Wave 6 rollback
  artifacts until the full observation interval passes.

## Next Gate

After 2026-08-21 15:13:06 UTC, inspect the complete service journals, public
health/contracts, newest daily backup and timer result, capacity, Git/runtime
state, vulnerability status, and AI drift. Promote lifecycle from
`modernizing` to `active` only if every closing check is green.
