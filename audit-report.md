# Vulnerability Audit & Dependency Update Report

**Branch:** `chore/20082026-crushme-modernization`

**Date:** 2026-08-20

**Base:** `main` @ `0642bb4c598d146dad0024679c26f2546a2dea7b`

**Scope:** dependency reachability, patch/minor updates, approved security majors,
application boundaries, static analysis, and current-tree secret detection

## Verdict

**YELLOW - technical mitigations are in place; production credential rotation
and Git-history remediation remain promotion blockers.**

| Surface | Initial | Final |
|---|---:|---:|
| Frontend `npm audit` | 11: 1 critical, 8 high, 1 moderate, 1 low | 0 |
| Backend `pip-audit` | 102 findings in 19 packages | 1 mitigated finding in Stanza |
| Bandit (medium/high) | Not enforced | 0 |
| Current-tree verified secrets | Not baselined | 0 |
| Pytest advisory | Vulnerable 8.4.2 found on follow-up dev scan | Fixed in 9.1.1 |

## Frontend

### Initial Findings

`npm audit` reported vulnerable paths through `axios`, `defu`, `esbuild`,
`follow-redirects`, `form-data`, `nanoid`, `picomatch`, `postcss`, `rollup`,
`tar`, and `vite`.

### Updates Applied

Commits `ab2b6af` and `bee2028` updated the lockfile and direct pins, including:

- `axios` 1.12.2 -> 1.19.0
- Tailwind/Vite integration 4.1.13 -> 4.3.3
- `gsap` 3.13.0 -> 3.15.0
- `pinia` 3.0.3 -> 3.0.4
- `pinia-plugin-persistedstate` 4.5.0 -> 4.7.1
- `sweetalert2` 11.23.0 -> 11.26.25
- Vue 3.5.13 -> 3.5.41
- Vue Router 4.5.1 -> 4.6.4
- `@vitejs/plugin-vue` 6.0.5 -> 6.0.8

Final `npm audit`: **0 vulnerabilities**.

### Deferred Majors

| Package | Current -> Latest | Decision |
|---|---|---|
| Flowbite | 3.1.2 -> 4.0.2 | Separate UI compatibility project |
| Pinia | 3.0.4 -> 4.0.3 | Separate store/persistence migration |
| Vite | 7.3.6 -> 8.2.1 | Separate build-platform migration |
| Vue I18n | 9.14.5 -> 11.4.8 | Preserve current locale contract |
| Vue Router | 4.6.4 -> 5.2.0 | Preserve current locale-prefixed routes |

## Backend

### Initial Findings

The initial environment contained 102 findings across 19 packages. The largest
clusters were Django 5.1.5, Pillow 11.1.0, aiohttp 3.13.1, PyJWT 2.10.1,
sqlparse 0.5.3, and stale transitive packages from unused OAuth/NLP tooling.

### Updates Applied

Commits `b488d89`, `840fa2d`, and `ec28a18`:

- Upgraded Django 5.1.5 -> 5.2.17 and DRF 3.15.2 -> 3.18.0.
- Upgraded SimpleJWT 5.3.0 -> 5.5.1 and PyJWT 2.10.1 -> 2.13.0.
- Upgraded Pillow 11.1.0 -> 12.3.0 after explicit image compatibility tests.
- Upgraded Argos Translate 1.9.6 -> 1.11.0 and Torch CPU 2.9.0 -> 2.13.0.
- Upgraded requests, urllib3, sqlparse, setuptools, GeoIP, and MySQL client pins.
- Removed unreachable direct packages, including the abandoned Google OAuth
  stack; its unauthenticated orphan endpoint was removed from the application.
