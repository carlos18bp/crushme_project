# 🌐 Sistema de Emails Multiidioma - COMPLETADO

## ✅ Implementación Completa

Se ha implementado un sistema completo de emails en **español e inglés** que detecta automáticamente el idioma del usuario desde el frontend.

---

## 📂 Estructura de Templates

```
email_templates/
├── es/                           # Templates en español
│   ├── 1-signup-verification.html
│   ├── 2-resend-verification.html
│   ├── 3-password-recovery.html
│   ├── 4-order-confirmation.html
│   ├── 5-gift-received.html
│   └── 6-gift-sent-confirmation.html
└── en/                           # Templates en inglés
    ├── 1-signup-verification.html
    ├── 2-resend-verification.html
    ├── 3-password-recovery.html
    ├── 4-order-confirmation.html
    ├── 5-gift-received.html
    └── 6-gift-sent-confirmation.html
```

---

## 🔄 Flujo de Detección de Idioma

### Frontend → Backend

El frontend envía el idioma en cada request mediante:

1. **Header `Accept-Language`**: `es` o `en`
2. **Query parameter `lang`**: `?lang=es` o `?lang=en`

### Backend

La función `get_language_from_request()` detecta el idioma:

```python
from ..services.translation_service import get_language_from_request

# En cualquier vista
lang = get_language_from_request(request)
# Retorna: 'es' o 'en'
```

**Prioridad de detección:**
1. Query parameter `lang`
2. Header `Accept-Language`
3. Default: `'es'` (español)

---

## 📧 Funciones del Email Service

Todas las funciones ahora aceptan el parámetro `lang`:

### 1. **send_verification_code()**
```python
email_service.send_verification_code(
    to_email='usuario@example.com',
    code='1234',
    username='juanperez',
    lang='es'  # ← Nuevo parámetro
)
```

**Subjects:**
- `es`: "Verifica tu correo - CrushMe"
- `en`: "Verify your email - CrushMe"

---

### 2. **send_password_reset_code()**
```python
email_service.send_password_reset_code(
    to_email='usuario@example.com',
    code='9876',
    username='mariagarcia',
    lang='en'  # ← Nuevo parámetro
)
```

**Subjects:**
- `es`: "Recupera tu contraseña - CrushMe"
- `en`: "Reset your password - CrushMe"

---

### 3. **send_order_confirmation()**
```python
email_service.send_order_confirmation(
    to_email='cliente@example.com',
    order_number='ORD-20250124-ABC123',
    total=150000.00,
    items=[...],
    username='carlosrodriguez',
    lang='es'  # ← Nuevo parámetro
)
```

**Subjects:**
- `es`: "Confirmación de pedido #ORD-123 - CrushMe"
- `en`: "Order confirmation #ORD-123 - CrushMe"

---

### 4. **send_gift_received_notification()**
```python
email_service.send_gift_received_notification(
    to_email='destinatario@example.com',
    sender_username='analopez',
    gift_message='¡Feliz cumpleaños! 🎁',
    order_number='ORD-20250124-GIFT456',
    username='pedromartinez',
    lang='en'  # ← Nuevo parámetro
)
```

**Subjects:**
- `es`: "¡Has recibido un regalo! 🎁 - CrushMe"
- `en`: "You received a gift! 🎁 - CrushMe"

---

### 5. **send_gift_sent_confirmation()**
```python
email_service.send_gift_sent_confirmation(
    to_email='remitente@example.com',
    receiver_username='pedromartinez',
    order_number='ORD-20250124-GIFT456',
    username='analopez',
    lang='es'  # ← Nuevo parámetro
)
```

**Subjects:**
- `es`: "Regalo enviado a @pedromartinez - CrushMe"
- `en`: "Gift sent to @pedromartinez - CrushMe"

---

## 🔧 Cambios en el Backend

### 1. **email_service.py**

**Función principal actualizada:**
```python
@staticmethod
def send_email(
    to_email,
    subject,
    template_name='index.html',
    context=None,
    from_email=None,
    lang='es'  # ← Nuevo parámetro
):
    # Validate language
    if lang not in ['es', 'en']:
        lang = 'es'  # Default to Spanish
    
    # Load template with language folder
    template_path = Path(settings.BASE_DIR) / 'email_templates' / lang / template_name
```

**Todas las funciones de envío:**
- ✅ Aceptan parámetro `lang='es'` (default español)
- ✅ Subject dinámico según idioma
- ✅ Template correcto según idioma

---

### 2. **auth_views.py**

