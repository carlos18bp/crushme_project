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

- **venv is `venv_cpu/`**, not `venv/` — exists because PyTorch is installed (but unused in code).
- **Systemd quirk**: the Gunicorn unit is `gunicorn.service`, not `crushme_project.service`. Socket is `gunicorn.socket`.
- **Huey immediate mode** in dev: tasks run synchronously, no Redis/worker needed.
- **Vite dev proxy**: `/api/` and `/media/` proxied to localhost:8000. Both servers must run.

## Testing

- Backend test suite structure exists (`crushme_app/tests/{views,models,serializers,services,commands}/`) but has no test files yet.
- Frontend has 1 unit test file (`src/utils/__tests__/priceHelper.test.js`). E2E directory has no specs.
- Pre-commit hook: `test-quality-gate` runs on staged test files with `--semantic-rules strict`.

## Tech Debt

- **PyTorch, stanza, ctranslate2** in requirements.txt but unused — 650M memory limit exists because of PyTorch footprint.
- **No test coverage** — test infrastructure is in place but no tests written yet.