- Upgraded pytest 8.4.2 -> 9.1.1 for
  [GHSA-6w46-j5rx-g56g](https://github.com/advisories/GHSA-6w46-j5rx-g56g).
- Updated coverage, pytest-django, pip-audit, and pre-commit development pins.

### Remaining Stanza Advisory

`pip-audit` reports Stanza 1.10.1 for
[GHSA-v5jw-96jm-7h2c](https://github.com/advisories/GHSA-v5jw-96jm-7h2c).
Argos Translate 1.11.0 pins that exact Stanza release, so pip cannot install the
fixed Stanza >=1.12.2 without breaking dependency resolution.

The vulnerable checkpoint loader is mitigated as follows:

- Django settings reject every `ARGOS_CHUNK_TYPE` except `MINISBD` and force CPU.
- Application code never imports `stanza` or constructs `stanza.Pipeline`.
- A regression test supplies an Argos package that advertises a Stanza model
  and proves `PackageTranslation` still selects `MiniSBDSentencizer`.
- Versioned systemd units prepared for release make the application home
  read-only except for explicit media/log/backup paths.

**Owner:** dependency maintenance. Re-evaluate each month and replace the
mitigation when Argos supports Stanza >=1.12.2. Re-enabling Stanza chunking is a
release blocker.

### Audit Limitation

`pip-audit` cannot map the `torch==2.13.0+cpu` local-version wheel from the
PyTorch CPU index to a PyPI advisory record. This is an audit limitation, not a
clean bill of health; the exact pin and CPU index must be reviewed on each
monthly audit.

### Deferred Majors

Direct major upgrades for Django 6, django-cleanup 9, django-redis 7, Gunicorn
26, Huey 3, Redis 8, pytest-cov 7, Ruff's next 0.x line, setuptools 84, and
Faker 40 are deferred to isolated compatibility plans. None is required to
clear a current reachable critical/high finding.

## Application Hardening

- Payment amounts, products, variants, shipping, discounts, and gift recipients
  are rebuilt server-side before PayPal or Wompi sessions are created.
- PayPal capture amounts/currency and Wompi signatures/properties are verified
  against durable `PaymentSession` state with idempotent processing.
- JWT access/refresh lifetime is 15 minutes/7 days, refresh tokens rotate and
  blacklist, and the frontend serializes concurrent refresh attempts.
- Public auth, payment, webhook, search, write, and upload surfaces are throttled
  through the shared Redis cache.
- Uploaded images are content-verified and constrained by format, size, pixel
  count, file count, and atomic profile updates.
- The unverified Google login endpoint and public WooCommerce connection probe
  were removed/restricted.

## Static and Secret Analysis

- Bandit 1.9.4: **0 medium/high findings** over application, project, and
  quality-tool Python sources.
- detect-secrets 1.5.0: **0 verified secrets** in the current tracked tree.
- 71 reviewed false positives (field names, fixtures, UI text, explicit
  placeholders, and vendor code) are recorded in `.secrets.baseline`.
- Pre-commit now rejects new secrets and medium/high Bandit findings.

### Historical Secret Blocker

The removed `backend/setup_db.sql` contained the active production database
credential and has existed in Git history since `9bda4ba`. Deleting the file
does not revoke the credential. Before lifecycle promotion:

1. Rotate the production database credential in a maintenance window.
2. Update protected environment/credential storage atomically.
3. Restart and health-check web and Huey services.
4. Purge the secret from Git history or record explicit risk acceptance.
5. Re-scan rewritten/current history with a history-aware scanner.

No production credential or runtime was changed during this audit.

## Verification Results

| Check | Result |
|---|---|
| `npm audit` | 0 vulnerabilities |
| `npm run build` | Pass; existing chunk-size warning remains |
| `pip check` | No broken requirements |
| `python manage.py check --settings=crushme_project.settings_test` | 0 issues |
| `pytest --collect-only -q` | 37 tests collected, 0 errors |
| Security/upload slice | 9 passed |
| Payment integrity slice | 18 passed |
| Clean migration from zero | All migrations through 0020 and token blacklist pass |
| `pre-commit run` | detect-secrets and Bandit pass |
| `systemd-analyze verify` | Canonical socket/web/Huey units pass |
| Isolated Nginx parser check | Canonical site template passes |

The complete pytest suite was not executed locally, per project policy. CI and
the QA wave own partitioned complete execution.

## Rollbacks

None.
