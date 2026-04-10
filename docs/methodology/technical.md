# Technical Context — CrushMe

## Technology Stack

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12.3 | Runtime |
| Django | 5.1.5 | Web framework |
| DRF | 3.15.2 | REST API |
| SimpleJWT | 5.3.0 | JWT authentication |
| MySQL | 8 | Database (mysqlclient 2.2.7) |
| Redis | 7.1.0 | Cache (db 1) + task queue (db 2) |
| Huey | 2.5+ | Async task queue |
| argostranslate | 1.9.6 | Offline ES/EN translation |
| Gunicorn | 23.0.0 | WSGI server |
| django-silk | 5.0+ | Profiling (conditional, `ENABLE_SILK=True`) |
| django-dbbackup | 4.0+ | Database backups |
| django-cors-headers | 4.6.0 | CORS |
| django-attachments | 1.1.1 | File galleries (vendored) |
| django-cleanup | 8.1.0 | Auto-delete orphaned files |
| Faker | 25.0.1 | Fake data generation |

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Vue | 3.5.13 | UI framework |
| Vite | 7 | Build tool + dev server |
| Pinia | 3.0.3 | State management |
| pinia-plugin-persistedstate | 4.5.0 | localStorage persistence |
| vue-router | 4.5.1 | Routing with locale prefixes |
| vue-i18n | 9.14.5 | Internationalization |
| Axios | 1.12.2 | HTTP client |
| Tailwind CSS | 4.1.13 | Utility-first CSS |
| Flowbite | 3.1.2 | UI component library |
| Headless UI | 1.7.23 | Accessible UI primitives |
| GSAP | 3.13.0 | Animations |
| SweetAlert2 | 11.23.0 | Alert dialogs |

### Testing
| Tool | Scope | Config |
|------|-------|--------|
| pytest + pytest-django | Backend | `backend/pytest.ini` |
| Jest | Frontend unit | `frontend/jest.config.cjs` |
| Playwright | Frontend E2E | `frontend/playwright.config.js` |

## Key Technical Decisions

### Single HTTP Client (not dual)
All frontend API requests go through `src/services/request_http.js`. It sends both CSRF and JWT headers, injects language/currency headers, and handles automatic token refresh. There is no separate platform API composable.

### Offline Translation
Product content is translated at WooCommerce sync time via `argostranslate` and cached in a `TranslatedContent` model. No real-time MT. Frontend reads localized fields directly.

### Mixed Pinia Store API Styles
9 stores use setup/Composition API, 3 use Options API. This is the current state — not a design decision to enforce.

### PyTorch Installed But Unused
`torch`, `transformers`, `stanza`, `ctranslate2` are in `requirements.txt` but no application code imports them. The `venv_cpu` venv and 650M memory limit exist because of PyTorch's footprint.

## Development Environment

### Prerequisites
- Python 3.12+, Node 18+
- MySQL 8, Redis
- venv at `backend/venv_cpu/` (NOT `backend/venv/`)

### Running Locally
```bash
# Backend
cd backend && source venv_cpu/bin/activate
python manage.py runserver  # :8000

# Frontend (separate terminal)
cd frontend && npm run dev  # :5173, proxies /api/ and /media/ to :8000
```

### Environment Variables
Managed via `python-decouple` reading `.env` file:
- `DJANGO_ENV` — `development` (default) or `production`
- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`
- `REDIS_CACHE_URL` (default: `redis://127.0.0.1:6379/1`)
- `REDIS_HUEY_URL` (default: `redis://127.0.0.1:6379/2`)
- `ENABLE_SILK` — Enable django-silk profiling (default: False)

## Deployment

### Production Path
`/home/ryzepeck/webapps/crushme_project`

### Deploy Sequence
1. `git pull origin main`
2. `cd backend && source venv_cpu/bin/activate && pip install -r requirements.txt && DJANGO_SETTINGS_MODULE=crushme_project.settings_prod python manage.py migrate`
3. `cd frontend && npm ci && npm run build`
4. `cd backend && DJANGO_SETTINGS_MODULE=crushme_project.settings_prod python manage.py collectstatic --noinput`
5. `sudo systemctl restart gunicorn && sudo systemctl restart crushme-huey`
6. `bash /home/ryzepeck/webapps/ops/vps/scripts/deployment/post-deploy-check.sh crushme_project`
