# Deployment Guide - CrushMe

This document records project-specific facts. The executable deployment
protocol is `.agents/skills/deploy-and-check/SKILL.md` and the fleet registry is
`vps-ops-toolkit/projects.yml`.

## Production Coordinate

| Item | Value |
|---|---|
| Path | `/home/ryzepeck/webapps/crushme_project` |
| Branch | `main` |
| Domain | `crushme.com.co`, `www.crushme.com.co` |
| Django service | `crushme_project.service` |
| Huey service | `crushme-huey.service` |
| Gunicorn socket | `/run/gunicorn.sock` |
| Nginx site | `/etc/nginx/sites-available/crushme` |
| Settings | `crushme_project.settings` with `DJANGO_ENV=production` |

## Release Gate

Deploy only an integration commit that has passed:

1. Dependency and vulnerability audit.
2. Secret scan and production credential rotation when required.
3. Focused backend, frontend unit, and E2E quality gates.
4. Frontend build and Django system/migration checks.
5. Staging smoke tests and the roadmap observation window.
6. Explicit lifecycle/release authorization in the fleet registry.

## Canonical Sequence

The deployment skill performs the guarded form of this sequence:

```bash
cd /home/ryzepeck/webapps/crushme_project
git pull --ff-only origin main

cd backend
source venv_cpu/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput

cd ../frontend
npm ci
npm run build

cd ../backend
python manage.py collectstatic --noinput

sudo systemctl restart crushme_project.service
sudo systemctl restart crushme-huey.service

bash /home/ryzepeck/webapps/vps-ops-toolkit/scripts/deployment/post-deploy-check.sh crushme_project
```

Do not use this snippet to bypass the skill's branch, registry, health, rollback,
or production confirmation gates.

## Staging

Staging uses `crushme_project.settings_staging`, separate MySQL and Redis
resources, sandbox gateways, disabled scheduled backups, and its own service
names/socket. It must never copy production payment secrets or run against the
production database.

The planned hostname is `crushme.projectapp.co`; deployment remains blocked
until DNS resolves to the staging VPS.
