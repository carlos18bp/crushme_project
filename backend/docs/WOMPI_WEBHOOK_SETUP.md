# Configuración del Webhook de Wompi

## 🎯 Objetivo

El webhook de Wompi permite que el backend reciba notificaciones automáticas cuando un pago es aprobado, rechazado o cambia de estado. Esto es **CRÍTICO** para procesar órdenes automáticamente.

## 📍 Endpoint del Webhook

**URL:** `POST /api/orders/wompi/webhook/`

**Características:**
- ✅ Público (no requiere autenticación)
- ✅ Acepta requests de Wompi
- ✅ Procesa pagos aprobados automáticamente
- ✅ Crea órdenes en la base de datos
- ✅ Envía emails de confirmación
- ✅ Sincroniza con WooCommerce

## 🔧 Testing Local con ngrok

### Paso 1: Instalar ngrok

```bash
# Opción 1: Con snap (Ubuntu/Debian)
sudo snap install ngrok

# Opción 2: Descargar desde
https://ngrok.com/download
```

### Paso 2: Iniciar el servidor Django

```bash
cd /home/cerrotico/work/crushme_project/backend
source venv/bin/activate
python manage.py runserver
```

### Paso 3: Exponer con ngrok

```bash
# Usar el script automático
./setup_ngrok_webhook.sh

# O manualmente
ngrok http 8000
```

Verás algo como:
```
Forwarding  https://a1b2-3c4d-5e6f.ngrok-free.app -> http://localhost:8000
```

### Paso 4: Configurar en Wompi Dashboard

1. **Ir al dashboard de Wompi:**
   - Sandbox: https://comercios.wompi.co/dashboard
   - Producción: https://comercios.wompi.co/dashboard

2. **Navegar a Webhooks:**
   - Configuración → Webhooks → Eventos

3. **Agregar webhook URL:**
   ```
   https://TU-URL-NGROK.ngrok-free.app/api/orders/wompi/webhook/
   ```

4. **Seleccionar evento:**
   - `transaction.updated` ✅

5. **Guardar configuración**

## 🧪 Testing del Webhook

### 1. Crear una transacción de prueba

Desde el frontend o Postman:

```bash
POST http://localhost:8000/api/orders/wompi/create/
Content-Type: application/json
X-Currency: COP

{
  "customer_email": "test@example.com",
  "customer_name": "Test User",
  "phone_number": "3001234567",
  "items": [
    {
      "woocommerce_product_id": 1234,
      "product_name": "Test Product",
      "quantity": 1,
      "unit_price": 50000
    }
  ],
  "shipping": 15000,
  "total": 65000,
  "shipping_address": "Calle 123",
  "shipping_city": "Bogotá",
  "shipping_state": "Cundinamarca",
  "shipping_postal_code": "110111",
  "shipping_country": "CO"
}
```

### 2. Completar el pago en Wompi

- Usa la URL del widget que retorna el endpoint
- Completa el pago con tarjeta de prueba de Wompi
- Wompi enviará el webhook automáticamente

### 3. Verificar logs del servidor

En la terminal del servidor Django verás:

```
📬 [WOMPI WEBHOOK] Received webhook
📬 [WOMPI WEBHOOK] Event: transaction.updated, Transaction: 12345-..., Status: APPROVED
✅ [WOMPI WEBHOOK] Found order data in cache
🔄 [WOMPI WEBHOOK] Processing order for transaction: 12345-...
✅ [WOMPI WEBHOOK] Order processed successfully: ORD-123456
```

## 📊 Estructura del Webhook de Wompi

Wompi envía un POST con este formato:

```json
{
  "event": "transaction.updated",
  "data": {
    "transaction": {
      "id": "12345-1234-1234-1234-123456789012",
      "status": "APPROVED",
      "reference": "ORD-20231119-123456",
      "customer_email": "test@example.com",
      "amount_in_cents": 6500000,
      "currency": "COP",
      "payment_method_type": "CARD",
      "created_at": "2023-11-19T10:30:00.000Z"
    }
  },
  "sent_at": "2023-11-19T10:30:05.000Z"
}
```

## 🔐 Validación de Integridad (Opcional)

Wompi puede firmar los webhooks con un secret. Para habilitarlo:

1. **Obtener el secret del dashboard de Wompi**

