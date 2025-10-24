# Sistema de Correos Electrónicos - CrushMe

## ✅ Configuración Completa

### 📧 Credenciales SMTP (GoDaddy)
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtpout.secureserver.net'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'support@crushme.com.co'
EMAIL_HOST_PASSWORD = 'cRu$hM3/2025'
DEFAULT_FROM_EMAIL = 'CrushMe Support <support@crushme.com.co>'
```

**Ubicación:** `crushme_project/settings.py` (líneas 163-171)

---

## 📂 Estructura de Archivos

### 1. Servicio Central de Emails
**Archivo:** `crushme_app/services/email_service.py`

**Funciones disponibles:**
- `send_email()` - Función genérica para enviar correos con templates
- `send_verification_code()` - Código de verificación de email
- `send_password_reset_code()` - Código de recuperación de contraseña
- `send_order_confirmation()` - Confirmación de pedido
- `send_gift_received_notification()` - Notificación de regalo recibido
- `send_gift_sent_confirmation()` - Confirmación de regalo enviado

### 2. Templates de Email
**Carpeta:** `email_templates/`
**Template base:** `email_templates/index.html`

Template HTML responsive con:
- Colores de marca CrushMe (rosa y morado)
- Soporte para variables dinámicas
- Diseño profesional y moderno
- Compatible con todos los clientes de email

---

## 🔔 Acciones que Detonan Envío de Correos

### 1. **Registro de Usuario** ✅
- **Endpoint:** `POST /api/auth/signup/`
- **Archivo:** `crushme_app/views/auth_views.py` (línea 65)
- **Correo enviado a:** Usuario que se registra
- **Contenido:** Código de verificación de 4 dígitos
- **Función:** `email_service.send_verification_code()`

**Ejemplo:**
```python
email_service.send_verification_code(
    to_email=user.email,
    code="1234",
    user_name="Juan Pérez"
)
```

---

### 2. **Reenviar Código de Verificación** ✅
- **Endpoint:** `POST /api/auth/resend-verification/`
- **Archivo:** `crushme_app/views/auth_views.py` (línea 183)
- **Correo enviado a:** Usuario que solicita nuevo código
- **Contenido:** Nuevo código de verificación de 4 dígitos
- **Función:** `email_service.send_verification_code()`

---

### 3. **Recuperación de Contraseña** ✅
- **Endpoint:** `POST /api/auth/forgot-password/`
- **Archivo:** `crushme_app/views/auth_views.py` (línea 474)
- **Correo enviado a:** Usuario que olvidó su contraseña
- **Contenido:** Código de recuperación de 4 dígitos
- **Función:** `email_service.send_password_reset_code()`

**Ejemplo:**
```python
email_service.send_password_reset_code(
    to_email=user.email,
    code="5678",
    user_name="María García"
)
```

---

### 4. **Confirmación de Compra (PayPal)** ✅
- **Endpoint:** `POST /api/orders/paypal/capture/`
- **Archivo:** `crushme_app/views/paypal_order_views.py` (línea 576)
- **Correo enviado a:** Cliente que realizó la compra
- **Contenido:** Número de orden, total, lista de productos
- **Función:** `email_service.send_order_confirmation()`

**Ejemplo:**
```python
email_service.send_order_confirmation(
    to_email="cliente@example.com",
    order_number="ORD-20250124-ABC123",
    total=150000.00,
    items=[
        {'name': 'Producto 1', 'quantity': 2},
        {'name': 'Producto 2', 'quantity': 1}
    ],
    user_name="Carlos Rodríguez"
)
```

---

### 5. **Confirmación de Compra (Wompi)** ✅
- **Endpoint:** `POST /api/orders/wompi/confirm/`
- **Archivo:** `crushme_app/views/order_helpers.py` (línea 143)
- **Correo enviado a:** Cliente que realizó la compra
- **Contenido:** Número de orden, total, lista de productos
- **Función:** `email_service.send_order_confirmation()`

---

### 6. **Notificación de Regalo Recibido** ✅
- **Endpoints:** 
  - `POST /api/orders/paypal/capture/` (con `is_gift: true`)
  - `POST /api/orders/wompi/confirm/` (con `is_gift: true`)
- **Archivos:** 
  - `crushme_app/views/paypal_order_views.py` (línea 591)
  - `crushme_app/views/order_helpers.py` (línea 158)
- **Correo enviado a:** Usuario que recibe el regalo
- **Contenido:** Nombre del remitente, mensaje personalizado, número de orden
- **Función:** `email_service.send_gift_received_notification()`

**Ejemplo:**
```python
email_service.send_gift_received_notification(
    to_email="destinatario@example.com",
    sender_name="Ana López",
    gift_message="¡Feliz cumpleaños! Espero que te guste 🎁",
    order_number="ORD-20250124-GIFT456",
    user_name="Pedro Martínez"
)
```

---

### 7. **Confirmación de Regalo Enviado** ✅
- **Endpoints:** 
  - `POST /api/orders/paypal/capture/` (con `is_gift: true`)
  - `POST /api/orders/wompi/confirm/` (con `is_gift: true`)
- **Archivos:** 
  - `crushme_app/views/paypal_order_views.py` (línea 601)
  - `crushme_app/views/order_helpers.py` (línea 168)
- **Correo enviado a:** Usuario que envió el regalo
- **Contenido:** Nombre del destinatario, número de orden, confirmación de envío
- **Función:** `email_service.send_gift_sent_confirmation()`

**Ejemplo:**
```python
email_service.send_gift_sent_confirmation(
    to_email="remitente@example.com",
    receiver_name="Pedro Martínez",
    order_number="ORD-20250124-GIFT456",
    user_name="Ana López"
)
```

---

## 📋 Resumen de Acciones

| # | Acción | Endpoint | Destinatario | Función |
|---|--------|----------|--------------|---------|
| 1 | Registro de usuario | `POST /api/auth/signup/` | Usuario nuevo | `send_verification_code()` |
| 2 | Reenviar verificación | `POST /api/auth/resend-verification/` | Usuario | `send_verification_code()` |
| 3 | Recuperar contraseña | `POST /api/auth/forgot-password/` | Usuario | `send_password_reset_code()` |
| 4 | Compra PayPal | `POST /api/orders/paypal/capture/` | Comprador | `send_order_confirmation()` |
| 5 | Compra Wompi | `POST /api/orders/wompi/confirm/` | Comprador | `send_order_confirmation()` |
| 6 | Regalo recibido | PayPal/Wompi (gift) | Destinatario | `send_gift_received_notification()` |
| 7 | Regalo enviado | PayPal/Wompi (gift) | Remitente | `send_gift_sent_confirmation()` |

---

## 🧪 Pruebas

### Probar envío de correo de verificación:
```bash
# Activar entorno virtual
source venv/bin/activate

