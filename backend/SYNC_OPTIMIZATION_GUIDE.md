# Guía de Optimización - Sincronización WooCommerce

## 🚨 Problema Identificado

La sincronización de WooCommerce está consumiendo demasiados recursos del VPS, causando que el servidor se trabe.

## ✅ Soluciones Implementadas

### 1. NO Ejecutar Sincronización Automática

**IMPORTANTE:** La sincronización NO debe ejecutarse automáticamente en cada deploy o inicio del servidor.

#### ❌ NO HACER:
- NO agregar sincronización en `apps.py` con `ready()`
- NO usar APScheduler en el proceso principal de Django
- NO ejecutar sync en cada deploy automáticamente

#### ✅ SÍ HACER:
- Ejecutar sincronización MANUALMENTE cuando sea necesario
- Usar cron jobs con horarios de baja demanda (madrugada)
- Sincronizar solo lo necesario (stock, no productos completos)

### 2. Sincronización Manual (Recomendado)

```bash
# Solo cuando necesites actualizar productos (raro)
python manage.py sync_woocommerce --products

# Solo cuando necesites actualizar categorías (muy raro)
python manage.py sync_woocommerce --categories

# Actualización rápida de stock y precios (recomendado)
python manage.py sync_woocommerce --stock
```

### 3. Sincronización Programada (Opcional)

Si necesitas sincronización automática, usa cron en horarios de BAJA demanda:

```bash
# Editar crontab
crontab -e

# Agregar (ejecuta a las 3 AM, cuando hay menos usuarios)
0 3 * * * cd /home/cerrotico/work/crushme_project/backend && /home/cerrotico/work/crushme_project/backend/venv/bin/python manage.py sync_woocommerce --stock >> /tmp/sync.log 2>&1
```

### 4. Optimización del Servicio de Sincronización

El servicio ya está optimizado con:
- Paginación (100 items por página)
- Transacciones atómicas
- Manejo de errores sin detener todo el proceso
- Logs detallados

### 5. Configuración de Producción

#### Gunicorn (Recomendado para producción)

```bash
# Instalar gunicorn si no lo tienes
pip install gunicorn

# Ejecutar con workers limitados
gunicorn crushme_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile /tmp/gunicorn-access.log \
    --error-logfile /tmp/gunicorn-error.log \
    --log-level info
```

#### Systemd Service (Para mantener el servidor corriendo)

Crear archivo: `/etc/systemd/system/crushme.service`

```ini
[Unit]
Description=CrushMe Django Application
After=network.target

[Service]
Type=notify
User=cerrotico
Group=cerrotico
WorkingDirectory=/home/cerrotico/work/crushme_project/backend
Environment="PATH=/home/cerrotico/work/crushme_project/backend/venv/bin"
ExecStart=/home/cerrotico/work/crushme_project/backend/venv/bin/gunicorn \
    crushme_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --max-requests 1000 \
    --access-logfile /var/log/crushme/access.log \
    --error-logfile /var/log/crushme/error.log

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Activar servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl enable crushme
sudo systemctl start crushme
sudo systemctl status crushme
```

### 6. Monitoreo de Recursos

```bash
# Ver uso de CPU y memoria
htop

# Ver procesos de Python
ps aux | grep python

# Ver logs en tiempo real
tail -f /tmp/gunicorn-error.log
```

### 7. Estrategia de Sincronización Recomendada

#### Para Producción:

1. **Sincronización Inicial (Una sola vez):**
   ```bash
   python manage.py sync_woocommerce --full
   ```

2. **Actualizaciones Diarias (3 AM):**
   ```bash
   # Solo stock y precios (rápido, ~2-5 minutos)
   0 3 * * * cd /path/to/backend && venv/bin/python manage.py sync_woocommerce --stock
   ```

3. **Actualizaciones Semanales (Domingo 2 AM):**
   ```bash
   # Productos completos (lento, ~30-60 minutos)
   0 2 * * 0 cd /path/to/backend && venv/bin/python manage.py sync_woocommerce --products
   ```

