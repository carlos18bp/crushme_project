# Architecture - CrushMe

## System Overview

```text
[Browser] -> [Nginx] -> /api/    -> [Gunicorn/Django/DRF] -> [MySQL 8]
                    -> /static/  -> [filesystem]                 |
                    -> /media/   -> [filesystem]            [Redis DB 1]
                    -> /*        -> [Vue SPA]                [Redis DB 2/Huey]
```

- **Backend**: Django 5.2.17 + DRF 3.18.0, single business app
  `crushme_app`.
- **Frontend**: Vue 3.5.41 + Vite 7.3.6 SPA, built into
  `backend/static/frontend/`.
- **Database**: MySQL 8 with `utf8mb4` and strict SQL mode.
- **Cache/queue**: Redis DB 1 for Django cache and DB 2 for Huey.
- **Runtime**: `crushme_project.service` behind Nginx through
  `/run/gunicorn.sock`, plus `crushme-huey.service`.

## Backend Architecture

### Single Business App

`crushme_app` is intentionally retained. Models, serializers, function-based
DRF views, services, URLs, tasks, and management commands are separated by
resource within the app. Modernization does not introduce an incidental app or
CBV/ViewSet migration.

The normal request path is:

```text
URL -> @api_view -> serializer/validator -> service -> ORM -> Response
```

Business integrations remain behind services for email, translation,
WooCommerce, PayPal, and Wompi. Raw client input must not flow directly to an
integration or persisted total.

### Authentication Boundary

- Public API: SimpleJWT with 15-minute access and 7-day refresh lifetimes.
- Refresh rotation is blacklisted and serialized with a MySQL row lock so the
  same refresh token cannot produce two valid successors.
- Logout revokes the submitted refresh token.
- Admin: Django session authentication with CSRF.

### Payment Boundary

`PaymentSession` stores the server-calculated gateway contract. Creation
rebuilds products, variants, shipping, discounts, currency, and totals from
trusted records. PayPal capture and Wompi signature/properties must match that
session before order processing continues.

### Upload And Public API Boundary

Image uploads are verified by content and constrained by extension, MIME type,
bytes, decoded pixel count, and files per request. Named DRF throttles protect
authentication, payment creation/confirmation, webhooks, uploads, public
writes, and public search.

### Translation Boundary

Argos Translate performs offline translation during WooCommerce sync. Runtime
settings force `ARGOS_CHUNK_TYPE=MINISBD` and `ARGOS_DEVICE_TYPE=cpu`; no
application path creates a Stanza pipeline.

### Settings

- Shared: `crushme_project.settings`.
- Development: `settings_dev.py` override with sandbox integrations.
- Test: `settings_test.py` with SQLite, in-memory cache/Huey, and local email.
- E2E: `settings_e2e.py` with isolated SQLite and disabled/sandbox gateways.
- Production: `settings_prod.py`, loaded only with `DJANGO_ENV=production`,
  requiring live HTTPS integration configuration, secure headers/cookies, and
  frame embedding denial. Gateway popups remain compatible through COOP.

## Frontend Architecture

The Vue SPA retains Pinia stores with their existing mixed setup/Options API
styles. Every API call goes through `src/services/request_http.js`, which adds
CSRF, JWT, language, and currency headers.

The client shares one in-flight token refresh between failed requests. An auth
epoch prevents a late refresh response from restoring credentials after logout
or account replacement. Payment gateway public configuration is fetched from
the backend rather than compiled into the frontend bundle.

Locale-prefixed routing, Vue I18n, server-translated product content, and
server-priced currency responses remain unchanged business contracts.

## Production Infrastructure

### Service Limits

| Service | MemoryHigh | MemoryMax | CPUQuota | TasksMax | OOMScoreAdjust |
|---|---:|---:|---:|---:|---:|
| `crushme_project.service` | 500M | 650M | 60% | 80 | 200 |
| `crushme-huey.service` | 350M | 450M | 30% | 50 | 400 |

### Periodic Work

- Weekly database/media backup through Huey with four-copy retention.
- Silk garbage collection and reports only when profiling is enabled.
- Slow-query reporting and monthly Silk cleanup.

Wave 5 owns final alignment of timers, log retention, restore automation,
observability, and measured headroom; it must operate on this production
coordinate rather than create a staging runtime.
