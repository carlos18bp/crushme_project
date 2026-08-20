# Active Context - CrushMe

## Current Focus

Modernization Waves 4-6 (August 2026): finish behavior coverage, validate the
integration PR, deploy isolated staging after DNS, and certify promotion.

## Recent Changes

- Registered lifecycle `modernizing` and an isolated staging work coordinate.
- Synchronized Claude 35/35, Codex 35/35, and Windsurf 32/32 skills and agents.
- Removed 306 generated, unsafe, redundant, or orphaned tracked files.
- Updated Django/Vue dependencies and reduced npm advisories from 11 to 0 and
  backend advisories from 102 findings to one mitigated Stanza advisory.
- Hardened payment integrity, JWT, uploads, throttles, secrets, systemd, and
  Nginx without changing public business contracts.
- Added hermetic pytest/Jest/Playwright settings, guarded deterministic data,
  MySQL compatibility CI, ESLint, and the strict test-quality gate.
- Added fail-fast staging settings and versioned env/systemd/Nginx artifacts;
  none have been installed.
- Canonical QA now reports 4 covered, 16 partial, 36 missing, 0 junk-only, and
  0 unvalidated flows across 56 declared outcomes.

## Active Decisions

- Preserve the single HTTP client, function-based DRF views, locale routes,
  mixed Pinia styles, WooCommerce mirror, offline translation, PayPal, and Wompi.
- Production remains on `main`; modernization work stays isolated until all
  promotion gates pass.
- Pytest and local E2E use guarded SQLite; CI separately proves MySQL migration
  compatibility, while runtime and staging remain MySQL.
- Playwright uses one worker because the deterministic scenario shares one
  guarded SQLite database.
- Argos keeps CTranslate2/PyTorch; MiniSBD makes the pinned Stanza loader
  unreachable until upstream supports a fixed Stanza release.
- The staging registry remains `dev_only` and has no server coordinate until
  DNS and deployment are explicitly authorized.

## Next Gates

1. Close the 36 missing flows and the remaining negative-case gap.
2. Push the session branch, open the PR to `release/crushme-modernization`, and
   require complete partitioned CI without merging.
3. Rotate the exposed production DB credential and remediate Git history.
4. Provision `crushme.projectapp.co`, deploy isolated staging, issue TLS, and
   complete restore, observability, performance, and headroom validation.
5. Run Wave 6 read-only certification and the production observation window
   before lifecycle promotion.
