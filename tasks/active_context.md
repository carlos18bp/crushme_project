# Active Context - CrushMe

## Current Focus

Wave 4 is merged and deployed. Wave 5 is aligning the production runtime,
backups, restore evidence, observability, and measured capacity without
changing CrushMe's business flows.

## Current Coordinate

- Runtime checkout: `/home/ryzepeck/webapps/crushme_project` on clean `main`
  at `98adad8`.
- Authoring: temporary worktree `/home/ryzepeck/webapps/.wt/crushme-wave5-ops`
  on `ops/20082026-crushme-wave-5`.
- Domain: `crushme.com.co` and `www.crushme.com.co`.
- Data: MySQL `crushme`, Redis cache DB 1, Huey DB 2.
- Runtime services: `crushme_project.service` and `crushme-huey.service`.

## Wave State

- Wave 4 PR #12 passed all six CI jobs and its production deploy passed 14
  post-deploy checks with zero failures.
- Wave 5 baseline load had zero HTTP failures and 223 ms p95, but only 25.2%
  web-memory headroom (486.3 MiB / 650 MiB), below the 30% gate.
- Argos/ONNX/PyTorch was traced to eager URL/serializer imports in every web
  worker and Huey. The engine now loads only for actual translation work.
- Candidate health checks app/MySQL/Redis; candidate systemd and Nginx syntax
  pass static verification.
- The Wave 5 release-candidate evidence and production acceptance checklist are
  recorded in `docs/audits/2026-08-20-operations-performance.md`.
- Daily DB/media backup is moving from Huey's weekly schedule to the independent
  persistent `crushme-dbbackup.timer`.

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

## Next Gate

Finish focused regression and runtime-template validation, synchronize the
toolkit copies, pass CI, deploy with fresh snapshots/rollback files, then prove
backup restore, timer/log health, and at least 30% measured service headroom.
