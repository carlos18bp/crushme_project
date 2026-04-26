---
trigger: model_decision
description: Project intelligence and lessons learned. Reference for project-specific patterns, preferences, and key insights discovered during development.
---

# Lessons Learned — CrushMe

This file captures important patterns, preferences, and project intelligence that help work more effectively with this codebase. Updated as new insights are discovered.

---

## 1. Architecture Patterns

### Single Django App: `crushme_app`
- All models, views, serializers, and services live in `crushme_app/`
- Models are split into individual files under `crushme_app/models/`
- Views are split per resource: `auth_views.py`, `product_views.py`, `cart_views.py`, etc.
- This works for now but may need splitting if scope grows significantly

### Service Layer Pattern
- Business logic lives in `crushme_app/services/`, not in views
- Views are thin FBV wrappers that call service methods
- Services: `email_service`, `translation_service`, `translation_batch_service`, `woocommerce_service`, `woocommerce_sync_service`, `woocommerce_order_service`, `paypal_service`, `wompi_service`

### WooCommerce Mirror + Offline Translation
- Products are mirrored from a remote WooCommerce store via `WooCommerceProduct` and `WooCommerceProductVariation` models
- All text content is translated offline via `argostranslate` and cached in `TranslatedContent` model at sync time
- There is no real-time MT

---

## 2. Code Style & Conventions

### Backend: Function-Based Views (FBV)
- **All** DRF views use `@api_view` decorators, not class-based views
- Never convert to CBV unless explicitly requested
- Pattern: deserialize → service call → response

### Frontend: Single HTTP Client
- All requests go through `src/services/request_http.js` — Axios with CSRF + JWT + auto-refresh
- Sends `X-CSRFToken`, `Authorization: Bearer`, `Accept-Language`, and `X-Currency` headers
- There is no separate `usePlatformApi.js`

### Frontend: Pinia Mixed API Styles
- Most stores use setup/Composition API (`defineStore('name', () => { ... })`)
- A few stores (i18nStore, reviewStore, contactStore) use Options API
- All stores in `src/stores/modules/`, camelCase filenames

### Bilingual Content Pattern
- Product/blog text is translated server-side at WooCommerce sync time via `argostranslate`
- Frontend reads localized fields directly — do not translate client-side
- UI strings go through `vue-i18n` locale files in `src/locales/`

### Naming Conventions
- Backend: snake_case for everything (Python standard)
- Frontend stores: camelCase file names (`authStore.js`, `productStore.js`)
- Frontend components: PascalCase (`HomeView.vue`, `LoginView.vue`)
- Frontend composables: camelCase with `use` prefix (`useAlert.js`, `useCart.js`)

---

## 3. Development Workflow

### Backend Commands Always Need venv_cpu
```bash
cd backend && source venv_cpu/bin/activate && <command>
```
The venv is `venv_cpu/` (PyTorch CPU build), **not** `venv/`.

### Huey Immediate Mode in Development
- When `DJANGO_ENV != 'production'`, Huey tasks execute synchronously
- No need to run Redis or Huey worker for development
- Tasks still need to be importable and functional

### Frontend Dev Proxy
- Vite proxies `/api` and `/media` to Django at `localhost:8000`
- Both servers must be running simultaneously for full functionality
- In production, everything goes through Django (no separate frontend server)

### Test Execution Rules
- Never run the full test suite — always specify files
- Backend: `cd backend && source venv_cpu/bin/activate && pytest crushme_app/tests/<specific_file> -v`
- Frontend unit: `cd frontend && npm test -- <specific_file>`
- Frontend E2E: `cd frontend && npx playwright test e2e/<specific_file>` — max 2 files per invocation
- Use `E2E_REUSE_SERVER=1` when dev server is already running

---

## 4. Production Deployment

### Build Flow
1. Frontend: `cd frontend && npm run build` → generates `backend/static/frontend/` (Vite build)
2. Backend: `python manage.py collectstatic` → copies to `backend/staticfiles/`
3. Restart: `sudo systemctl restart gunicorn && sudo systemctl restart crushme-huey`

### Django Serves Vue SPA
- A SPA fallback view serves the Vue app for all non-API routes
- This is the LAST URL pattern — all other routes take priority
- Static assets use hashed filenames for cache busting (configured in `vite.config.js`)

---

## 5. Dual Payment Gateways

### PayPal (International, USD)
- `paypal_order_views.py` + `paypal_service.py`
- Webhook endpoint updates `Order.status` based on payment events

### Wompi (Colombian, COP)
- `wompi_order_views.py` + `wompi_service.py`
- Webhook endpoint updates `Order.status` based on payment events

---

## 6. Testing Insights

### Backend conftest.py
- Custom coverage report with Unicode progress bars replaces default pytest-cov output
- Fixtures: `api_client`, `user`, `admin_user`, `authenticated_client`, `admin_client`

### Playwright + Vite Dev Server Patterns
- **Never use `networkidle`** with Vite dev server — HMR WebSocket keeps connection alive
- Use `{ waitUntil: 'domcontentloaded' }` in `page.goto()` + explicit element waits
- Use role-based locators and `data-testid` attributes

---

## 7. Auth Strategy

### Dual Auth
- `/api/auth/...` uses JWT via SimpleJWT (30d access, 60d refresh, rotation + blacklist)
- `/admin/` uses Django session + CSRF (default)
- The single frontend HTTP client handles both — sends CSRF token + JWT Bearer header together

---

## 8. Methodology Maintenance

### When to Refresh Memory Files
- After adding new models or major features
- After significant changes to test infrastructure
- When documented patterns drift from actual code
