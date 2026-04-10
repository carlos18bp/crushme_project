# CrushMe — Claude Compatibility Guide

## Source Of Truth
- The canonical repo guidance is maintained in the Codex-native surfaces: `AGENTS.md`, `backend/AGENTS.md`, `frontend/AGENTS.md`, `.agents/skills/*`, `.codex/config.toml`.
- This `CLAUDE.md` file is a compatibility mirror for mixed-tool teams and should stay aligned with the Codex guidance.
- There is **no `docs/methodology/` Memory Bank yet** — long-lived context lives in top-level `docs/` markdown standards files.

## Project Overview
- **What it is**: a bilingual (ES/EN) e-commerce + wishlist-sharing platform built around the "crush" concept (verified profiles can receive gifted wishlists from others).
- **Stack**: Django 5.1.5 + DRF (backend) / Vue 3.5 + Vite 7 + Pinia (frontend) / MySQL 8 / Redis / Huey / **PyTorch CPU venv** (`backend/venv_cpu/`, currently unused in code).
- **Single Django app**: `crushme_app` — ~25 models, 15+ view modules, real service layer.
- **Production path**: `/home/ryzepeck/webapps/crushme_project`.
- **Domain**: `crushme.com.co`.
- **Services**: `gunicorn.service` (the systemd unit is named `gunicorn`, not `crushme_project`), `crushme-huey.service`. Socket: `/run/gunicorn.sock`.
- **Memory limit**: 650M (because of PyTorch's footprint).
- The frontend Vite build emits to `backend/static/frontend/` and is served by Django.

## Architecture Invariants
- **Backend views are 100% function-based** with `@api_view`. View modules are split per resource (auth, product, cart, order, wishlist, paypal, wompi, etc.). Do not convert to CBV/`APIView`/`ViewSets`.
- **Service layer is real**: business logic lives in `crushme_app/services/` (translation, woocommerce sync, paypal, wompi, email). Views call services. Do not inline business rules into views.
- **Translation is offline + cached**: `argostranslate` translates ES↔EN at WooCommerce sync time and caches the result in a `TranslatedContent` model. Frontend reads localized fields directly.
- **Dual auth**:
  - `/api/auth/...` uses **JWT via SimpleJWT** (30d access, 60d refresh, rotation + blacklist).
  - `/admin/` uses **session + CSRF**.
- **Dual frontend HTTP clients**:
  - Content/admin flows → `frontend/src/services/request_http.js` (Axios with CSRF).
  - Platform/auth (JWT) flows → `frontend/src/composables/usePlatformApi.js` (Axios with JWT interceptors).
  - **Never mix the two clients in the same feature.**
- **Pinia stores use Options API** (`{ state, getters, actions }`) and `pinia-plugin-persistedstate` for localStorage persistence. Do not rewrite to `setup()` style.
- **Custom `User` model**: email-as-username, with crush verification fields (`is_crush`, `crush_verification_status`, `crush_verified_at`).
- **GuestUser model** supports anonymous checkout via session.
- **Two payment gateways**: PayPal (international) and Wompi (Colombian, COP). Each has a webhook endpoint that updates `Order.status`.
- **WooCommerce mirror**: products are pulled from a remote WooCommerce store and mirrored locally with translated content.
- **Conditional Silk**: `django-silk` is gated by `ENABLE_SILK=True`. Off by default.

## Working Rules
- Prefer existing project patterns over generic framework advice.
- The venv is at `backend/venv_cpu/`, not `backend/venv/`. Activate accordingly.
- The systemd unit is `gunicorn.service` (not `crushme_project.service`) — keep this in mind for restart scripts.
- Do not change old migrations; add new migrations when schema changes are required.
- Keep security basics intact: validated serializer inputs, ORM-first queries, escaped rendering, secure cookies, no secrets in code.
- Do not hardcode user-facing strings — bilingual content is either in `vue-i18n` locale files or already translated server-side via `argostranslate`.
- Do not edit files inside `backend/static/frontend/` — they are Vite build artifacts.

## Commands
- Backend tests: `cd backend && source venv_cpu/bin/activate && pytest crushme_app/tests/path/to/test_file.py -v`
- Backend dev server: `cd backend && source venv_cpu/bin/activate && python manage.py runserver`
- Frontend dev server: `cd frontend && npm run dev` (Vite, default :5173)
- Frontend unit tests (Jest): `cd frontend && npm test -- path/to/file.spec.js`
- Frontend E2E (Playwright): `cd frontend && npx playwright test e2e/path/to/spec.js`
- Frontend build: `cd frontend && npm run build`

## Testing Constraints
- Never run the full test suite.
- Maximum 20 tests per batch and 3 test commands per cycle.
- Run only the smallest backend, frontend unit, or E2E slice needed for the changed behavior.

## Memory Bank
- **Not yet established.** No `docs/methodology/` and no `tasks/` directory exist.
- Long-lived project context lives in top-level `docs/` standards files (`DJANGO_VUE_ARCHITECTURE_STANDARD.md`, `BACKEND_AND_FRONTEND_COVERAGE_REPORT_STANDARD.md`, `E2E_FLOW_COVERAGE_REPORT_STANDARD.md`, `GLOBAL_RULES_GUIDELINES.md`, `TESTING_QUALITY_STANDARDS.md`, `CACHE_BUSTING_SETUP.md`).
- If you need to bootstrap a Memory Bank, use the `methodology-setup` skill.
