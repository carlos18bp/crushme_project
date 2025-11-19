# 🔴 Redis Setup - CRÍTICO para Webhooks en Producción

## ❌ Problema Actual:

El webhook de Wompi no encuentra los datos porque:

1. **Sin Redis:** Django usa cache en memoria local (LocMemCache)
2. **Múltiples workers:** Cada worker tiene su propia memoria
3. **Worker 1** guarda el cache → Solo Worker 1 lo ve
4. **Webhook llega a Worker 2** → No encuentra el cache ❌

## ✅ Solución: Instalar Redis

### 1. Instalar Redis en el Servidor

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# Iniciar Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verificar que está corriendo
redis-cli ping
# Debe responder: PONG
```

### 2. Instalar Cliente de Python

```bash
cd /home/cerrotico/work/crushme_project/backend
source venv/bin/activate
pip install django-redis redis
pip freeze > requirements.txt
```

### 3. Configurar Django (YA HECHO)

El archivo `settings.py` ya está configurado:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'crushme',
        'TIMEOUT': 3600,
    }
}
```

### 4. Reiniciar Django

```bash
# Si usas systemd
sudo systemctl restart crushme-backend

# O si usas supervisor
sudo supervisorctl restart crushme-backend

# O si es desarrollo
# Ctrl+C y luego:
python manage.py runserver
```

---

## 🧪 Verificar que Funciona:

### Test 1: Verificar Redis

```bash
redis-cli
> ping
PONG
> keys *
(empty array or existing keys)
> exit
```

### Test 2: Verificar Django Cache

```bash
python manage.py shell
```

```python
from django.core.cache import cache

# Guardar algo
cache.set('test_key', 'test_value', 60)

# Leer
print(cache.get('test_key'))  # Debe mostrar: test_value

# Verificar en Redis directamente
exit()
```

```bash
redis-cli
> keys crushme:*
# Debe mostrar: "crushme:1:test_key"
```

### Test 3: Hacer una Compra Real

1. Crear transacción desde frontend
2. Ver logs del backend:
   ```
   💾 [WOMPI] Stored order data in cache for reference: ORD579445281WTDEX
   ```

3. Verificar en Redis:
   ```bash
   redis-cli
   > keys crushme:*wompi_order_data*
   # Debe mostrar el key
   
   > get "crushme:1:wompi_order_data_ORD579445281WTDEX"
   # Debe mostrar los datos JSON
   ```

4. Completar pago en Wompi

5. Ver logs del webhook:
   ```
   📬 [WOMPI WEBHOOK] Received webhook
   ✅ [WOMPI WEBHOOK] Found order data in cache  ← ESTO DEBE APARECER
   ✅ [WOMPI WEBHOOK] Order processed successfully
   ```

---

## 🔧 Configuración de Producción:

### Redis con Contraseña (Recomendado)

```bash
# Editar configuración de Redis
sudo nano /etc/redis/redis.conf

# Buscar y descomentar:
requirepass tu_password_seguro_aqui

# Reiniciar Redis
sudo systemctl restart redis-server
```

### Actualizar Django

```python
# settings.py o .env
REDIS_URL=redis://:tu_password_seguro_aqui@127.0.0.1:6379/1
```

### Redis Remoto (Opcional)

Si Redis está en otro servidor:

```python
REDIS_URL=redis://:password@redis-server.com:6379/1
```

---

## 📊 Monitoreo de Redis:

### Ver todas las keys:

```bash
redis-cli
> keys crushme:*
```

### Ver datos del webhook:

```bash
redis-cli
> keys *wompi_order_data*
> get "crushme:1:wompi_order_data_ORD579445281WTDEX"
```

### Ver memoria usada:

```bash
redis-cli
> info memory
```

### Limpiar cache (si es necesario):

```bash
redis-cli
> flushdb  # Limpia la base de datos actual
> flushall # Limpia todas las bases de datos
```

---

## ⚠️ IMPORTANTE:

### Sin Redis:
- ❌ Webhooks fallan en producción
- ❌ Cache no compartido entre workers
- ❌ Datos se pierden al reiniciar

### Con Redis:
- ✅ Webhooks funcionan correctamente
- ✅ Cache compartido entre todos los workers
- ✅ Datos persisten hasta expirar (1 hora)
- ✅ Rápido y eficiente

---

## 🚀 Checklist de Instalación:

- [ ] Redis instalado en el servidor
- [ ] Redis corriendo (`redis-cli ping` → PONG)
- [ ] django-redis instalado (`pip install django-redis`)
- [ ] settings.py configurado (ya hecho)
- [ ] Django reiniciado
- [ ] Test de cache exitoso
- [ ] Compra de prueba exitosa
- [ ] Webhook recibido y procesado

---

## 🆘 Troubleshooting:

### Error: "Connection refused"

```bash
# Verificar que Redis está corriendo
sudo systemctl status redis-server

# Si no está corriendo
sudo systemctl start redis-server
```

### Error: "NOAUTH Authentication required"

Redis tiene contraseña configurada. Actualiza REDIS_URL:

```python
REDIS_URL=redis://:tu_password@127.0.0.1:6379/1
```

### Error: "No module named 'redis'"

```bash
pip install redis django-redis
```

---

## 📚 Referencias:

- [Django Redis Documentation](https://github.com/jazzband/django-redis)
- [Redis Documentation](https://redis.io/documentation)
- [Redis Quick Start](https://redis.io/docs/getting-started/)
