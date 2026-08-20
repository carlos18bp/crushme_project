# CrushMe

CrushMe is a bilingual e-commerce and public-wishlist platform. Users can buy
products for themselves, share wishlists, and send gifts to verified "crush"
profiles. The existing product behavior is the compatibility contract during
modernization.

## Stack

- Python 3.12, Django 5.1.5, Django REST Framework 3.15
- Vue 3.5, Vite 7, Pinia 3, Vue Router, vue-i18n
- MySQL 8, Redis, Huey, Gunicorn, Nginx
- WooCommerce catalog mirror with offline ES/EN translation
- Wompi for COP payments and PayPal for USD payments

## Repository

```text
backend/              Django API, services, commands, templates
frontend/             Vue SPA, stores, components, unit and E2E harnesses
emails/               Bilingual email source templates
docs/                 Architecture, standards, audits, and roadmap
tasks/                Active context and backlog
.agents/ .claude/     Codex and Claude skills/configuration
.codex/              Codex project configuration
```

The Python environment is `backend/venv_cpu/`; there is no `backend/venv/`.
Frontend builds are generated in `backend/static/frontend/` and must not be
committed.

## Local Setup

```bash
cd backend
python3.12 -m venv venv_cpu
source venv_cpu/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

In another shell:

```bash
cd frontend
npm ci
npm run dev
```

Development defaults to SQLite and sandbox/disabled integrations. Never reuse a
production `.env` for tests or E2E.

## Focused Verification

The project intentionally forbids full-suite runs during ordinary development.
Run at most 20 tests per command and no more than three test commands per cycle.

```bash
cd backend
source venv_cpu/bin/activate
python manage.py check
pytest crushme_app/tests/path/to/test_file.py -v

cd ../frontend
npm test -- test/path/to/file.spec.js
npx playwright test e2e/path/to/flow.spec.js
npm run build
```

The current fake-data commands predate the modernization guard. Do not run them
outside an isolated local database; Wave 2 adds an enforced production refusal.

## Environments

| Environment | Settings | Data/integrations |
|---|---|---|
| Development | `crushme_project.settings` | Local DB; sandbox defaults |
| Current pytest | `crushme_project.settings` | Must be supplied an isolated local environment |
| Production | `crushme_project.settings` + `DJANGO_ENV=production` | Production MySQL/Redis and explicit live credentials |

## Documentation

- [Modernization roadmap](docs/MODERNIZATION_ROADMAP.md)
- [Architecture](docs/methodology/architecture.md)
- [Technical context](docs/methodology/technical.md)
- [Testing standard](docs/TESTING_QUALITY_STANDARDS.md)
- [Deployment guide](docs/deployment-guide.md)
- [Active work](tasks/active_context.md)

Production deployments and verification must use the canonical
`deploy-and-check` skill. Do not deploy directly from a feature/session branch.
