---
name: deploy-and-check
description: "Deploy latest master/main to the production server with pre-deploy checks, build, restart, and post-deploy verification."
disable-model-invocation: true
allowed-tools: Bash
---

> Ejecutar estos pasos conectado al servidor de producción vía SSH.
> Ruta base: `/home/ryzepeck/webapps/crushme_project`
> NO ejecutar en local.

# Deploy crushme_project to Production

Run these steps on the production server at `/home/ryzepeck/webapps/crushme_project` to deploy the latest `main` branch.

## Pre-Deploy

1. Quick status snapshot before deploy:
```bash
bash /home/ryzepeck/webapps/ops/vps/scripts/diagnostics/quick-status.sh
```

## Deploy Steps

2. Pull the latest code from main:
```bash
cd /home/ryzepeck/webapps/crushme_project && git pull origin main
```

3. Install backend dependencies and run migrations:
```bash
cd /home/ryzepeck/webapps/crushme_project/backend && source venv_cpu/bin/activate && pip install -r requirements.txt && DJANGO_SETTINGS_MODULE=crushme_project.settings_prod python manage.py migrate
```

4. Build the frontend (Vite build → Django static):
```bash
cd /home/ryzepeck/webapps/crushme_project/frontend && npm ci && npm run build
```

5. Collect static files:
```bash
cd /home/ryzepeck/webapps/crushme_project/backend && source venv_cpu/bin/activate && DJANGO_SETTINGS_MODULE=crushme_project.settings_prod python manage.py collectstatic --noinput
```

6. Restart services:
```bash
sudo systemctl restart gunicorn && sudo systemctl restart crushme-huey
```

## Post-Deploy Verification

7. Run post-deploy check for crushme_project:
```bash
bash /home/ryzepeck/webapps/ops/vps/scripts/deployment/post-deploy-check.sh crushme_project
```
Expected: PASS on all checks, FAIL=0.

8. If something fails, check the logs:
```bash
sudo journalctl -u gunicorn.service --no-pager -n 30
sudo journalctl -u crushme-huey.service --no-pager -n 30
sudo tail -20 /var/log/nginx/error.log
```

## Architecture Reference

- **Domain**: `crushme.com.co` / `www.crushme.com.co`
- **Backend**: Django (`crushme_project` module), settings selected via `DJANGO_SETTINGS_MODULE=crushme_project.settings_prod` in systemd unit
- **Frontend**: Vue 3 SPA (Vite build) → `backend/static/frontend/` + Django SPA fallback view
- **Services**: `gunicorn.service` (Gunicorn via socket), `gunicorn.socket`, `crushme-huey.service`
- **Nginx**: `/etc/nginx/sites-available/crushme_project`
- **Socket**: `/run/gunicorn.sock`
- **Static**: `/home/ryzepeck/webapps/crushme_project/backend/staticfiles/`
- **Media**: `/home/ryzepeck/webapps/crushme_project/backend/media/`
- **Resource limits**: MemoryMax=650M, CPUQuota=40%, OOMScoreAdjust=300

## Cleanup

9. Remove `node_modules` to save disk space (frontend already compiled):
```bash
rm -rf /home/ryzepeck/webapps/crushme_project/frontend/node_modules
```

## Notes

- VPS operations scripts live in `/home/ryzepeck/webapps/ops/vps/scripts/`.
- Frontend uses `npm run build` which runs `vite build` and outputs to `backend/static/frontend/` (configured in `vite.config.js`).
- `DJANGO_SETTINGS_MODULE=crushme_project.settings_prod` must be set for migrate and collectstatic commands (manage.py defaults to settings_dev).
