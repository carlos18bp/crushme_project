# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
CrushMe is a bilingual (ES/EN) e-commerce + wishlist-sharing platform where verified "crush" profiles can receive gifted wishlists. Built with Django 5.1.5 + DRF (backend) and Vue 3.5 + Vite 7 + Pinia (frontend), backed by MySQL 8, Redis, and Huey for async tasks. Production domain: `crushme.com.co`.

## Commands
```bash
# Backend (always activate venv first — it's venv_cpu, not venv)
cd backend && source venv_cpu/bin/activate
python manage.py runserver                                    # Dev server
pytest crushme_app/tests/path/to/test_file.py -v             # Run specific tests
pytest crushme_app/tests/path/to/test_file.py::test_name -v  # Single test
python manage.py makemigrations crushme_app && python manage.py migrate
python manage.py create_fake_data                             # Seed dev data
python manage.py delete_fake_data --confirm                   # Remove seeded data
python manage.py sync_woocommerce                             # Pull products from WooCommerce

# Frontend
cd frontend && npm run dev          # Vite dev server (:5173, proxies /api/ and /media/ to :8000)
cd frontend && npm run build        # Build → ../backend/static/frontend/
cd frontend && npm test -- path/to/file.spec.js          # Jest unit test
cd frontend && npx playwright test e2e/path/to/spec.js   # Playwright E2E
# Use E2E_REUSE_SERVER=1 if Vite dev server is already running
```

## Testing Constraints
- Never run the full test suite (backend, frontend unit, or E2E).
- Maximum 20 tests per batch and 3 test commands per cycle.
- Run only the smallest slice needed for the changed behavior.
- Backend fixtures in `backend/conftest.py`: `api_client`, `user`, `admin_user`, `authenticated_client`, `admin_client`.
- Pre-commit hook: `test-quality-gate` runs on staged test files with `--semantic-rules strict`.

## Architecture

### Backend — Single Django App (`crushme_app`)
- **Views are 100% function-based** with `@api_view`, split per resource (`auth_views.py`, `product_views.py`, `cart_views.py`, `order_views.py`, `wishlist_views.py`, `paypal_order_views.py`, `wompi_order_views.py`, etc.). Do not convert to CBV/`APIView`/`ViewSets`.
- **Service layer is real**: business logic lives in `crushme_app/services/` (email, translation, woocommerce sync, paypal, wompi). Views are thin wrappers that call services — do not inline business rules into views.
- **Dual auth**: `/api/auth/...` uses JWT via SimpleJWT (30d access, 60d refresh, rotation + blacklist). `/admin/` uses session + CSRF.
- **Offline translation**: `argostranslate` translates ES↔EN at WooCommerce sync time and caches results in a `TranslatedContent` model. No real-time machine translation.
- **Custom `User` model**: email-as-username, crush verification fields (`is_crush`, `crush_verification_status`). `GuestUser` model supports anonymous checkout via session.
- **Two payment gateways**: PayPal (USD, international) and Wompi (COP, Colombian). Each has webhook endpoints that update `Order.status`.
- **WooCommerce mirror**: products are pulled from a remote WooCommerce store and mirrored locally with translated content.
- **Conditional Silk**: `django-silk` profiling is gated by `ENABLE_SILK=True` env var. Off by default.
- **Currency middleware**: custom middleware reads `x-currency` header (COP/USD) from frontend requests.

### Frontend — Vue 3 SPA
- **Pinia stores use mixed API styles** with `pinia-plugin-persistedstate`. Most stores (auth, cart, crush, currency, order, payment, product, profile, wishlist) use the **setup/Composition API** (`defineStore('name', () => { ... })`). A few (i18n, review, contact) use the **Options API**. Stores live in `src/stores/modules/`.
- **Single HTTP client**: all API requests go through `src/services/request_http.js` — an Axios wrapper that sends both `X-CSRFToken` and `Authorization: Bearer` headers, injects `Accept-Language` and `X-Currency`, and handles automatic JWT refresh on 401.
- **Locale routing**: vue-router uses `/en/...` and `/es/...` prefixes. Active locale comes from `i18nStore`.
- **Bilingual content**: product text is already translated server-side — the frontend just reads localized fields. UI strings (buttons, labels) go through `vue-i18n` locale files in `src/locales/`.
- **Currency**: `currencyStore` tracks COP/USD; `request_http.js` injects `x-currency` header on every request.
- Build output goes to `backend/static/frontend/` — do not edit files there directly.

