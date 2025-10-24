# 🌍 Emails Bilingües - CrushMe

Sistema completo de emails en **Español** e **Inglés** con diseño minimalista y branding de CrushMe.

---

## 📁 Estructura de Archivos

```
emails/
├── emails/
│   ├── es/                          # Versión en Español
│   │   ├── 1-signup-verification.tsx
│   │   ├── 2-resend-verification.tsx
│   │   ├── 3-password-recovery.tsx
│   │   ├── 4-order-confirmation.tsx
│   │   ├── 5-gift-received.tsx
│   │   └── 6-gift-sent-confirmation.tsx
│   │
│   └── en/                          # Versión en Inglés
│       ├── 1-signup-verification.tsx
│       ├── 2-resend-verification.tsx
│       ├── 3-password-recovery.tsx
│       ├── 4-order-confirmation.tsx
│       ├── 5-gift-received.tsx
│       └── 6-gift-sent-confirmation.tsx
│
└── out/                             # HTMLs exportados
    ├── es/                          # HTMLs en Español
    │   ├── 1-signup-verification.html
    │   ├── 2-resend-verification.html
    │   ├── 3-password-recovery.html
    │   ├── 4-order-confirmation.html
    │   ├── 5-gift-received.html
    │   └── 6-gift-sent-confirmation.html
    │
    ├── en/                          # HTMLs en Inglés
    │   ├── 1-signup-verification.html
    │   ├── 2-resend-verification.html
    │   ├── 3-password-recovery.html
    │   ├── 4-order-confirmation.html
    │   ├── 5-gift-received.html
    │   └── 6-gift-sent-confirmation.html
    │
    └── static/
        └── BUY.png
```

---

## 📧 Emails Disponibles

### Español (es/)

| # | Nombre | Descripción |
|---|--------|-------------|
| 1 | `signup-verification` | Código de verificación de registro |
| 2 | `resend-verification` | Reenviar código de verificación |
| 3 | `password-recovery` | Recuperación de contraseña |
| 4 | `order-confirmation` | Confirmación de compra |
| 5 | `gift-received` | Notificación de regalo recibido |
| 6 | `gift-sent-confirmation` | Confirmación de regalo enviado |

### English (en/)

| # | Name | Description |
|---|------|-------------|
| 1 | `signup-verification` | Registration verification code |
| 2 | `resend-verification` | Resend verification code |
| 3 | `password-recovery` | Password recovery |
| 4 | `order-confirmation` | Order confirmation |
| 5 | `gift-received` | Gift received notification |
| 6 | `gift-sent-confirmation` | Gift sent confirmation |

---

## 🎨 Características de Diseño

✅ **Logo público:** `https://crushme.com.co/static/frontend/BUY.png`  
✅ **Rosa tenue:** `#D689A2` en títulos  
✅ **Rosa fuerte:** `#FF3FD5` en códigos y destacados  
✅ **Sin emojis grandes** en títulos  
✅ **Sin alertas amarillas** - Texto simple y limpio  
✅ **Diseño minimalista** inspirado en Tidal  
✅ **Responsive** - Se adapta a móvil y desktop  
✅ **Compatible** con todos los clientes de email  

---

## 🔧 Integración con Django Backend

### Estructura Recomendada

```python
# crushme_app/services/email_service.py

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

class EmailService:
    def send_verification_code(self, to_email, code, user_name, language='es'):
        """Enviar código de verificación en el idioma especificado"""
        
        # Seleccionar template según idioma
        template_path = f'emails/{language}/1-signup-verification.html'
        
        # Asunto según idioma
        subjects = {
            'es': 'Verifica tu cuenta en CrushMe',
            'en': 'Verify your CrushMe account'
        }
        
        html_content = render_to_string(template_path, {
            'user_name': user_name,
            'code': code,
        })
        
        send_mail(
            subject=subjects.get(language, subjects['en']),
            message=f'Your verification code is: {code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_content,
        )
    
    def send_order_confirmation(self, to_email, order_number, total, items, user_name, language='es'):
        """Enviar confirmación de orden"""
        
        template_path = f'emails/{language}/4-order-confirmation.html'
        
        subjects = {
            'es': f'Confirmación de orden {order_number} - CrushMe',
            'en': f'Order confirmation {order_number} - CrushMe'
        }
        
        html_content = render_to_string(template_path, {
            'user_name': user_name,
            'order_number': order_number,
            'total': total,
            'items': items,
        })
        
        send_mail(
            subject=subjects.get(language, subjects['en']),
            message=f'Your order {order_number} has been confirmed.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_content,
        )
    
    def send_gift_received_notification(self, to_email, sender_name, gift_message, order_number, user_name, language='es'):
        """Notificar regalo recibido"""
        
        template_path = f'emails/{language}/5-gift-received.html'
        
        subjects = {
            'es': f'¡{sender_name} te ha enviado un regalo! - CrushMe',
            'en': f'{sender_name} sent you a gift! - CrushMe'
        }
        
        html_content = render_to_string(template_path, {
            'user_name': user_name,
            'sender_name': sender_name,
            'gift_message': gift_message,
            'order_number': order_number,
        })
        
        send_mail(
            subject=subjects.get(language, subjects['en']),
            message=f'{sender_name} sent you a gift.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_content,
        )

# Instancia global
email_service = EmailService()
```

