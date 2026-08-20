# Vulnerability Audit & Dependency Update Report

**Branch:** `chore/20082026-crushme-wave-3-security`

**Date:** 2026-08-20

**Base:** `main` @ `053f3375d49e`

**Scope:** dependency reachability, patch/minor updates, approved security
majors, application boundaries, static analysis, backup restore, and credential
rotation

## Verdict

**GREEN - no unmitigated critical/high finding remains; CI, merge, signing-key
rotation, and the controlled production deployment passed.**

| Surface | Initial | Current |
|---|---:|---:|
| Frontend `npm audit` | 11: 1 critical, 8 high, 1 moderate, 1 low | 0 |
| Backend `pip-audit` | 101 findings in 18 packages | 1 mitigated Stanza finding |
| Bandit medium/high | Not enforced | 0 |
| Current-tree verified secrets | Not baselined | 0 |
| Production DB credential | Exposed and active | Rotated; former user revoked |

## Frontend

### Updates Applied

Commit `aae96ec` updated patch/minor dependencies without `--force`, including:

- Axios 1.12.2 to 1.19.0.
- Tailwind/Vite integration 4.1.13 to 4.3.3.
- GSAP 3.13.0 to 3.15.0.
- Pinia 3.0.3 to 3.0.4.
- `pinia-plugin-persistedstate` 4.5.0 to 4.7.1.
- SweetAlert2 11.23.0 to 11.26.25.
- Vue 3.5.13 to 3.5.41.
- Vue Router 4.5.1 to 4.6.4.
- Vite to 7.3.6 and `@vitejs/plugin-vue` to 6.0.8.

Final `npm audit`: **0 vulnerabilities**.

### Deferred Majors

| Package | Current to latest | Decision |
|---|---|---|
| Flowbite | 3.1.2 to 4.0.2 | Isolate as a UI compatibility project |
| Pinia | 3.0.4 to 4.0.3 | Isolate with persisted-store migration |
| Vite | 7.3.6 to 8.2.1 | Isolate as a build-platform migration |
| Vue I18n | 9.14.5 to 11.4.8 | Preserve the current locale contract |
| Vue Router | 4.6.4 to 5.2.0 | Preserve locale-prefixed routes |

## Backend

### Updates Applied

Commit `437d2b4` updated direct pins and removed unreachable direct packages:

- Django 5.1.5 to 5.2.17 and DRF 3.15.2 to 3.18.0.
- SimpleJWT 5.3.0 to 5.5.1 and PyJWT 2.10.1 to 2.13.0.
- Pillow 11.1.0 to 12.3.0.
- Argos Translate 1.9.6 to 1.11.0 and Torch CPU to 2.13.0.
- Requests, urllib3, sqlparse, setuptools, GeoIP, MySQL client, Redis,
  django-dbbackup, django-cors-headers, django-silk, and Huey patch/minor pins.
- Pytest 9.1.1 plus updated coverage, pytest-django, pip-audit, pre-commit,
  and Ruff development pins.

Final `pip-audit`: **1 finding in 1 package**.

### Remaining Stanza Advisory

`pip-audit` reports Stanza 1.10.1 as `PYSEC-2026-3075`. Argos Translate
1.11.0 pins that exact release, while the fixed Stanza release is 1.12.2 or
newer. Installing the fixed release would violate Argos dependency resolution.

The vulnerable model-loading path is not reachable:

- Django settings reject every `ARGOS_CHUNK_TYPE` except `MINISBD` and reject
  every device except CPU.
- Application code never imports Stanza or creates `stanza.Pipeline`.
- A regression test presents a package with a Stanza model path and proves
  Argos 1.11 still instantiates `MiniSBDSentencizer`.
- Re-enabling Stanza chunking is a release blocker.

This mitigation was executed locally against the real Argos 1.11 and MiniSBD
packages. The dependency must be re-evaluated monthly until Argos accepts a
fixed Stanza version.

### Audit Limitation

`pip-audit` cannot map the `torch==2.13.0+cpu` local-version wheel from the
PyTorch CPU index to a PyPI advisory record. The exact CPU pin and index remain
part of every monthly review; this limitation is not treated as a clean bill of
health.

### Deferred Majors

Django 6, django-cleanup 9, django-redis 7, Gunicorn 26, Huey 3, Redis 8,
Faker 40, pytest-cov 7, and other direct majors are deferred to isolated
compatibility work. None is needed to clear a reachable critical/high finding.

## Application Hardening

Commits `b677149`, `6f89e62`, and `7a4bd5e` add compatible security controls:

- Payment products, variants, shipping, discounts, currency, and totals are
  rebuilt server-side before PayPal or Wompi sessions are created.