2. **Agregar a settings.py:**
```python
WOMPI_WEBHOOK_SECRET = 'tu_webhook_secret_aqui'
```

3. **Validar firma en el webhook:**
```python
import hmac
import hashlib

def validate_wompi_signature(request):
    signature = request.headers.get('X-Wompi-Signature')
    secret = settings.WOMPI_WEBHOOK_SECRET
    
    computed = hmac.new(
        secret.encode(),
        request.body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, computed)
```

## 🚀 Producción

### Configurar URL permanente

En producción, usa tu dominio real:

```
https://api.crushme.com/api/orders/wompi/webhook/
```

### Variables de entorno

```bash
# .env
WOMPI_PUBLIC_KEY=pub_prod_xxxxx
WOMPI_PRIVATE_KEY=prv_prod_xxxxx
WOMPI_WEBHOOK_SECRET=webhook_secret_xxxxx
```

### Verificar HTTPS

Wompi **requiere HTTPS** en producción. Asegúrate de que tu servidor tenga SSL configurado.

## 🐛 Troubleshooting

### El webhook no llega

1. **Verificar que ngrok esté corriendo:**
   ```bash
   curl https://TU-URL-NGROK.ngrok-free.app/api/
   ```

2. **Verificar logs de ngrok:**
   - Abre http://localhost:4040 en el navegador
   - Verás todos los requests que llegan a ngrok

3. **Verificar configuración en Wompi:**
   - URL correcta
   - Evento `transaction.updated` seleccionado
   - Webhook activo

### El webhook llega pero falla

1. **Verificar logs del servidor Django:**
   ```bash
   tail -f logs/django.log
   ```

2. **Verificar que el reference existe en cache:**
   ```python
   from django.core.cache import cache
   cache.get('wompi_order_data_ORD-20231119-123456')
   ```

3. **Verificar que no haya orden duplicada:**
   ```python
   from crushme_app.models import Order
   Order.objects.filter(transaction_id='12345-...').exists()
   ```

### Error 404 en el webhook

Verifica que la URL sea exactamente:
```
https://TU-DOMINIO/api/orders/wompi/webhook/
```

**Nota:** La barra final `/` es importante.

## 📝 Logs Importantes

El webhook genera estos logs:

```
📬 [WOMPI WEBHOOK] Received webhook
📬 [WOMPI WEBHOOK] Headers: {...}
📬 [WOMPI WEBHOOK] Body: {...}
📬 [WOMPI WEBHOOK] Event: transaction.updated, Transaction: xxx, Status: APPROVED
✅ [WOMPI WEBHOOK] Found order data in cache
🔄 [WOMPI WEBHOOK] Processing order
✅ [WOMPI WEBHOOK] Order processed successfully: ORD-123456
```

## 🔄 Flujo Completo

1. **Usuario completa checkout** → Frontend llama a `/api/orders/wompi/create/`
2. **Backend crea transacción** → Guarda datos en cache con `reference`
3. **Usuario paga en Wompi** → Completa el pago
4. **Wompi envía webhook** → POST a `/api/orders/wompi/webhook/`
5. **Backend procesa webhook** → Busca datos en cache con `reference`
6. **Backend crea orden** → Guarda en DB, envía email, sincroniza WooCommerce
7. **Frontend polling** → Verifica status con `/api/orders/wompi/status/{reference}/`
8. **Frontend redirige** → Muestra página de éxito

## 📚 Referencias

- [Documentación de Webhooks de Wompi](https://docs.wompi.co/docs/webhooks)
- [Dashboard de Wompi](https://comercios.wompi.co/dashboard)
- [ngrok Documentation](https://ngrok.com/docs)

## ✅ Checklist de Configuración

- [ ] ngrok instalado
- [ ] Servidor Django corriendo
- [ ] ngrok exponiendo puerto 8000
- [ ] URL de ngrok copiada
- [ ] Webhook configurado en Wompi dashboard
- [ ] Evento `transaction.updated` seleccionado
- [ ] Webhook activo en Wompi
- [ ] Logs del servidor visibles
- [ ] Transacción de prueba creada
- [ ] Pago completado en Wompi
- [ ] Webhook recibido y procesado
- [ ] Orden creada en base de datos
- [ ] Email de confirmación enviado
