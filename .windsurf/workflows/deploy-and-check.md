---
description: Deploy latest master to production server for crushme_project
---

# Deploy crushme_project to Production

Run these steps on the production server at `/home/ryzepeck/webapps/crushme_project` to deploy the latest `master` branch.

## Pre-Deploy

// turbo
1. Quick status snapshot before deploy:
```bash
bash ~/scripts/quick-status.sh
```

## Deploy Steps

// turbo
2. Pull the latest code from master:
```bash
cd /home/ryzepeck/webapps/crushme_project && git pull origin master
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

## Post-Deploy Verification

// turbo
7. Run post-deploy check:
```bash
bash ~/scripts/post-deploy-check.sh crushme_project
```

8. If something fails, check the logs:
```bash
sudo journalctl -u gunicorn --no-pager -n 30
sudo journalctl -u crushme-huey --no-pager -n 30
sudo tail -20 /var/log/nginx/error.log
```

## Architecture Reference

- **Domain**: `crushme.com.co` / `www.crushme.com.co`
- **Backend**: Django (`crushme_project` module), settings via `DJANGO_ENV=production` auto-import
- **Frontend**: Vue 3 + Vite → `backend/templates/`
- **Services**: `gunicorn.service` (Gunicorn via socket), `crushme-huey.service`
- **Nginx**: `/etc/nginx/sites-available/crushme`
- **Socket**: `/run/gunicorn.sock`
- **Static**: `/home/ryzepeck/webapps/crushme_project/backend/staticfiles/`
- **Media**: `/home/ryzepeck/webapps/crushme_project/backend/media/`
- **Venv**: `venv_cpu` (CPU-only PyTorch)
- **Resource limits**: MemoryMax=650MB, CPUQuota=60%, OOMScoreAdjust=200
- **Redis DB**: /2 (Huey), /1 (Cache)

## Notes

- `~/scripts` is a symlink to `/home/ryzepeck/webapps/ops/vps/`.
- This project uses `venv_cpu` (not `venv`) due to PyTorch CPU-only installation.
- Frontend `npm ci` may take a few minutes; the backend stays up during build.