- PayPal captures and Wompi signatures/properties are checked against durable
  `PaymentSession` state before an order is processed.
- Public payment configuration comes from the backend; gateway identifiers are
  no longer compiled into frontend configuration.
- JWT lifetime is 15 minutes/7 days, rotation is blacklisted and serialized by
  database row lock, and logout revokes the refresh token.
- The frontend shares one in-flight refresh and cannot persist a late refresh
  response after logout or account replacement.
- Public auth, payment, webhook, search, write, and upload surfaces are
  throttled through named DRF policies.
- Uploaded images are content-verified and constrained by format, byte size,
  pixel count, request file count, and atomic profile updates.
- The unverified Google login endpoint was removed and the WooCommerce probe is
  admin-only.
- Production requires explicit HTTPS/live integration settings and secure
  cookies, HSTS, referrer policy, and popup-compatible COOP headers.

## Static And Secret Analysis

- Bandit 1.9.4 found **0 medium/high issues** across 26,979 Python source lines.
- detect-secrets 1.5.0 found **0 new/current secrets** outside the reviewed
  baseline.
- The baseline contains 71 reviewed false positives such as fixture values,
  field names, placeholders, documentation examples, and vendored code.
- Pre-commit rejects new secrets, medium/high Bandit findings, and test-quality
  regressions.

## Data Safety And Credential Rotation

Before rotating production access, fresh recovery artifacts were created:

- Database: `default-srv571894-2026-08-20-123100.dump.gz`.
- Media: `srv571894-2026-08-20-123110.tar.gz`.
- Toolkit restore rehearsal: 1/1 weekly DB, 1/1 weekly media, and 1/1 fresh
  daily DB restored successfully; temporary databases were dropped.
- Fresh media rehearsal: 38/38 files extracted with identical inventory hash
  and byte count; the temporary extraction was removed.

The exposed `crushme_user` account was replaced atomically by
`crushme_app_20260820`:

1. The replacement user received only the existing `crushme.*` grants.
2. Direct database connectivity was verified before changing runtime files.
3. Runtime and protected credential source were updated with mode 600.
4. Web and Huey restarted and the public production health endpoint passed.
5. The former MySQL user was dropped and verified absent.
6. The protected source was committed in toolkit commit `52d9898`.

The rollback environment is retained with mode 600 under
`/var/backups/crushme_project/credential-rotation-20260820T123648Z` until the
observation window closes.

### Historical Secret Risk Acceptance

The removed `backend/setup_db.sql` still exists in Git history. The credential
it contained is now revoked and its MySQL user no longer exists. Rewriting
shared history would invalidate active modernization branches and provide no
additional revocation benefit. The project therefore explicitly accepts the
historical record while requiring history-aware scanners to classify this
specific credential as **revoked**, never active. Any future active secret in
history still requires immediate rotation and separate remediation.

## Verification Results

| Check | Result |
|---|---|
| `npm audit` | 0 vulnerabilities |
| `npm run build` | Pass; existing chunk-size warnings only |
| `pip-audit -r backend/requirements.txt` | 1 mitigated Stanza finding |
| Django system check | 0 issues |
| Migration drift | No changes detected through migration 0020 |
| Authentication security slice | 5 passed, MySQL concurrency case deferred to CI |
| Upload validation slice | 4 passed |
| Argos/MiniSBD mitigation | 1 passed against Argos 1.11 |
| Payment integrity slice | 16 passed |
| Test quality gate | 100/100 for 11 new security tests |
| detect-secrets | Pass |
| Bandit medium/high | Pass, 0 findings |
| Backup restore rehearsal | Pass |
| Credential cutover health | Web active, Huey active, public health OK |
| Six partitioned CI jobs | Pass on PR #10 and PR #11 |
| Production deployment | Pass; migrations applied and services restarted |
| Canonical post-deploy check | 14 pass, 0 fail |

The complete test suite was not run locally, per project policy. CI owns the
partitioned complete run and the production-engine concurrent JWT test.

## Rollbacks

No dependency or application rollback was required. MySQL rejected the first
generated password before any user or environment mutation; the corrected
candidate then completed the guarded cutover successfully.

## Deployment Closure

- PR #10 and frame-protection hotfix PR #11 are merged into `main`.
- Production runs commit `68f5d1b`; migrations 0019/0020 and token blacklist
  migrations are applied.
- Exact backend/frontend dependencies, build, and static collection passed.
- `crushme_project.service` and `crushme-huey.service` restarted cleanly.
- Public health, compiled assets, payment configuration contracts, and hardened
  HTTP headers return the expected responses.
- The rollback artifacts remain retained until the final observation window
  closes.
