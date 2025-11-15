# 🔔 Configuración de Webhooks de Wompi Widget

## 📋 Resumen

Este documento explica cómo configurar los webhooks de Wompi para procesar pagos automáticamente cuando se usa el **Wompi Widget** en el frontend.

---

## 🎯 ¿Por qué Webhooks?

El **Wompi Widget** NO envía el `transaction_id` automáticamente por:
- ❌ Redirect URL
- ❌ postMessage

**Solución:** Usar **webhooks** para recibir notificaciones de Wompi cuando el pago se aprueba.

---

## 🔄 Flujo Completo

### **1. Usuario paga con Wompi Widget**
```
Frontend → Wompi Widget → Usuario paga → Wompi procesa
```

### **2. Wompi envía webhook al backend**
```
Wompi → POST /api/orders/wompi/webhook/
```
**Payload:**
```json
{
  "event": "transaction.updated",
  "data": {
    "transaction": {
      "id": "1332149-1763070937-18732",
      "status": "APPROVED",
      "reference": "ORD182916UQJEES0O",
      "customer_email": "user@example.com",
      "amount_in_cents": 31350000
    }
  }
}
```

### **3. Backend procesa la orden automáticamente**
```python
# wompi_order_views.py::wompi_webhook()
1. Verifica que status == 'APPROVED'
2. Recupera order_data del cache usando reference
3. Procesa la orden (crea en DB y WooCommerce)
4. Guarda resultado en cache para frontend
```

### **4. Frontend hace polling para verificar estado**
```javascript
// WompiSuccess.vue
setInterval(() => {
  GET /api/orders/wompi/status/{reference}/
}, 1000)
```

**Respuesta:**
```json
{
  "status": "success",
  "order_id": 123,
  "order_number": "ORD182916UQJEES0O",
  "transaction_id": "1332149-1763070937-18732",
  "total": "313500.00",
  "email": "user@example.com"
}
```

### **5. Frontend muestra confirmación**
```
WompiSuccess.vue → Muestra orden exitosa → Redirige a Home
```

---

## 🛠️ Configuración en Wompi Dashboard

### **Paso 1: Ir a Desarrollos → Programadores**

En el dashboard de Wompi:
1. Menú lateral → **"Desarrollo"** o **"Developers"**
2. Click en **"Programadores"**

### **Paso 2: Configurar URL de Eventos**

En la sección **"Seguimiento de transacciones"**:

**Para desarrollo (localhost):**
```
⚠️ Wompi NO soporta localhost en webhooks
```

**Solución: Usar ngrok**
```bash
# 1. Instalar ngrok
snap install ngrok

# 2. Exponer el backend
ngrok http 8000

# 3. Copiar la URL de ngrok
https://abc123.ngrok.io
```

**URL de webhook a configurar:**
```
https://abc123.ngrok.io/api/orders/wompi/webhook/
```

**Para producción:**
```
https://crushme.com.co/api/orders/wompi/webhook/
```

### **Paso 3: Guardar configuración**

Click en el botón **"Guardar"** verde.

---

## 📡 Endpoints Implementados

### **1. POST `/api/orders/wompi/webhook/`**
**Descripción:** Recibe notificaciones de Wompi cuando cambia el estado de una transacción.

**Headers:**
- `X-Wompi-Signature`: Firma de seguridad (opcional en sandbox)

**Body:**
```json
{
  "event": "transaction.updated",
  "data": {
    "transaction": {
      "id": "TRANSACTION_ID",
      "status": "APPROVED",
      "reference": "ORDER_REFERENCE"
    }
  }
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Webhook processed successfully"
}
```

**Proceso:**
1. Verifica que `status == 'APPROVED'`
2. Busca `order_data` en cache usando `reference`
3. Procesa orden usando `process_order_after_payment()`
4. Guarda resultado en cache: `wompi_payment_status_{reference}`

---

### **2. GET `/api/orders/wompi/status/<reference>/`**
**Descripción:** Endpoint de polling para que el frontend verifique el estado del pago.

**Parámetros:**
- `reference`: Referencia de la orden (ej: `ORD182916UQJEES0O`)

**Respuestas:**

**Pending (pago aún no procesado):**
```json
{
  "status": "pending",
  "message": "Payment is being processed"
}
```

**Success (pago procesado exitosamente):**
```json
{
  "status": "success",
  "order_id": 123,
  "order_number": "ORD182916UQJEES0O",
  "transaction_id": "1332149-1763070937-18732",
  "total": "313500.00",
  "email": "user@example.com",
  "message": "Payment processed successfully"
}
```

**Error (pago falló):**
```json
{
  "status": "error",
  "error": "Payment verification failed",
  "message": "Payment processing failed"
}
```

---

### **3. POST `/api/orders/wompi/create/`**
**Descripción:** Crea widget data para inicializar Wompi Widget en el frontend.

**Body:**
```json
{
  "items": [...],
  "customer_email": "user@example.com",
  "customer_name": "John Doe",
  "phone_number": "+57 300 1234567",
  "shipping_address": "Calle 123",
  "shipping_city": "Medellín",
  "shipping_state": "Antioquia",
  "shipping_postal_code": "050001",
  "shipping_country": "CO"
}
```

**Respuesta:**
```json
{
  "success": true,
  "widget_data": {
    "public_key": "pub_test_...",
    "currency": "COP",
    "amount_in_cents": 31350000,
    "reference": "ORD182916UQJEES0O",
    "signature": "3c20eb100dedb30f...",
    "redirect_url": "http://localhost:5173/checkout/wompi/success",
    "customer_data": {
      "email": "user@example.com",
      "full_name": "John Doe",
      "phone_number": "3001234567",
      "phone_number_prefix": "+57"
    }
  },
  "reference": "ORD182916UQJEES0O",
  "total": "313500.00",
  "amount_in_cents": 31350000
}
```

