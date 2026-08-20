# Architecture — CrushMe

## System Overview

```
[Browser] → [Nginx] → /api/  → [Gunicorn → Django/DRF]  → [MySQL 8]
                     → /static/ → [filesystem]               ↕
                     → /media/  → [filesystem]           [Redis db1: cache]
                     → /*       → [Vue SPA index.html]   [Redis db2: Huey]
```

- **Backend**: Django 5.2.17 LTS + DRF 3.18.0, single app `crushme_app`
- **Frontend**: Vue 3.5.41 + Vite 7 SPA, built to `backend/static/frontend/`
- **Database**: MySQL 8 (utf8mb4, STRICT_TRANS_TABLES)
- **Cache**: Redis db 1 (django-redis)
- **Task queue**: Huey against Redis db 2 (synchronous in dev, async in prod via `crushme-huey.service`)
- **Web server**: Gunicorn behind Nginx, socket at `/run/gunicorn.sock`

## Backend Architecture

### Single Django App: `crushme_app`

All business logic lives in one app. Modules are split by responsibility:

| Layer | Location | Count | Role |
|-------|----------|-------|------|
| Models | `crushme_app/models/` | 14 files / 28 model classes | Data layer: User, Product, Cart, Order, WishList, Review, etc. |
| Views | `crushme_app/views/` | 21 files | API endpoints, 100% FBV with `@api_view` |
| Services | `crushme_app/services/` | 10 files | Business logic: checkout, payments, translation, WooCommerce, email |
| Serializers | `crushme_app/serializers/` | 11 files | Input validation and response formatting |
| URLs | `crushme_app/urls/` | 12 files | Modular URL routing per resource |
| Management commands | `crushme_app/management/commands/` | 13 files | Data seeding, WooCommerce sync, translation |

### View Pattern (100% FBV)
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order = order_service.create(serializer.validated_data, request.user)
    return Response(OrderSerializer(order).data, status=201)
```

### Service Layer
Views are thin wrappers. Business logic lives in services:
- `email_service.py` — SMTP via GoDaddy, template rendering
- `translation_service.py` — Offline ES/EN via argostranslate
- `translation_batch_service.py` — Bulk translation for WooCommerce sync
- `woocommerce_service.py` — WooCommerce API client
- `woocommerce_sync_service.py` — Product sync orchestrator
- `woocommerce_order_service.py` — Local orders → WooCommerce
- `paypal_service.py` — PayPal SDK integration
- `wompi_service.py` — Wompi gateway integration

### Dual Auth
- **API**: JWT via SimpleJWT (15m access, 7d refresh, rotation + blacklist)
- **Admin**: Django session + CSRF

### Settings
- Base: `crushme_project/settings.py` (shared)
- Dev override: `settings_dev.py` (DEBUG=True, loaded when `DJANGO_ENV=development`)
- Prod override: `settings_prod.py` (HSTS and secure cookies, loaded for production/staging baseline)
- Staging entry point: `settings_staging.py` (production-like, sandbox integrations)
- Test entry point: `settings_test.py` (in-memory SQLite, local cache/Huey, fixed exchange rate, no external integrations)
- E2E entry point: `settings_e2e.py` (guarded file-backed SQLite inherited from test settings)
- MySQL CI entry point: `settings_ci_mysql.py` (ephemeral database names/hosts only)
- Pytest uses `DJANGO_SETTINGS_MODULE=crushme_project.settings_test` (from pytest.ini)

## Frontend Architecture

### Vue 3 SPA (No SSR, No Nuxt)

| Layer | Location | Count | Role |
|-------|----------|-------|------|
| Stores | `src/stores/modules/` | 12 files | Pinia state management (mixed setup/Options API) |
| Views | `src/views/` | 25 files | Page-level components |
| Components | `src/components/` | 26 files | Reusable UI components |
| Composables | `src/composables/` | 3 files | useAlert, useCart, useNotifications |
| Services | `src/services/` | 1 file | request_http.js — single HTTP client |
| Router | `src/router/` | 1 file / 21 base definitions | vue-router 4 expands routes for EN/ES and profile children |
| Locales | `src/locales/` | nested by domain | vue-i18n EN/ES translation files |

### Single HTTP Client
`src/services/request_http.js` handles ALL API requests:
- Sends `X-CSRFToken` + `Authorization: Bearer` headers
- Injects `Accept-Language` and `X-Currency` from stores
- Automatic JWT refresh on 401

### Pinia Stores (Mixed API Styles)
- **Setup/Composition API** (9): authStore, cartStore, crushStore, currencyStore, orderStore, paymentStore, productStore, profileStore, wishlistStore
- **Options API** (3): i18nStore, reviewStore, contactStore
- Persisted to localStorage via `pinia-plugin-persistedstate`

### Build
- Vite builds to `backend/static/frontend/` with hashed filenames
- Django serves the SPA via a fallback view
- Dev: Vite proxies `/api/` and `/media/` to localhost:8000

### Test Topology
- Pytest runs against `settings_test.py`; local E2E runs against guarded
  `settings_e2e.py` and deterministic `seed_e2e_data` fixtures.
- Playwright starts Django on port 8001 and Vite on port 5174, refuses
  production hosts, uses one worker for the shared SQLite scenario, and never
  contacts payment, SMTP, translation, currency, or WooCommerce providers.
- GitHub Actions partitions backend, frontend unit/build, E2E, and MySQL
  migration compatibility into independent jobs.
- The executable inventory contains 18 backend behavior files / 49 test
  functions, 7 frontend-unit files / 16 tests, and 11 Playwright specs / 21
  tests. Static flow tags map them to 56 declared outcomes.
- The E2E database is shared and guarded, so Playwright runs one worker. Stable
  selectors use `data-testid` for controls and accessible role/name elsewhere.

## Infrastructure

### Systemd Services
- `crushme_project.service` — Production app server
- Gunicorn binds to `/run/gunicorn.sock`
- `crushme-huey.service` — Async task worker

Prepared staging is isolated as `crushme_staging.service` plus
`crushme-staging-huey.service`, socket `/run/crushme_staging.sock`, MySQL
database `crushme_staging`, Redis cache DB 10, and Huey DB 11. These artifacts
are versioned only; DNS and deployment are still pending.

### Huey Periodic Tasks
- `scheduled_backup` — Sun 03:00 UTC (DB + media, 4-week retention)
- `silk_garbage_collection` — Daily 03:30 UTC (when Silk enabled)
- `weekly_slow_queries_report` — Tue 07:00 UTC
- `silk_reports_cleanup` — 1st of month 05:30 UTC

### Resource Limits
- MemoryMax=650M, CPUQuota=60%, OOMScoreAdjust=200