### Environment & Settings
- Base settings: `backend/crushme_project/settings.py`. Environment-specific overrides auto-import from `settings_dev.py` or `settings_prod.py` based on `DJANGO_ENV` env var (default: `development`).
- Pytest uses `DJANGO_SETTINGS_MODULE=crushme_project.settings` (from `pytest.ini`).
- Redis db 1 = Django cache, Redis db 2 = Huey task queue.
- Systemd units: `gunicorn.service` (not `crushme_project.service`) + `crushme-huey.service`. Socket: `/run/gunicorn.sock`.
- Memory limit: 650M (PyTorch is in requirements but unused in code).

### Deployment Flow
1. `git pull origin main`
2. `pip install -r requirements.txt` + `python manage.py migrate`
3. `cd frontend && npm install && npm run build`
4. `python manage.py collectstatic --noinput`
5. `sudo systemctl restart gunicorn crushme-huey`

### Email Templates
Bilingual MJML source templates in `emails/`, rendered HTML in `backend/email_templates/{en,es}/`. Email sending is handled by `crushme_app/services/email_service.py`.

## Working Rules
- The venv is at `backend/venv_cpu/`, not `backend/venv/`.
- Do not change old migrations; add new migrations when schema changes are required.
- Do not hardcode user-facing strings — use `vue-i18n` locale files or server-side translation.
- Do not edit files inside `backend/static/frontend/` — they are Vite build artifacts.
- Prefer existing project patterns over generic framework advice.
<!-- session-start-protocol:begin -->
## Session Start Protocol

Al inicio de **cada sesión y antes de editar archivos**, debes invocar la skill `git-sync` para este repo. Razón: el operador trabaja desde múltiples máquinas y procesos automatizados (cron, CI) pueden haber commiteado cambios que tu copia local no tiene; editar sobre una versión desactualizada genera conflictos o trabajo duplicado.

**Flujo:**
1. Un hook `SessionStart` (definido en `.claude/settings.json`) ejecuta `git fetch + git status` read-only y te inyecta el estado de este repo como contexto.
2. Si el reporte indica `behind > 0` o `dirty > 0`, **invoca la skill `git-sync`** antes de hacer cualquier cambio. `git-sync` hace rebase contra el parent branch y, si hay conflictos, te guía interactivamente por la resolución.
3. Si el reporte indica `behind=0 ahead=0 dirty=0`, el repo ya está sincronizado y puedes proceder.

**Importante:** Nunca uses `git pull --force`, `git reset --hard` ni stash automático para "resolver" el sync — usa siempre la skill `git-sync`, que es segura y reproducible.
<!-- session-start-protocol:end -->
<!-- e2e-user-flows-protocol:begin -->
## E2E User Flows Check

Cuando termines de implementar un cambio que afecte un **flujo de usuario en el frontend** — por ejemplo:
- Crear o editar un formulario (agregar/quitar campos)
- Nueva ruta, página o vista accesible al usuario
- Cambios en flujos de autenticación, checkout, onboarding, búsqueda, perfil
- Modificaciones a `docs/USER_FLOW_MAP.md` o `frontend/e2e/flow-definitions.json`

…debes invocar la skill `e2e-user-flows-check` como **paso final** antes de reportar la implementación como completa. Esa skill audita la cobertura E2E del flujo modificado y reporta brechas/riesgos.

**Por qué:** los flujos de usuario en frontend cambian las assumptions de los tests E2E. Sin auditoría, un campo eliminado deja tests "verdes" pero inválidos, y un form nuevo queda sin cobertura.

**No aplica para:** correcciones aisladas que no cambian el flujo (typos, refactors internos, estilos puros, dependency bumps), ni cambios solo en backend que no alteren UX.

