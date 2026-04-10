# Architecture — CrushMe

## System Overview

```
[Browser] → [Nginx] → /api/  → [Gunicorn → Django/DRF]  → [MySQL 8]
                     → /static/ → [filesystem]               ↕
                     → /media/  → [filesystem]           [Redis db1: cache]
                     → /*       → [Vue SPA index.html]   [Redis db2: Huey]
```

- **Backend**: Django 5.1.5 + DRF 3.15.2, single app `crushme_app`
- **Frontend**: Vue 3.5.13 + Vite 7 SPA, built to `backend/static/frontend/`
- **Database**: MySQL 8 (utf8mb4, STRICT_TRANS_TABLES)
- **Cache**: Redis db 1 (django-redis)
- **Task queue**: Huey against Redis db 2 (synchronous in dev, async in prod via `crushme-huey.service`)
- **Web server**: Gunicorn behind Nginx, socket at `/run/gunicorn.sock`

## Backend Architecture

### Single Django App: `crushme_app`

All business logic lives in one app. Modules are split by responsibility:

| Layer | Location | Count | Role |
|-------|----------|-------|------|
| Models | `crushme_app/models/` | 12 files | Data layer: User, Product, Cart, Order, WishList, Review, etc. |
| Views | `crushme_app/views/` | 20 files | API endpoints, 100% FBV with `@api_view` |
| Services | `crushme_app/services/` | 8 files | Business logic: email, translation, woocommerce, paypal, wompi |
| Serializers | `crushme_app/serializers/` | 10 files | Input validation and response formatting |
| URLs | `crushme_app/urls/` | 12 files | Modular URL routing per resource |
| Management commands | `crushme_app/management/commands/` | 12 files | Data seeding, WooCommerce sync, translation |

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
- **API**: JWT via SimpleJWT (30d access, 60d refresh, rotation + blacklist)
- **Admin**: Django session + CSRF

### Settings
- Base: `crushme_project/settings.py` (shared)
- Dev override: `settings_dev.py` (DEBUG=True, loaded when `DJANGO_ENV=development`)
- Prod override: `settings_prod.py` (HSTS, secure cookies, loaded when `DJANGO_ENV=production`)
- Pytest uses `DJANGO_SETTINGS_MODULE=crushme_project.settings` (from pytest.ini)

## Frontend Architecture

### Vue 3 SPA (No SSR, No Nuxt)

| Layer | Location | Count | Role |
|-------|----------|-------|------|
| Stores | `src/stores/modules/` | 12 files | Pinia state management (mixed setup/Options API) |
| Views | `src/views/` | 6 dirs + 4 root files | Page-level components |
| Components | `src/components/` | 9 dirs | Reusable UI components |
| Composables | `src/composables/` | 4 files | useAlert, useCart, useCheckout, useNotifications |
| Services | `src/services/` | 1 file | request_http.js — single HTTP client |
| Router | `src/router/` | 1 file | vue-router 4 with locale prefixes |
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

## Infrastructure

### Systemd Services
- `gunicorn.service` — App server (NOT `crushme_project.service`)
- `gunicorn.socket` — Socket at `/run/gunicorn.sock`
- `crushme-huey.service` — Async task worker

### Huey Periodic Tasks
- `scheduled_backup` — Sun 03:00 UTC (DB + media, 4-week retention)
- `silk_garbage_collection` — Daily 03:30 UTC (when Silk enabled)
- `weekly_slow_queries_report` — Tue 07:00 UTC
- `silk_reports_cleanup` — 1st of month 05:30 UTC

### Resource Limits
- MemoryMax=650M, CPUQuota=40%, OOMScoreAdjust=300
