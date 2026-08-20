# Lessons Learned — CrushMe

Patterns, preferences, and project intelligence discovered during development.

## Architecture

- **Single app (`crushme_app`)** works for now but is large. Models, views, serializers, services, and tests all live here.
- **Service layer is real**: business logic in `crushme_app/services/`, views are thin FBV wrappers.
- **WooCommerce mirror**: products synced from a remote store, translated offline, cached in `TranslatedContent`.
- **Dual payment gateways**: PayPal (USD) + Wompi (COP), each with webhook endpoints.
- **Custom User model**: email-as-username, crush verification workflow.

## Frontend

- **Single HTTP client** (`request_http.js`): sends CSRF + JWT + language + currency headers. No separate platform API client.
- **Mixed store styles**: most Pinia stores use setup/Composition API; i18nStore, reviewStore, contactStore use Options API. Match existing style when editing.
- **Locale routing**: `/en/...` and `/es/...` prefixes via vue-router. Active locale from `i18nStore`.
- **Product content is pre-translated**: don't translate client-side. UI strings go through `vue-i18n`.

## Development

- **venv is `venv_cpu/`**, not `venv/` — Argos' Stanza dependency requires the PyTorch CPU build.
- **Production service**: Gunicorn runs as `crushme_project.service` and binds `/run/gunicorn.sock`; Huey runs as `crushme-huey.service`.
- **Huey immediate mode** in dev: tasks run synchronously, no Redis/worker needed.
- **Vite dev proxy**: `/api/` and `/media/` proxied to localhost:8000. Both servers must run.

## Testing

- The executable inventory is 18 backend behavior files / 49 test functions,
  7 frontend-unit files / 18 tests, and 11 E2E specs / 21 tests. Historical
  scripts outside `crushme_app/tests` do not count as behavior coverage.
- Literal Playwright tags are required on each test: `@flow`, `@role`, and
  `@outcome`. The static auditor does not resolve imported tag constants.
- The E2E scenario uses guarded file-backed SQLite and one worker. Increasing
  workers requires per-worker data isolation, not just a config change.
- A worktree without `backend/venv_cpu` must pass `E2E_PYTHON` explicitly;
  CI already does this.
- Cold Vite lazy routes require condition-based navigation synchronization.
  Use `waitForURL` before the click and bounded action timeouts, never sleeps,
  retries, `force`, or weakened assertions.
- User-content fixtures should be unambiguous in the requested locale unless
  translation is the behavior under test; otherwise auto-detection can invoke
  real offline Argos and contaminate timing.
- Mutating E2E tests must clean up their own records and assert cleanup success.
- Pre-commit runs strict semantic quality, ESLint, secret detection, and Bandit.
- Canonical QA is yellow at 4 covered, 16 partial, and 36 missing flows, with
  no junk-only or unvalidated flow.

## Tech Debt

- **Translation dependency chain is real** — Argos uses CTranslate2; Stanza pulls PyTorch, while MiniSBD is forced to keep vulnerable Stanza model loading unreachable.
- **Memory headroom is unproven** - validate the 650M limit with a representative translation sync in staging.
- **Flow coverage remains incomplete** - 36 of 56 declared flows are missing and one negative-case gap remains.
- **Permanent staging is blocked** - `crushme.projectapp.co` does not resolve, so TLS, restore, profiling, and sandbox smoke checks are not certified.
- **Exposed database credential** - a bootstrap SQL file matched production credentials and remains in Git history; rotation and history remediation block lifecycle promotion.