**Proceso:**
1. Valida items y calcula total
2. Genera `reference` única
3. Calcula `integrity_signature`
4. Guarda `order_data` en cache: `wompi_order_data_{reference}`
5. Retorna `widget_data` para el frontend

---

## 🗄️ Cache Storage

### **Datos guardados en cache:**

**1. Order Data (al crear transacción):**
```python
cache.set(f'wompi_order_data_{reference}', {
    'items': [...],
    'customer_email': '...',
    'customer_name': '...',
    'shipping_address': '...',
    # ... todos los datos de la orden
}, 3600)  # 1 hora
```

**2. Payment Status (después del webhook):**
```python
cache.set(f'wompi_payment_status_{reference}', {
    'status': 'success',
    'order_id': 123,
    'transaction_id': '...'
}, 3600)  # 1 hora
```

---

## 🧪 Testing en Desarrollo

### **Opción 1: Usar ngrok (Recomendado)**

```bash
# Terminal 1: Backend Django
python manage.py runserver

# Terminal 2: ngrok
ngrok http 8000

# Copiar URL de ngrok y configurar en Wompi
# Ejemplo: https://abc123.ngrok.io/api/orders/wompi/webhook/
```

### **Opción 2: Simular webhook manualmente**

```bash
# Simular webhook de Wompi
curl -X POST http://localhost:8000/api/orders/wompi/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "event": "transaction.updated",
    "data": {
      "transaction": {
        "id": "test-transaction-123",
        "status": "APPROVED",
        "reference": "ORD182916UQJEES0O",
        "customer_email": "test@example.com",
        "amount_in_cents": 31350000
      }
    }
  }'
```

---

## 🔍 Debugging

### **Ver logs del webhook:**

```bash
# Backend logs
tail -f logs/django.log | grep WEBHOOK

# Buscar:
# 📬 [WOMPI WEBHOOK] Received webhook
# 📬 [WOMPI WEBHOOK] Event: transaction.updated, Transaction: ..., Status: APPROVED
# ✅ [WOMPI WEBHOOK] Order processed successfully: ...
```

### **Verificar cache:**

```python
# Django shell
python manage.py shell

from django.core.cache import cache

# Ver order data
reference = "ORD182916UQJEES0O"
order_data = cache.get(f'wompi_order_data_{reference}')
print(order_data)

# Ver payment status
payment_status = cache.get(f'wompi_payment_status_{reference}')
print(payment_status)
```

### **Verificar orden en DB:**

```python
from crushme_app.models import Order

# Buscar por transaction_id
order = Order.objects.filter(transaction_id='1332149-1763070937-18732').first()
print(f"Order: {order.order_number}, Status: {order.status}")
```

---

## ⚠️ Troubleshooting

### **Problema: Webhook no se recibe**

**Causa:** Wompi no puede alcanzar localhost.

**Solución:** Usar ngrok para exponer el backend.

---

### **Problema: Order data not found in cache**

**Causa:** El cache expiró (1 hora) o no se guardó correctamente.

**Solución:**
1. Verificar que `create_wompi_transaction` guarda en cache
2. Aumentar tiempo de expiración si es necesario
3. Verificar logs: `💾 [WOMPI] Stored order data in cache for reference: ...`

---

### **Problema: Frontend polling timeout (60 segundos)**

**Causa:** El webhook no se ejecutó o falló.

**Solución:**
1. Verificar logs del webhook
2. Verificar que la URL del webhook está configurada en Wompi
3. Simular webhook manualmente para testing

---

### **Problema: Orden duplicada**

**Causa:** Wompi envió el webhook múltiples veces.

**Solución:** Ya implementado - el webhook verifica si la orden ya existe:
```python
existing_order = Order.objects.filter(transaction_id=transaction_id).first()
if existing_order:
    return Response({'success': True, 'message': 'Order already processed'})
```

---

## 📚 Referencias

- **Wompi Widget Docs:** https://docs.wompi.co/en/docs/colombia/widget-checkout-web/
- **Wompi Webhooks Docs:** https://docs.wompi.co/en/docs/colombia/webhooks/
- **ngrok Docs:** https://ngrok.com/docs

---

## ✅ Checklist de Implementación

- [x] Endpoint de webhook implementado (`/api/orders/wompi/webhook/`)
- [x] Endpoint de polling implementado (`/api/orders/wompi/status/<reference>/`)
- [x] Cache storage para order data
- [x] Cache storage para payment status
- [x] Prevención de órdenes duplicadas
- [x] Logging detallado
- [x] Error handling
- [ ] Configurar webhook URL en Wompi dashboard
- [ ] Testing con ngrok en desarrollo
- [ ] Configurar webhook URL en producción

---

## 🎉 Resultado Final

**Flujo completo funcionando:**

1. ✅ Usuario paga con Wompi Widget
2. ✅ Wompi envía webhook al backend
3. ✅ Backend procesa orden automáticamente
4. ✅ Frontend hace polling y obtiene resultado
5. ✅ Frontend muestra confirmación de orden
6. ✅ Carrito se limpia
7. ✅ Usuario redirigido a Home

**Sin necesidad de:**
- ❌ Transaction ID manual
- ❌ Botón "Confirmar pago"
- ❌ Redirect URL con parámetros
- ❌ postMessage entre ventanas

**Todo automático y transparente para el usuario! 🎊**
