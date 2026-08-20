# Active Context - CrushMe

## Current Focus

Wave 3 is deployed and healthy. Wave 4 is preparing its QA release candidate:
behavior tests, executable flow coverage, test quality, and the restoration of
the real currency-detection path.

## Current Coordinate

- Runtime checkout: `/home/ryzepeck/webapps/crushme_project` on clean `main`
  at `68f5d1b`.
- Authoring: temporary worktree `/home/ryzepeck/webapps/.wt/crushme-wave4-qa`
  on `qa/20082026-crushme-wave-4`.
- Domain: `crushme.com.co` and `www.crushme.com.co`.
- Data: MySQL `crushme`, Redis cache DB 1, Huey DB 2.
- Runtime services: `crushme_project.service` and `crushme-huey.service`.

## Wave State

- Wave 3 passed deployment with 14 post-deploy controls, zero failures, and
  production health/assets/payment configuration checks returning HTTP 200.
- The Wave 4 quality gate reports zero findings across all test layers.
- Focused verification has 23 backend tests passing, one MySQL-only concurrency
  test skipped locally, 15 frontend-unit tests passing, and 21 Playwright tests
  passing against isolated SQLite E2E data.
- The flow registry has 56 real browser flows: 4 covered, 16 partial, 36
  missing, zero junk-only, and zero unvalidated.
- Currency initialization now respects a valid browser preference or uses the
  backend geolocation recommendation; the temporary forced-COP path is gone.

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

## Next Gate

Run the CI-parity quality verifier over every touched test, pass the six CI
jobs, merge the Wave 4 PR, and confirm the production checkout remains healthy
before starting Wave 5 operations and performance work.
