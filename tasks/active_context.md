# Active Context - CrushMe

## Current Focus

Wave 3 dependency and security release is merged. The controlled deployment is
paused before migrations/restart while a deployment-check hotfix closes frame
embedding and rotates the prefixed Django signing key.

## Current Coordinate

- Runtime checkout: `/home/ryzepeck/webapps/crushme_project` on clean `main`
  at `93807f0`; existing processes still serve the pre-Wave-3 code until the
  guarded restart.
- Authoring: temporary worktree
  `/home/ryzepeck/webapps/.wt/crushme-frame-protection` on
  `fix/20082026-crushme-frame-protection`.
- Domain: `crushme.com.co` and `www.crushme.com.co`.
- Data: MySQL `crushme`, Redis cache DB 1, Huey DB 2.
- Runtime services: `crushme_project.service` and `crushme-huey.service`.

## Wave 3 State

- Frontend audit is clean; backend has one mitigated, unreachable Stanza
  advisory caused by the Argos Translate dependency pin.
- Payment amounts and gateway confirmations are bound to durable,
  server-calculated `PaymentSession` data.
- JWT access/refresh lifetimes are 15 minutes/7 days. Refresh rotation uses a
  database lock, and logout revokes the refresh token.
- Uploads, public endpoints, integrations, secrets, and production settings
  have explicit security boundaries.
- Fresh database and media backups restored successfully in rehearsal.
- The exposed MySQL account was replaced by `crushme_app_20260820`; the old
  account is absent and the protected fleet source matches production.

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

## Next Gate

Merge the frame-protection hotfix, rotate/synchronize `DJANGO_SECRET_KEY`,
confirm `check --deploy` has no warnings, then install exact dependencies,
apply migrations, build assets, restart services, and run post-deploy checks.
