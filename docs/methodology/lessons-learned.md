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

- Backend product tests currently contain one file with 10 fake-data guard cases; six historical `test_*.py` scripts outside the suite are not quality-gate coverage.
- Frontend has 1 unit test file (`src/utils/__tests__/priceHelper.test.js`). E2E directory has no specs.
- The Jest config only discovers `frontend/test/`; the existing unit file must be moved before it counts.
- Pre-commit hook: `test-quality-gate` runs on staged test files with `--semantic-rules strict`.

## Tech Debt

- **Translation dependency chain is real** — Argos uses CTranslate2; Stanza pulls PyTorch, while MiniSBD is forced to keep vulnerable Stanza model loading unreachable.
- **Memory headroom is unproven** — validate the 650M limit with a representative translation sync in staging.
- **Minimal test coverage** — destructive command guards are covered, but core product behavior and all E2E flows remain uncovered.
- **Exposed database credential** — a bootstrap SQL file matched production credentials and remains in Git history; rotation and history remediation block lifecycle promotion.
