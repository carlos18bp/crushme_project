---
description: Deploy latest main to production server for crushme_project
---

# Deploy crushme_project to Production

Run these steps on the production server at `/home/ryzepeck/webapps/crushme_project` to deploy the latest `main` branch.

## Pre-Deploy

// turbo
1. Quick status snapshot before deploy:
```bash
bash ~/scripts/quick-status.sh
```

## Deploy Steps

// turbo
2. Pull the latest code from main:
```bash
cd /home/ryzepeck/webapps/crushme_project && git pull origin main
```

3. Install backend dependencies and run migrations:
```bash
cd /home/ryzepeck/webapps/crushme_project/backend && source venv_cpu/bin/activate && pip install -r requirements.txt && python manage.py migrate
```

4. Build the frontend (Vue 3 + Vite):
```bash
cd /home/ryzepeck/webapps/crushme_project/frontend && npm ci && npm run build
```

5. Collect static files:
```bash
cd /home/ryzepeck/webapps/crushme_project/backend && source venv_cpu/bin/activate && python manage.py collectstatic --noinput
```

6. Restart services:
```bash
sudo systemctl restart gunicorn && sudo systemctl restart crushme-huey
```

## Architecture Reference

- **Domain**: `crushme.co` / `www.crushme.co`
- **Backend**: Django (`crushme_project` module), settings via `DJANGO_SETTINGS_MODULE=crushme_project.settings`
- **Frontend**: Vue 3 + Vite
- **Services**: `gunicorn.service` (Gunicorn via socket), `crushme-huey.service`
- **Nginx**: `/etc/nginx/sites-available/crushme`
- **Socket**: `/run/gunicorn.sock`
- **Static**: `/home/ryzepeck/webapps/crushme_project/backend/staticfiles/`
- **Media**: `/home/ryzepeck/webapps/crushme_project/backend/media/`
- **Resource limits**: MemoryMax=350MB, CPUQuota=40%
- **Redis DB**: /2
- **venv**: `venv_cpu` (CPU-only torch for ML features)

## Notes

- `~/scripts` is a symlink to `/home/ryzepeck/webapps/ops/vps/`.
- crushme uses `venv_cpu` instead of `venv` (CPU-only PyTorch build for ML features).
- The gunicorn systemd service is named `gunicorn.service` (generic name, legacy).
