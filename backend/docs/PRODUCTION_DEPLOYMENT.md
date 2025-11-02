# Guía de Despliegue a Producción - CrushMe

## Configuración de Entorno de Producción

### 1. Variables de Entorno en `settings.py`

El sistema ya está configurado para detectar automáticamente el entorno mediante el flag `PRODUCTION`:

```python
# Production/Development environment flag
PRODUCTION = False  # ⬅️ Cambiar a True en producción

# Frontend URLs based on environment
if PRODUCTION:
    FRONTEND_URL = 'https://crushme.com.co'
else:
    FRONTEND_URL = 'http://localhost:5173'
```

### 2. Cambios Necesarios para Producción

#### A. En `settings.py` cambiar:

```python
# ANTES (Desarrollo):
DEBUG = True
PRODUCTION = False
ALLOWED_HOSTS = []
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

# DESPUÉS (Producción):
DEBUG = False
PRODUCTION = True
ALLOWED_HOSTS = ['crushme.com.co', 'www.crushme.com.co', 'api.crushme.com.co']
CORS_ALLOWED_ORIGINS = [
    'https://crushme.com.co',
    'https://www.crushme.com.co',
]
```

#### B. Configurar Base de Datos de Producción:

```python
# Reemplazar SQLite por PostgreSQL en producción
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'crushme_db'),
        'USER': os.environ.get('DB_USER', 'crushme_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

#### C. Configurar Credenciales Sensibles:

```python
# Usar variables de entorno en producción
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'default-secret-key')

# PayPal
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')
PAYPAL_MODE = 'live'  # Cambiar de 'sandbox' a 'live'

# Wompi
WOMPI_PUBLIC_KEY = os.environ.get('WOMPI_PUBLIC_KEY')
WOMPI_PRIVATE_KEY = os.environ.get('WOMPI_PRIVATE_KEY')
WOMPI_EVENTS_SECRET = os.environ.get('WOMPI_EVENTS_SECRET')
WOMPI_INTEGRITY_KEY = os.environ.get('WOMPI_INTEGRITY_KEY')
WOMPI_BASE_URL = 'https://production.wompi.co/v1'  # URL de producción
WOMPI_ENVIRONMENT = 'production'

# WooCommerce
WOOCOMMERCE_CONSUMER_KEY = os.environ.get('WOOCOMMERCE_CONSUMER_KEY')
WOOCOMMERCE_CONSUMER_SECRET = os.environ.get('WOOCOMMERCE_CONSUMER_SECRET')
```

### 3. Funcionalidades que Usan FRONTEND_URL

Las siguientes funcionalidades ya están configuradas para usar `settings.FRONTEND_URL`:

#### A. **Wishlist Public URLs**
Archivo: `crushme_app/models/wishlist.py`

```python
@property
def public_url(self):
    """Get the public sharing URL"""
    from django.conf import settings
    frontend_url = settings.FRONTEND_URL
    username = self.user.username or self.user.email.split('@')[0]
    return f"{frontend_url}/@{username}/{self.id}"
```

**Resultado:**
- Desarrollo: `http://localhost:5173/@username/1`
- Producción: `https://crushme.com.co/@username/1`

#### B. **Emails con Links**
Si hay emails que incluyen links al frontend, también deben usar `settings.FRONTEND_URL`.

### 4. Archivos Estáticos y Media

```python
# Configurar para servir archivos estáticos en producción
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'

# Usar un CDN o S3 en producción (recomendado)
# AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

### 5. Seguridad Adicional en Producción

```python
# Agregar en settings.py para producción
if PRODUCTION:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

### 6. Checklist de Despliegue

- [ ] Cambiar `PRODUCTION = True` en settings.py
- [ ] Cambiar `DEBUG = False`
- [ ] Configurar `ALLOWED_HOSTS` con dominios de producción
- [ ] Actualizar `CORS_ALLOWED_ORIGINS` con URLs de producción
- [ ] Cambiar base de datos a PostgreSQL
- [ ] Configurar variables de entorno para credenciales sensibles
- [ ] Cambiar PayPal a modo 'live'
- [ ] Cambiar Wompi a URLs de producción
- [ ] Configurar SECRET_KEY único y seguro
- [ ] Ejecutar `python manage.py collectstatic`
- [ ] Ejecutar migraciones: `python manage.py migrate`
- [ ] Configurar servidor web (Nginx/Apache)
- [ ] Configurar HTTPS con certificado SSL
- [ ] Configurar backup automático de base de datos
- [ ] Configurar logs de producción
- [ ] Probar links de wishlist públicos

### 7. Verificación de URLs

Para verificar que las URLs se generan correctamente:

```python
# En Django shell
python manage.py shell

from crushme_app.models import WishList
from django.conf import settings

print(f"PRODUCTION: {settings.PRODUCTION}")
print(f"FRONTEND_URL: {settings.FRONTEND_URL}")

wishlist = WishList.objects.first()
if wishlist:
    print(f"Public URL: {wishlist.public_url}")
    print(f"Shareable Path: {wishlist.shareable_path}")
```

**Resultado esperado:**
- Desarrollo: `http://localhost:5173/@username/1`
- Producción: `https://crushme.com.co/@username/1`

### 8. Testing en Staging

Antes de desplegar a producción, se recomienda:

1. Crear un entorno de staging con `PRODUCTION = True`
2. Probar todas las funcionalidades:
   - Links de wishlist públicos
   - Compartir wishlists
   - Comprar desde wishlist
   - Emails con links
3. Verificar que todos los links apunten a `crushme.com.co`

### 9. Rollback Plan

Si algo falla en producción:

1. Cambiar `PRODUCTION = False` temporalmente
2. Revisar logs: `tail -f /var/log/crushme/error.log`
3. Verificar configuración de base de datos
4. Verificar CORS y ALLOWED_HOSTS

### 10. Monitoreo Post-Despliegue

Verificar:
- [ ] Links de wishlist funcionan correctamente
- [ ] Emails se envían con URLs correctas
- [ ] No hay errores 500 en logs
- [ ] CORS funciona correctamente
- [ ] Pagos funcionan (PayPal y Wompi)
- [ ] Sincronización con WooCommerce funciona

## Resumen

✅ **El código ya está preparado para producción**
- Usa `settings.FRONTEND_URL` dinámicamente
- Cambia automáticamente según el flag `PRODUCTION`
- No hay URLs hardcodeadas en el código

🔧 **Solo necesitas cambiar en `settings.py`:**
```python
PRODUCTION = True
DEBUG = False
ALLOWED_HOSTS = ['crushme.com.co', 'www.crushme.com.co']
CORS_ALLOWED_ORIGINS = ['https://crushme.com.co', 'https://www.crushme.com.co']
```

🎉 **Todos los links de wishlist cambiarán automáticamente a `https://crushme.com.co`**
