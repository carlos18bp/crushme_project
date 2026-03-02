# Deployment Guide — crushme_project

Instructions for deploying crushme_project to production.

---

## Prerequisites

- Ubuntu/Debian with Python 3.12+, Node 22+, MySQL 8+, Redis, Nginx
- SSL certificate (Let's Encrypt via certbot)
- Domain: `crushme.com.co`

---

## Deploy from master

```bash
cd /home/ryzepeck/webapps/crushme_project
git pull origin master

# Backend
cd backend
source venv_cpu/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# Frontend
cd ../frontend
npm install
npm run build

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart crushme-huey
```

## Environment Variables

All variables are loaded from `backend/.env` via `python-decouple`.
See `backend/.env.example` for the full list with descriptions.

Key variables:
- `DJANGO_ENV=production`
- `DJANGO_SECRET_KEY` (required)
- `DJANGO_ALLOWED_HOSTS` (required)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `REDIS_URL`
- `ENABLE_SILK=false`