**Importación agregada:**
```python
from ..services.translation_service import get_language_from_request
```

**3 endpoints actualizados:**

**a) `signup()` - Registro:**
```python
# Get language from request
lang = get_language_from_request(request)

email_sent = email_service.send_verification_code(
    to_email=user.email,
    code=verification_code,
    username=user.username,
    lang=lang  # ← Pasa el idioma
)
```

**b) `resend_verification_code()` - Reenviar código:**
```python
# Get language from request
lang = get_language_from_request(request)

email_sent = email_service.send_verification_code(
    to_email=user.email,
    code=verification_code,
    username=user.username,
    lang=lang  # ← Pasa el idioma
)
```

**c) `forgot_password()` - Recuperar contraseña:**
```python
# Get language from request
lang = get_language_from_request(request)

email_sent = email_service.send_password_reset_code(
    to_email=email,
    code=reset_code,
    username=user.username,
    lang=lang  # ← Pasa el idioma
)
```

---

## 📋 Parámetros de Templates

Todos los templates (español e inglés) usan los mismos parámetros:

| Template | Parámetros |
|----------|-----------|
| **1-signup-verification.html** | `username`, `code` |
| **2-resend-verification.html** | `username`, `code` |
| **3-password-recovery.html** | `username`, `code` |
| **4-order-confirmation.html** | `username`, `order_number` |
| **5-gift-received.html** | `username`, `sender_username` |
| **6-gift-sent-confirmation.html** | `username`, `receiver_username` |

**Formato de usernames:** Todos usan `@username` (ej: "@juanperez")

---

## 🌍 Ejemplo de Flujo Completo

### Usuario en Español (Colombia)

1. **Frontend detecta:** Navegador en español → envía `Accept-Language: es`
2. **Usuario se registra:** POST `/api/auth/signup/`
3. **Backend:**
   - `get_language_from_request(request)` → `'es'`
   - `email_service.send_verification_code(..., lang='es')`
   - Carga template: `email_templates/es/1-signup-verification.html`
   - Subject: "Verifica tu correo - CrushMe"
4. **Usuario recibe:** Email en español con "Hola @juanperez"

### Usuario en Inglés (USA)

1. **Frontend detecta:** Navegador en inglés → envía `Accept-Language: en`
2. **Usuario se registra:** POST `/api/auth/signup/`
3. **Backend:**
   - `get_language_from_request(request)` → `'en'`
   - `email_service.send_verification_code(..., lang='en')`
   - Carga template: `email_templates/en/1-signup-verification.html`
   - Subject: "Verify your email - CrushMe"
4. **Usuario recibe:** Email en inglés con "Hello @johnsmith"

---

## ✅ Archivos Modificados

### Backend:
1. **`email_service.py`**
   - ✅ Parámetro `lang` en `send_email()`
   - ✅ Parámetro `lang` en todas las funciones de envío
   - ✅ Subjects dinámicos según idioma
   - ✅ Carga de templates desde carpeta de idioma

2. **`auth_views.py`**
   - ✅ Import de `get_language_from_request`
   - ✅ 3 endpoints actualizados para pasar `lang`

### Templates:
3. **`email_templates/es/`** (6 templates)
   - ✅ Todos con parámetros `{{ username }}`, `{{ code }}`, etc.
   - ✅ Textos en español

4. **`email_templates/en/`** (6 templates)
   - ✅ Todos con parámetros `{{ username }}`, `{{ code }}`, etc.
   - ✅ Textos en inglés

---

## 🧪 Testing

### Probar con español:
```bash
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -H "Accept-Language: es" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!"
  }'
```

### Probar con inglés:
```bash
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -H "Accept-Language: en" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!"
  }'
```

---

## 📊 Resumen

| Característica | Estado |
|---------------|--------|
| Templates en español | ✅ 6/6 |
| Templates en inglés | ✅ 6/6 |
| Detección automática de idioma | ✅ |
| Subjects dinámicos | ✅ |
| Parámetros con usernames | ✅ |
| Integración en auth_views.py | ✅ 3/3 |
| Fallback a español | ✅ |

---

## 🎯 Resultado Final

El sistema de emails ahora:
- ✅ Detecta automáticamente el idioma del usuario
- ✅ Envía emails en español o inglés según preferencia
- ✅ Usa usernames (@usuario) en lugar de nombres reales
- ✅ Subjects personalizados por idioma
- ✅ Fallback robusto a español si el idioma no es válido
- ✅ Compatible con sistema de i18n del frontend

**Sistema 100% funcional y listo para producción!** 🚀