# Registrar un usuario nuevo
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### Verificar logs:
```bash
# Los logs mostrarán:
✅ Email sent successfully to ['test@example.com']: Verifica tu correo - CrushMe
📧 Order confirmation email sent to cliente@example.com
📧 Gift received notification sent to destinatario@example.com
```

---

## 🔧 Mantenimiento

### Agregar nuevo tipo de correo:

1. **Agregar método en `email_service.py`:**
```python
@staticmethod
def send_shipping_notification(to_email, order_number, tracking_number, user_name=None):
    context = {
        'title': '¡Tu pedido ha sido enviado!',
        'message': f'Tu pedido {order_number} está en camino.<br>Número de seguimiento: {tracking_number}',
        'button_text': 'Rastrear pedido',
        'button_url': f'{settings.FRONTEND_URL}/track/{tracking_number}'
    }
    
    return EmailService.send_email(
        to_email=to_email,
        subject=f'Pedido enviado #{order_number} - CrushMe',
        context=context
    )
```

2. **Usar en el endpoint correspondiente:**
```python
from ..services.email_service import email_service

email_service.send_shipping_notification(
    to_email=order.email,
    order_number=order.order_number,
    tracking_number="TRACK123456",
    user_name=order.name
)
```

---

## 📝 Notas Importantes

1. **Todos los correos se envían desde:** `support@crushme.com.co`
2. **Template actual:** `email_templates/index.html` (temporal para todos)
3. **Próximos pasos:** Crear templates específicos para cada tipo de correo
4. **Logs:** Todos los envíos se registran en los logs de Django
5. **Errores:** Si falla el envío de correo, NO falla la operación principal (orden, registro, etc.)

---

## ✅ Estado Actual

- ✅ Configuración SMTP completa (GoDaddy)
- ✅ Servicio central de emails (`email_service.py`)
- ✅ Template HTML base (`index.html`)
- ✅ 7 tipos de correos implementados
- ✅ Integración en todos los endpoints críticos
- ✅ Logs detallados de envíos
- ✅ Manejo de errores robusto

**Sistema 100% funcional y listo para producción** 🚀
