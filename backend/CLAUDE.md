# Backend Rules — CrushMe

## Stack And Scope
- Django 5.1.5 + DRF 3.15.2, Python 3.x.
- **Single business app**: `crushme_app` — contains all models, views, serializers, services, and tests.
- Auxiliary apps: `django_attachments` (vendored), `easy_thumbnails`, `dbbackup`, `silk` (conditional), `huey.contrib.djhuey`, `corsheaders`, `rest_framework`, `rest_framework_simplejwt.token_blacklist`.
- Production settings module: `crushme_project.settings_prod`.
- Database: **MySQL 8** (`mysqlclient`, `utf8mb4`, `STRICT_TRANS_TABLES`). Cache + queue: Redis (db 1 for cache, db 2 for Huey).
- **venv**: `backend/venv_cpu/` (PyTorch CPU build) — **not** `backend/venv/`.

## Project Conventions
- DRF views are **function-based** with `@api_view`. Pattern: deserialize → service call → respond. Do not convert to CBV/`APIView`/`ViewSets`.
- View modules are split per resource: `auth_views.py`, `product_views.py`, `cart_views.py`, `order_views.py`, `wishlist_views.py`, `review_views.py`, `paypal_order_views.py`, `wompi_order_views.py`, `woocommerce_local_views.py`, `favorite_product_views.py`, `contact_views.py`, `feed_views.py`, `geolocation_views.py`, `discount_views.py`, `user_search_views.py`.
- **Service layer is real**: `crushme_app/services/` holds the bulk of business logic — `email_service`, `translation_service` (offline `argostranslate`), `translation_batch_service`, `woocommerce_service`, `woocommerce_sync_service`, `woocommerce_order_service`, `paypal_service`, `wompi_service`. Views are thin wrappers that call services.
- Translation is **offline** via `argostranslate` and **cached at sync time** in a `TranslatedContent` model. There is no real-time MT.
- The custom `User` model uses email as the username field and adds a "crush verification" workflow (`is_crush`, `crush_verification_status`, `crush_verified_at`).
- `GuestUser` model supports anonymous checkout via session.
- Prefer Django ORM. Raw SQL only when strictly necessary, always parameterized.

## Auth And Security
- **API auth**: JWT via SimpleJWT — `ACCESS_TOKEN_LIFETIME=30d`, `REFRESH_TOKEN_LIFETIME=60d`, refresh rotation enabled, blacklist after rotation.
- **Admin auth**: Django session + CSRF (default).
- `settings_prod.py` enforces HSTS (1y), `SECURE_SSL_REDIRECT=True`, secure cookies, NOSNIFF, `X_FRAME_OPTIONS=SAMEORIGIN`.
- `CORS_ALLOW_CREDENTIALS=True` and a custom CORS-allowed header `x-currency` for the multi-currency frontend.
- `MEDIA_*` is on the local filesystem; uploaded user content (avatars, gallery) lives under `backend/media/`.
- Validate input in DRF serializers. Never disable CSRF or hardcode secrets.

## Commands
- Activate venv from `backend/`: `cd backend && source venv_cpu/bin/activate`
- Run backend tests: `pytest crushme_app/tests/path/to/test_file.py -v`
- Run a focused backend check: `python manage.py check`
- Run dev server: `python manage.py runserver`
- Make migrations: `python manage.py makemigrations crushme_app && python manage.py migrate`

## Testing Rules
- Run only the changed test file or a tight regression slice.
- Never run the full backend suite.
- Keep test names focused on one observable behavior.
- Prefer deterministic tests: freeze time, seed data explicitly, and avoid hidden global state.

## Tech Debt to Be Aware Of
- **PyTorch is in `requirements.txt` but unused** — no active code imports it. The 650M memory limit and the `venv_cpu` exist because of PyTorch's footprint.
- `stanza` and `ctranslate2` are also installed without active integration.
- The single `crushme_app` is large (~25 models, 15+ view modules); consider splitting if it grows further.