**Recordatorio automático:** un hook `Stop` revisa al cierre del turno si hay cambios uncommitted bajo `frontend/src/`, `frontend/app/`, etc., y te lo inyecta como contexto. El hook es un recordatorio, no bloqueante — la regla aplica igual aunque el hook no dispare.
<!-- e2e-user-flows-protocol:end -->
<!-- git-branch-protocol:begin -->
## Reglas de trabajo con Git: ramas y commits

**Nunca hagas commits directamente sobre `main` o `master`.** Estas ramas están protegidas y los pushes serán rechazados por GitHub. Antes de cualquier `git commit`, sigue este protocolo:

### 1. Verificar la rama actual

Antes de cualquier operación de escritura (add, commit, etc.), ejecuta:

```bash
git rev-parse --abbrev-ref HEAD
```

### 2. Si la rama actual es `main` o `master`

**No pidas permiso, crea automáticamente una nueva rama** y comunícaselo al usuario con un mensaje corto del tipo: "Estás en `main`, voy a crear la rama `<nombre>` antes de commitear." Luego procede.

### 3. Formato obligatorio del nombre de rama

`<prefijo>/<DDMMYYYY>-<descripcion-corta>`

- **`<prefijo>`** según el tipo de cambio:
  - `feat` — nueva funcionalidad
  - `fix` — corrección de bug
  - `docs` — cambios en documentación
  - `refactor` — refactorización sin cambio funcional
  - `test` — añadir o modificar tests
  - `chore` — mantenimiento (dependencias, configs)
  - `style` — formato/estilo, sin cambio de lógica
  - `perf` — mejoras de rendimiento
  - `ci` — cambios en workflows o pipelines
  - `hotfix` — corrección urgente en producción

- **`<DDMMYYYY>`** debe ser la fecha actual del sistema obtenida con `date +%d%m%Y`. Nunca la asumas ni la inventes.

- **`<descripcion-corta>`** en kebab-case, máximo 5 palabras, en inglés o español según el idioma del proyecto.

### 4. Ejemplos de nombres válidos

- `feat/15052026-login-google-oauth`
- `fix/15052026-typo-readme`
- `refactor/15052026-extract-user-service`
- `docs/15052026-update-deploy-guide`
- `chore/15052026-bump-django-version`

### 5. Comandos exactos a ejecutar

```bash
# 1. Obtener la fecha del día (no asumirla)
TODAY=$(date +%d%m%Y)

# 2. Crear y moverse a la nueva rama
git checkout -b <prefijo>/${TODAY}-<descripcion-corta>

# 3. Recién entonces hacer add y commit
git add <archivos>
git commit -m "<mensaje siguiendo conventional commits>"
```

### 6. Inferencia del prefijo

Determina el prefijo a partir del contenido de los cambios:
- Archivos nuevos que añaden features → `feat`
- Cambios que arreglan comportamiento roto → `fix`
- Solo cambios en `*.md`, comentarios o JSDoc → `docs`
- Cambios en `package.json`, `requirements.txt`, configs → `chore`
- Cambios en `.github/workflows/*` → `ci`
- Archivos `*test*` / `*spec*` modificados o añadidos → `test`
- Reorganización sin alterar comportamiento → `refactor`

Si hay ambigüedad, pregunta al usuario una sola vez antes de crear la rama.

### 7. Excepciones

- Operaciones de solo lectura (`git status`, `git log`, `git diff`, `git pull`, `git fetch`) están permitidas en `main`/`master`.
- Si el usuario explícitamente pide quedarse en `main` para revisar algo sin commitear, respeta esa intención.
- Si ya estás en una rama feature válida (no `main`/`master`), no crees una nueva — continúa trabajando en ella.

### 8. Mensajes de commit

Sigue Conventional Commits, con el mismo prefijo de la rama cuando aplique:

```
feat: add Google OAuth login flow
fix: correct typo in deployment README
refactor: extract user validation into service
```
<!-- git-branch-protocol:end -->