---

## 🌐 Detección Automática de Idioma

### Opción 1: Desde el perfil del usuario

```python
# En tu vista o serializer
user = request.user
language = user.preferred_language or 'es'  # Default a español

email_service.send_verification_code(
    to_email=user.email,
    code='1234',
    user_name=user.first_name,
    language=language  # 'es' o 'en'
)
```

### Opción 2: Desde el header Accept-Language

```python
from django.utils.translation import get_language_from_request

def send_verification_email(request, user, code):
    # Detectar idioma del request
    language = get_language_from_request(request)
    
    # Mapear a 'es' o 'en'
    if language.startswith('es'):
        lang = 'es'
    else:
        lang = 'en'
    
    email_service.send_verification_code(
        to_email=user.email,
        code=code,
        user_name=user.first_name,
        language=lang
    )
```

### Opción 3: Desde geolocalización (como en el frontend)

```python
# Basado en el país del usuario
def get_user_language(country_code):
    spanish_countries = ['AR', 'BO', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 
                        'SV', 'GQ', 'GT', 'HN', 'MX', 'NI', 'PA', 'PY', 
                        'PE', 'ES', 'UY', 'VE']
    
    return 'es' if country_code in spanish_countries else 'en'

# Uso
language = get_user_language(user.country_code)
email_service.send_verification_code(..., language=language)
```

---

## 📊 Parámetros por Email

### Autenticación (1, 2, 3)
```python
{
    'user_name': str,  # Nombre del usuario
    'code': str,       # Código de 4 dígitos
}
```

### Orden (4)
```python
{
    'user_name': str,
    'order_number': str,
    'total': float,
    'items': [
        {'name': str, 'quantity': int},
        ...
    ]
}
```

### Regalo Recibido (5)
```python
{
    'user_name': str,
    'sender_name': str,
    'gift_message': str,  # Opcional
    'order_number': str,
}
```

### Regalo Enviado (6)
```python
{
    'user_name': str,
    'receiver_name': str,
    'order_number': str,
}
```

---

## 🚀 Comandos Útiles

### Previsualizar emails
```bash
cd /home/cerrotico/work/crushme_project/emails
npm run dev
```
Abre: http://localhost:3000

### Exportar HTMLs
```bash
npm run export
```
Los HTMLs se generan en `/out/es/` y `/out/en/`

### Copiar HTMLs al backend Django
```bash
# Desde la carpeta emails/
cp -r out/es/* /path/to/django/templates/emails/es/
cp -r out/en/* /path/to/django/templates/emails/en/
```

---

## ✅ Checklist de Integración

### Frontend
- [x] Detectar idioma del usuario (i18nStore)
- [x] Enviar header `Accept-Language` en requests
- [ ] Pasar idioma al crear órdenes/gifts

### Backend
- [ ] Copiar HTMLs a `templates/emails/es/` y `templates/emails/en/`
- [ ] Implementar `EmailService` con parámetro `language`
- [ ] Detectar idioma del usuario (perfil, header o geo)
- [ ] Usar template correcto según idioma
- [ ] Configurar asuntos en ambos idiomas

### Testing
- [ ] Probar cada email en español
- [ ] Probar cada email en inglés
- [ ] Verificar que el logo se muestre correctamente
- [ ] Probar en diferentes clientes de email (Gmail, Outlook, etc.)
- [ ] Verificar responsive en móvil

---

## 📝 Notas Importantes

1. **Logo:** Todos los emails usan la URL pública `https://crushme.com.co/static/frontend/BUY.png`
2. **Parámetros:** Son idénticos en ambos idiomas, solo cambian los textos
3. **Formato de números:** 
   - Español: `$100.000 COP` (punto como separador de miles)
   - Inglés: `$100,000 USD` (coma como separador de miles)
4. **Default:** Si no se especifica idioma, usar español ('es')

---

## 🎯 Próximos Pasos

1. Copiar los HTMLs exportados al proyecto Django
2. Implementar `EmailService` con soporte bilingüe
3. Configurar detección automática de idioma
4. Probar envío de emails en ambos idiomas
5. Verificar que los emails se vean correctamente en producción

---

**Última actualización:** 24 de Octubre, 2025  
**Total de emails:** 12 (6 en español + 6 en inglés)  
**Archivos HTML exportados:** ✅ Listos en `/out/es/` y `/out/en/`
