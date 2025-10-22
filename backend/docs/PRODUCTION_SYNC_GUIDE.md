# 🚀 Guía de Sincronización y Deployment en Producción

## 📋 Índice

1. [Sincronización Completa de WooCommerce](#sincronización-completa-de-woocommerce)
2. [Sincronización de Productos Específicos](#sincronización-de-productos-específicos)
3. [Traducciones Automáticas](#traducciones-automáticas)
4. [Configuración de Tareas Automáticas](#configuración-de-tareas-automáticas)
5. [Deployment en Producción](#deployment-en-producción)
6. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)

---

## 1. Sincronización Completa de WooCommerce

### 📦 Sincronizar TODOS los Productos

```bash
# Sincronización completa (puede tardar varios minutos)
python manage.py sync_woocommerce_products

# Con límite de productos (recomendado para pruebas)
python manage.py sync_woocommerce_products --limit 100

# Solo productos publicados
python manage.py sync_woocommerce_products --status publish

# Forzar actualización de productos existentes
python manage.py sync_woocommerce_products --force-update
```

### 📊 Sincronizar Categorías

```bash
# Sincronizar todas las categorías
python manage.py sync_woocommerce_categories

# Con límite
python manage.py sync_woocommerce_categories --limit 50
```

### 🔄 Sincronización Completa (Productos + Categorías)

```bash
# Script completo de sincronización
python manage.py sync_woocommerce_categories
python manage.py sync_woocommerce_products
```

---

## 2. Sincronización de Productos Específicos

### 🎯 Sincronizar Producto de Dropshipping

Si tienes un producto dropshipping (como el ID 48500) que quieres agregar a la DB local:

```bash
# Sincronizar un producto específico
python manage.py sync_woocommerce_products --product-id 48500

# Sincronizar múltiples productos
python manage.py sync_woocommerce_products --product-ids 48500,48501,48502

# Sincronizar y forzar actualización
python manage.py sync_woocommerce_products --product-id 48500 --force-update
```

### 📝 Verificar Sincronización

```bash
# Verificar que el producto se sincronizó
python manage.py shell -c "
from crushme_app.models import WooCommerceProduct
product = WooCommerceProduct.objects.filter(wc_id=48500).first()
if product:
    print(f'✅ Producto sincronizado: {product.name}')
else:
    print('❌ Producto no encontrado')
"
```

---

## 3. Traducciones Automáticas

### 🌍 Traducir Productos

```bash
# Traducir todos los productos sin traducción
python manage.py translate_products

# Traducir solo productos nuevos (sin traducción)
python manage.py translate_products --new-only

# Traducir productos específicos
python manage.py translate_products --product-ids 48500,20090

# Forzar re-traducción de todos
python manage.py translate_products --force

# Traducir con límite (para pruebas)
python manage.py translate_products --limit 50
```

### 📂 Traducir Categorías

```bash
# Traducir todas las categorías
python manage.py translate_categories

# Solo categorías nuevas
python manage.py translate_categories --new-only

# Forzar re-traducción
python manage.py translate_categories --force
```

### 🎯 Idiomas Soportados

Por defecto, las traducciones se hacen a **inglés (en)**. Para agregar más idiomas:

```python
# En settings.py
TRANSLATION_LANGUAGES = ['en', 'fr', 'de']  # Inglés, Francés, Alemán
```

---

## 4. Configuración de Tareas Automáticas

### ⏰ Usando APScheduler (Ya Configurado)

El sistema ya tiene configurado APScheduler para ejecutar tareas automáticas.

#### Verificar Tareas Configuradas

```bash
# Ver tareas programadas
python manage.py shell -c "
from django_apscheduler.models import DjangoJob
jobs = DjangoJob.objects.all()
for job in jobs:
    print(f'Job: {job.name}')
    print(f'  Next run: {job.next_run_time}')
    print(f'  Interval: Every {job.interval_seconds / 3600} hours')
    print()
"
```

#### Configuración Actual (en `crushme_app/apps.py`)

```python
# Sincronización de productos cada 6 horas
scheduler.add_job(
    sync_woocommerce_data,
    trigger=IntervalTrigger(hours=6),
    id='sync_woocommerce_products',
    name='Sync WooCommerce Products',
    replace_existing=True
)

# Traducciones cada 12 horas
scheduler.add_job(
    translate_new_content,
    trigger=IntervalTrigger(hours=12),
    id='translate_new_content',
    name='Translate New Content',
    replace_existing=True
)
```

### 🔧 Modificar Intervalos de Sincronización

Edita `crushme_app/apps.py`:

```python
# Sincronizar cada 3 horas (en lugar de 6)
scheduler.add_job(
    sync_woocommerce_data,
    trigger=IntervalTrigger(hours=3),  # ← Cambiar aquí
    id='sync_woocommerce_products',
    name='Sync WooCommerce Products',
    replace_existing=True
)

# Traducir cada 6 horas (en lugar de 12)
scheduler.add_job(
    translate_new_content,
    trigger=IntervalTrigger(hours=6),  # ← Cambiar aquí
    id='translate_new_content',
    name='Translate New Content',
    replace_existing=True
)
```

### 📅 Programar con Cron (Alternativa)

Si prefieres usar cron en lugar de APScheduler:

```bash
# Editar crontab
crontab -e

# Agregar estas líneas:

# Sincronizar productos cada 6 horas
0 */6 * * * cd /path/to/backend && /path/to/venv/bin/python manage.py sync_woocommerce_products >> /var/log/crushme/sync.log 2>&1

# Traducir contenido cada 12 horas
0 */12 * * * cd /path/to/backend && /path/to/venv/bin/python manage.py translate_products --new-only >> /var/log/crushme/translate.log 2>&1

# Sincronizar categorías diariamente
0 2 * * * cd /path/to/backend && /path/to/venv/bin/python manage.py sync_woocommerce_categories >> /var/log/crushme/categories.log 2>&1
```

---

## 5. Deployment en Producción

### 🚀 Checklist Pre-Deployment

#### 1. **Configurar Variables de Entorno**

Crea archivo `.env` en producción:

```bash
# .env (Producción)

# Django
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/crushme_db

# WooCommerce
WOOCOMMERCE_URL=https://your-store.com
WOOCOMMERCE_CONSUMER_KEY=ck_xxxxxxxxxxxxx
WOOCOMMERCE_CONSUMER_SECRET=cs_xxxxxxxxxxxxx

# Frontend
FRONTEND_URL=https://yourdomain.com

# PayPal
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-secret
PAYPAL_MODE=live  # ← Cambiar a 'live' en producción

# Cache (Redis recomendado)
REDIS_URL=redis://localhost:6379/0

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

#### 2. **Instalar Dependencias**

```bash
# En el servidor de producción
cd /path/to/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. **Configurar Base de Datos**

```bash
# Crear base de datos PostgreSQL
sudo -u postgres psql
CREATE DATABASE crushme_db;
CREATE USER crushme_user WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE crushme_db TO crushme_user;
\q

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

#### 4. **Sincronización Inicial**

```bash
# Sincronizar categorías primero
python manage.py sync_woocommerce_categories

# Sincronizar productos (puede tardar)
python manage.py sync_woocommerce_products --limit 1000

# Traducir contenido
python manage.py translate_products --new-only
python manage.py translate_categories --new-only
```

#### 5. **Configurar Archivos Estáticos**

```bash
# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

### 🔧 Configurar Gunicorn

```bash
# Instalar Gunicorn
pip install gunicorn

# Crear archivo de configuración
nano /path/to/backend/gunicorn_config.py
```

**gunicorn_config.py:**
```python
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '/var/log/crushme/gunicorn-access.log'
errorlog = '/var/log/crushme/gunicorn-error.log'
loglevel = 'info'

# Process naming
proc_name = 'crushme_backend'

# Server mechanics
daemon = False
pidfile = '/var/run/crushme/gunicorn.pid'
user = 'www-data'
group = 'www-data'
tmp_upload_dir = None
```

### 📝 Crear Servicio Systemd

```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/crushme.service
```

**crushme.service:**
```ini
[Unit]
Description=CrushMe Django Backend
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/backend/venv/bin"
ExecStart=/path/to/backend/venv/bin/gunicorn \
    --config /path/to/backend/gunicorn_config.py \
    crushme_project.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable crushme
sudo systemctl start crushme
sudo systemctl status crushme
```

### 🌐 Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/crushme
```

**crushme (nginx config):**
```nginx
upstream crushme_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logs
    access_log /var/log/nginx/crushme-access.log;
    error_log /var/log/nginx/crushme-error.log;

    # Static files
    location /static/ {
        alias /path/to/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /path/to/backend/media/;
        expires 30d;
    }

    # API endpoints
    location / {
        proxy_pass http://crushme_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/crushme /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 🔒 Configurar SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renovación (ya configurado por certbot)
sudo certbot renew --dry-run
```

---

## 6. Monitoreo y Mantenimiento

### 📊 Logs de Sincronización

```bash
# Ver logs de sincronización
tail -f /var/log/crushme/sync.log

# Ver logs de traducciones
tail -f /var/log/crushme/translate.log

# Ver logs de Gunicorn
tail -f /var/log/crushme/gunicorn-error.log

# Ver logs de Nginx
tail -f /var/log/nginx/crushme-error.log
```

### 🔍 Verificar Estado del Sistema

```bash
# Estado del servicio Django
sudo systemctl status crushme

# Estado de Nginx
sudo systemctl status nginx

# Verificar procesos
ps aux | grep gunicorn

# Verificar conexiones
netstat -tlnp | grep :8000
```

### 📈 Monitorear Tareas Automáticas

```bash
# Ver tareas programadas en Django
python manage.py shell -c "
from django_apscheduler.models import DjangoJob, DjangoJobExecution
import datetime

print('📅 Tareas Programadas:')
print('=' * 60)
for job in DjangoJob.objects.all():
    print(f'\\n{job.name}')
    print(f'  ID: {job.id}')
    print(f'  Próxima ejecución: {job.next_run_time}')
    
    # Últimas ejecuciones
    executions = DjangoJobExecution.objects.filter(job=job).order_by('-run_time')[:5]
    print(f'  Últimas ejecuciones:')
    for exe in executions:
        status = '✅' if exe.status == 'Executed' else '❌'
        print(f'    {status} {exe.run_time} - {exe.status}')
"
```

### 🔄 Reiniciar Servicios

```bash
# Reiniciar Django (después de cambios en código)
sudo systemctl restart crushme

# Recargar Nginx (después de cambios en config)
sudo systemctl reload nginx

# Reiniciar todo
sudo systemctl restart crushme nginx
```

### 🧹 Mantenimiento de Base de Datos

```bash
# Limpiar ejecuciones antiguas de tareas
python manage.py shell -c "
from django_apscheduler.models import DjangoJobExecution
from datetime import datetime, timedelta

# Eliminar ejecuciones mayores a 30 días
cutoff = datetime.now() - timedelta(days=30)
deleted = DjangoJobExecution.objects.filter(run_time__lt=cutoff).delete()
print(f'Eliminadas {deleted[0]} ejecuciones antiguas')
"

# Optimizar base de datos (PostgreSQL)
sudo -u postgres psql crushme_db -c "VACUUM ANALYZE;"
```

---

## 📝 Scripts de Mantenimiento

### Script de Sincronización Completa

Crea `scripts/full_sync.sh`:

```bash
#!/bin/bash

# Script de sincronización completa
# Ejecutar: ./scripts/full_sync.sh

echo "🔄 Iniciando sincronización completa..."
echo "Fecha: $(date)"
echo ""

# Activar entorno virtual
source /path/to/backend/venv/bin/activate

# Ir al directorio del proyecto
cd /path/to/backend

# Sincronizar categorías
echo "📂 Sincronizando categorías..."
python manage.py sync_woocommerce_categories

# Sincronizar productos
echo "📦 Sincronizando productos..."
python manage.py sync_woocommerce_products

# Traducir contenido nuevo
echo "🌍 Traduciendo contenido nuevo..."
python manage.py translate_products --new-only
python manage.py translate_categories --new-only

echo ""
echo "✅ Sincronización completa finalizada"
echo "Fecha: $(date)"
```

```bash
# Hacer ejecutable
chmod +x scripts/full_sync.sh

# Ejecutar
./scripts/full_sync.sh
```

### Script de Verificación de Salud

Crea `scripts/health_check.sh`:

```bash
#!/bin/bash

# Script de verificación de salud
# Ejecutar: ./scripts/health_check.sh

echo "🏥 Verificación de salud del sistema"
echo "===================================="
echo ""

# Verificar servicio Django
echo "🔍 Servicio Django:"
systemctl is-active crushme && echo "  ✅ Activo" || echo "  ❌ Inactivo"

# Verificar Nginx
echo "🔍 Nginx:"
systemctl is-active nginx && echo "  ✅ Activo" || echo "  ❌ Inactivo"

# Verificar base de datos
echo "🔍 Base de datos:"
sudo -u postgres psql -c "SELECT 1" crushme_db > /dev/null 2>&1 && echo "  ✅ Conectada" || echo "  ❌ Error"

# Verificar espacio en disco
echo "🔍 Espacio en disco:"
df -h / | tail -1 | awk '{print "  Usado: "$5" de "$2}'

# Verificar memoria
echo "🔍 Memoria:"
free -h | grep Mem | awk '{print "  Usado: "$3" de "$2}'

echo ""
echo "✅ Verificación completada"
```

---

## 🎯 Resumen de Comandos Esenciales

### Sincronización Manual

```bash
# Sincronización completa
python manage.py sync_woocommerce_categories
python manage.py sync_woocommerce_products

# Producto específico (dropshipping)
python manage.py sync_woocommerce_products --product-id 48500

# Traducciones
python manage.py translate_products --new-only
python manage.py translate_categories --new-only
```

### Gestión de Servicios

```bash
# Reiniciar Django
sudo systemctl restart crushme

# Ver logs
sudo journalctl -u crushme -f

# Estado del sistema
sudo systemctl status crushme nginx
```

### Monitoreo

```bash
# Ver tareas programadas
python manage.py shell -c "from django_apscheduler.models import DjangoJob; [print(f'{j.name}: {j.next_run_time}') for j in DjangoJob.objects.all()]"

# Ver logs en tiempo real
tail -f /var/log/crushme/*.log
```

---

## ✅ Checklist de Producción

- [ ] Variables de entorno configuradas
- [ ] Base de datos PostgreSQL creada
- [ ] Migraciones ejecutadas
- [ ] Sincronización inicial completada
- [ ] Traducciones iniciales completadas
- [ ] Gunicorn configurado
- [ ] Systemd service creado y habilitado
- [ ] Nginx configurado
- [ ] SSL/HTTPS configurado
- [ ] Tareas automáticas verificadas
- [ ] Logs configurados
- [ ] Backups configurados
- [ ] Monitoreo activo

---

**🎉 ¡Sistema listo para producción!**
