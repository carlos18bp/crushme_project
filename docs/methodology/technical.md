# Technical Context - CrushMe

## Technology Stack

### Backend

| Technology | Version | Purpose |
|---|---:|---|
| Python | 3.12.3 | Runtime |
| Django | 5.2.17 | Web framework |
| DRF | 3.18.0 | REST API |
| SimpleJWT | 5.5.1 | JWT authentication |
| MySQL | 8 | Database (`mysqlclient` 2.2.8) |
| Redis | 7.1.0 | Cache DB 1 and Huey DB 2 |
| Huey | 2.6.0 | Async/periodic work |
| Argos Translate | 1.11.0 | Offline ES/EN translation |
| Torch | 2.13.0+cpu | Argos dependency, CPU wheel |
| Gunicorn | 23.0.0 | WSGI server |
| django-silk | 5.5.2 | Conditional profiling |
| django-dbbackup | 5.3.0 | Backup integration |

### Frontend

| Technology | Version | Purpose |
|---|---:|---|
| Vue | 3.5.41 | UI framework |
| Vite | 7.3.6 | Build tool/dev server |
| Pinia | 3.0.4 | State management |
| pinia-plugin-persistedstate | 4.7.1 | Local persistence |
| Vue Router | 4.6.4 | Locale-prefixed routing |
| Vue I18n | 9.14.5 | ES/EN UI localization |
| Axios | 1.19.0 | Shared HTTP client |
| Tailwind CSS | 4.3.3 | Styling |
| Flowbite | 3.1.2 | UI components |
| GSAP | 3.15.0 | Animation |
| SweetAlert2 | 11.26.25 | Dialogs |

### Quality Tooling

- Backend: pytest, pytest-django, coverage, Ruff, Bandit, pip-audit.
- Frontend: Jest, Vue Test Utils, Playwright, ESLint, npm audit.
- Repository: pre-commit, detect-secrets, semantic test-quality gate, six
  partitioned GitHub Actions jobs, and a MySQL auth-concurrency regression.

## Key Decisions

- Preserve the single `crushme_app`, function-based DRF views, and service
  layer.
- Preserve the single Axios client; token refresh is shared and guarded against
  late persistence after logout.
- Treat `PaymentSession` as the durable authority for payment amounts and
  gateway confirmation.
- Translate offline during WooCommerce sync and retain the existing fallback
  for dynamic content, but load Argos only when that fallback is exercised.
- Force Argos MiniSBD on CPU until Argos no longer pins vulnerable Stanza
  1.10.1. Enabling Stanza chunking is prohibited.
- Keep exact backend pins and lock frontend transitive versions through
  `package-lock.json`. Framework majors are separate compatibility work.
- Pin security-relevant reachable backend transitives explicitly when their
  safe floor is stricter than the direct package constraint. Current explicit
  pins are Click, Filelock, idna, Protobuf, and SentencePiece.

## Development And Test Environments

The runtime venv is `backend/venv_cpu/`, not `backend/venv/`.

```bash
# Backend development
cd backend
source venv_cpu/bin/activate
python manage.py runserver

# Focused backend test
pytest crushme_app/tests/path/to/test_file.py -v

# Frontend development
cd frontend
npm run dev

# Focused frontend checks
npm test -- path/to/file.spec.js
npx playwright test e2e/path/to/spec.js
```

Tests select `settings_test.py`; Playwright uses `settings_e2e.py`. Both isolate
database, cache, queue, email, and payment integrations. Fake-data commands
have code-level production refusal.

## Environment Variables

`python-decouple` reads `backend/.env`; committed examples contain placeholders
only. Relevant groups are:

- Django: `DJANGO_ENV`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`,
  `DJANGO_ALLOWED_HOSTS`, CSRF/CORS origins, and log level.
- Data: database name/user/password/host/port, `REDIS_CACHE_URL`, `REDIS_URL`.
- Auth: `JWT_ACCESS_TOKEN_MINUTES` (15) and `JWT_REFRESH_TOKEN_DAYS` (7), plus
  named `THROTTLE_*` rates.
- Payments: explicit PayPal and Wompi IDs/secrets, mode/environment, and HTTPS
  endpoints. Production requires PayPal `live` and Wompi `production`.
- Commerce: WooCommerce API URL/key/secret and dropshipping customer ID.
- Uploads: maximum bytes, pixels, and files per request.
- Translation: `ARGOS_CHUNK_TYPE=MINISBD` and `ARGOS_DEVICE_TYPE=cpu`.
- Optional profiling: `ENABLE_SILK=False` by default.

Secrets remain mode 600 in runtime/protected stores and never enter frontend
environment variables.

## Production Deployment

Production path: `/home/ryzepeck/webapps/crushme_project`.

1. Create fresh database/media backups, rehearse restore, and record rollback
   commit/environment/dependency state.
2. Pull the reviewed `main` release.
3. Activate `backend/venv_cpu` and run
   `python -m pip install --no-cache-dir -r requirements.txt`.
4. Run `python -m pip check`, Django checks, migration drift check, then
   `DJANGO_ENV=production python manage.py migrate`.
5. Run `npm ci && npm run build` in `frontend/`.
6. Run `DJANGO_ENV=production python manage.py collectstatic --noinput`.
7. Restart `crushme_project.service` and `crushme-huey.service`.
8. Run the toolkit post-deploy check, public health/payment-config smoke checks,
   service/log inspection, and retain rollback artifacts through observation.

Runtime templates are versioned under `scripts/nginx/` and `scripts/systemd/`.
Backups run through `crushme-dbbackup.timer`, not Huey. The restore,
observability, rollback, and capacity procedures are defined in
`docs/operations-runbook.md`.
