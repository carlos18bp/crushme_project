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
| Translation service | `crushme-translation.service` |
| Gunicorn socket | `/run/gunicorn.sock` |
| Nginx site | `/etc/nginx/sites-available/crushme` |
| Settings | `crushme_project.settings` with `DJANGO_ENV=production` |

## Release Gate

Deploy only an integration commit that has passed:

1. Dependency and vulnerability audit.
2. Secret scan and production credential rotation when required.
3. Focused backend, frontend unit, and E2E quality gates.
4. Frontend build and Django system/migration checks.
5. Backup restore rehearsal, focused smoke tests, and the roadmap observation window.
6. Explicit lifecycle/release authorization in the fleet registry.
7. Translation model hashes, Torch-free runtime, and socket probe when the
   release changes offline translation.

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
python3 scripts/operations/translation_runtime_probe.py
```

Do not use this snippet to bypass the skill's branch, registry, health, rollback,
or production confirmation gates.

## Runtime Scope

CrushMe has one runtime coordinate: the production project described above.
Modernization worktrees are Git authoring surfaces only and must never receive
DNS, deployment credentials, databases, sockets, or services.

## Versioned Runtime Templates

The canonical project-side copies are:

- `scripts/nginx/crushme.conf`
- `scripts/systemd/crushme_project.service`
- `scripts/systemd/crushme_project.socket`
- `scripts/systemd/crushme_project.override.conf`
- `scripts/systemd/huey.service`
- `scripts/systemd/crushme-huey.override.conf`
- `scripts/systemd/crushme-dbbackup.service`
- `scripts/systemd/crushme-dbbackup.timer`
- `scripts/systemd/crushme-translation.service`

The fleet deployable copies live in `vps-ops-toolkit/config/systemd/`. Compare
both sources with the installed `/etc` files before each operational change.
Obsolete Gunicorn/Nginx copies under `backend/` are deliberately unsupported.

Wave 7 stage 1 must complete the model/runtime installation and socket probe in
`docs/translation-runtime.md` before the first translation-service restart.
The translation unit is `PartOf=crushme_project.service`, so the guarded web
restart also reloads daemon code before the public health check.

Detailed backup, restore, observability, capacity, and rollback procedures are
in `docs/operations-runbook.md`.
