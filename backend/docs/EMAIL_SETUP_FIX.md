# Solución al Error 500 en Registro (signup)

## Problema Identificado

El error 500 "Internal Server Error" que ocurre al registrarse se debe a un **fallo en la configuración del servidor SMTP** para envío de emails.

### Detalles Técnicos

1. El proceso de registro funciona correctamente (crear usuario, generar código)
2. El error ocurre al intentar enviar el email de verificación
3. Error SMTP específico: `SMTPServerDisconnected: Connection unexpectedly closed`

### Stack Trace del Error

```
File "/django/core/mail/backends/smtp.py", line 95, in open
    self.connection.login(self.username, self.password)
smtplib.SMTPServerDisconnected: Connection unexpectedly closed
```

## Solución Implementada (Desarrollo)

Se modificó `crushme_project/settings.py` para usar el backend de consola en modo DEBUG:

```python
if DEBUG:
    # En desarrollo, muestra los emails en la consola
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # En producción, usa SMTP
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # ... configuración SMTP ...
```

**Beneficios de esta solución:**
- ✅ El registro ahora funciona sin errores
- ✅ Los códigos de verificación se muestran en la consola del servidor
- ✅ Perfecto para desarrollo y testing
- ✅ No requiere configuración SMTP funcional

## Soluciones para Producción

Para que los emails funcionen en producción, debes verificar con tu proveedor de hosting:

### Opción 1: Verificar Credenciales Actuales (GoDaddy/SecureServer)

```python
EMAIL_HOST = 'smtpout.secureserver.net'
EMAIL_PORT = 465  # También puedes probar puerto 587
EMAIL_USE_SSL = True  # Con puerto 465
EMAIL_USE_TLS = False  # Cambiar a True si usas puerto 587
EMAIL_HOST_USER = 'support@chrushme.com.co'
EMAIL_HOST_PASSWORD = 'tu_contraseña_correcta'
```

**Pasos a verificar:**
1. Confirma que la cuenta `support@chrushme.com.co` existe y está activa
2. Verifica que la contraseña es correcta
3. Asegúrate de que el dominio `chrushme.com.co` está verificado
4. Revisa si necesitas habilitar "acceso menos seguro" o generar una contraseña de aplicación

### Opción 2: Usar Gmail (Recomendado para Testing)

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'tu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-app-password'  # Requiere autenticación de 2 factores
DEFAULT_FROM_EMAIL = 'CrushMe <tu-email@gmail.com>'
```

**Nota:** Gmail requiere generar una "Contraseña de Aplicación" desde la configuración de tu cuenta.

### Opción 3: Servicios de Email Transaccional (Recomendado para Producción)

Servicios más confiables y con mejor deliverability:

#### SendGrid
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'tu-sendgrid-api-key'
```

#### Mailgun
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'postmaster@tu-dominio.mailgun.org'
EMAIL_HOST_PASSWORD = 'tu-mailgun-password'
```

#### Amazon SES
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-aws-smtp-username'
EMAIL_HOST_PASSWORD = 'tu-aws-smtp-password'
```

## Testing de Configuración Email

Para probar tu configuración de email, ejecuta:

```bash
cd /home/cerrotico/work/crushme_project/backend
source venv/bin/activate
python manage.py shell
```

Luego en el shell de Django:

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject='Test Email',
    message='Si recibes este email, la configuración funciona!',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['tu-email@example.com'],
    fail_silently=False,
)
```

Si no hay errores, tu configuración está correcta.

## Variables de Entorno (Recomendado)

Para mayor seguridad, usa variables de entorno para credenciales:

```python
# En settings.py
import os

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'support@chrushme.com.co')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
```

Luego crea un archivo `.env`:
```bash
EMAIL_HOST_USER=support@chrushme.com.co
EMAIL_HOST_PASSWORD=tu_contraseña_real
```

Y carga las variables con `python-dotenv`.

## Resumen

✅ **Solución implementada:** Backend de consola para desarrollo  
⚠️ **Pendiente:** Configurar SMTP para producción  
📝 **Recomendación:** Usar servicio de email transaccional como SendGrid o Mailgun

## Fecha de Solución
3 de Octubre, 2025