4. **Actualizaciones Mensuales (Primer día del mes, 1 AM):**
   ```bash
   # Categorías (raro que cambien)
   0 1 1 * * cd /path/to/backend && venv/bin/python manage.py sync_woocommerce --categories
   ```

### 8. Alternativa: Sincronización On-Demand

En lugar de sincronización automática, usa sincronización bajo demanda:

- Los productos se consultan directamente de WooCommerce cuando se necesitan
- Se cachean en la base de datos local
- Solo se actualiza stock en tiempo real cuando el usuario ve el producto

**Esto ya está implementado en:**
- `get_product_detail_local()` - Consulta WooCommerce si no existe localmente
- Stock en tiempo real con parámetro `?real_time_stock=true`

### 9. Configuración de Base de Datos (Optimización)

Si usas SQLite en producción (NO recomendado), considera migrar a PostgreSQL:

```bash
# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib

# Crear base de datos
sudo -u postgres psql
CREATE DATABASE crushme_db;
CREATE USER crushme_user WITH PASSWORD 'tu_password_seguro';
GRANT ALL PRIVILEGES ON DATABASE crushme_db TO crushme_user;
\q

# Actualizar settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'crushme_db',
        'USER': 'crushme_user',
        'PASSWORD': 'tu_password_seguro',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 10. Límites de Recursos (Prevenir Overload)

Agregar a `settings.py`:

```python
# Límites de timeout para requests externos
WOOCOMMERCE_TIMEOUT = 30  # segundos
WOOCOMMERCE_MAX_RETRIES = 2

# Límites de paginación
WOOCOMMERCE_SYNC_BATCH_SIZE = 50  # Reducir de 100 a 50
```

## 📊 Resumen de Recomendaciones

### ✅ HACER:
1. Usar Gunicorn en producción (no `runserver`)
2. Limitar workers (2-4 máximo en VPS pequeño)
3. Sincronización MANUAL o en horarios de baja demanda
4. Monitorear recursos con `htop`
5. Usar PostgreSQL en lugar de SQLite
6. Implementar caché de productos

### ❌ NO HACER:
1. NO ejecutar sync en cada deploy
2. NO usar APScheduler en el proceso principal
3. NO sincronizar en horarios de alta demanda
4. NO usar `runserver` en producción
5. NO sincronizar todo el catálogo frecuentemente

## 🚀 Deploy Optimizado

```bash
# 1. Activar entorno virtual
cd /home/cerrotico/work/crushme_project/backend
source venv/bin/activate

# 2. Actualizar código
git pull

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Migraciones
python manage.py migrate

# 5. Recolectar estáticos
python manage.py collectstatic --noinput

# 6. Reiniciar servicio (NO sync automático)
sudo systemctl restart crushme

# 7. Verificar que está corriendo
sudo systemctl status crushme
```

## 📞 Troubleshooting

### Servidor se traba durante sync:

```bash
# Matar proceso de sync si está corriendo
pkill -f "sync_woocommerce"

# Reiniciar servidor
sudo systemctl restart crushme
```

### Ver qué está consumiendo recursos:

```bash
# CPU y memoria
htop

# Procesos de Python
ps aux | grep python | grep -v grep

# Espacio en disco
df -h

# Memoria disponible
free -h
```

### Logs para debugging:

```bash
# Logs de Django
tail -f /var/log/crushme/error.log

# Logs de sincronización
tail -f /tmp/sync.log

# Logs del sistema
sudo journalctl -u crushme -f
```

## 🎯 Conclusión

**La clave es NO ejecutar sincronización automática en cada deploy o inicio del servidor.**

Usa sincronización manual cuando sea necesario, o programa cron jobs en horarios de baja demanda (madrugada).

El servidor debe estar optimizado para servir requests de usuarios, no para sincronizar datos constantemente.
