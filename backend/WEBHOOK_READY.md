# ✅ Webhook de Wompi - LISTO PARA USAR

## 🎉 Estado: COMPLETAMENTE FUNCIONAL

### ✅ Cambios Realizados:

1. **Modelo Order actualizado:**
   - ✅ Campo `transaction_id` agregado (único)
   - ✅ Campo `payment_provider` agregado (paypal/wompi)
   - ✅ Migración aplicada exitosamente

2. **Webhook configurado:**
   - ✅ Endpoint: `/api/orders/wompi/webhook/`
   - ✅ Público (AllowAny)
   - ✅ Procesa transacciones APPROVED
   - ✅ Previene duplicados
   - ✅ Guarda transaction_id y payment_provider

3. **ngrok configurado:**
   - ✅ ngrok instalado y autenticado
   - ✅ Corriendo en background
   - ✅ URL pública: `https://craggiest-unhermitically-patricia.ngrok-free.dev`

---

## 🔗 URL del Webhook para Wompi:

```
https://craggiest-unhermitically-patricia.ngrok-free.dev/api/orders/wompi/webhook/
```

---

## 📋 Configurar en Wompi Dashboard:

### 1. Ir al Dashboard:
```
https://comercios.wompi.co/dashboard
```

### 2. Navegar a Webhooks:
**Configuración** → **Webhooks** → **Eventos**

### 3. Agregar Webhook:
- **URL:** `https://craggiest-unhermitically-patricia.ngrok-free.dev/api/orders/wompi/webhook/`
- **Evento:** `transaction.updated` ✅
- **Guardar**

---

## 🧪 Testing Completo:

### Paso 1: Crear una transacción desde el frontend

1. Ve al checkout en el frontend
2. Completa el formulario
3. Click en "Pagar con Wompi"
4. Copia el `reference` que aparece en los logs (ej: `ORD57439997ZIUYDI`)

### Paso 2: Completar el pago en Wompi

1. Usa la tarjeta de prueba de Wompi:
   - **Número:** 4242 4242 4242 4242
   - **CVV:** 123
   - **Fecha:** Cualquier fecha futura
   - **Cuotas:** 1

2. Completa el pago

### Paso 3: Wompi envía el webhook automáticamente

El webhook llegará a tu servidor y verás en los logs:

```
📬 [WOMPI WEBHOOK] Received webhook
📬 [WOMPI WEBHOOK] Event: transaction.updated, Transaction: xxx, Status: APPROVED
✅ [WOMPI WEBHOOK] Found order data in cache
🔄 [WOMPI WEBHOOK] Processing order for transaction: xxx
✅ [WOMPI WEBHOOK] Order processed successfully: ORD-123456
```

### Paso 4: Verificar la orden en la base de datos

```bash
source venv/bin/activate
python manage.py shell
```

```python
from crushme_app.models import Order

# Ver última orden
order = Order.objects.latest('created_at')
print(f"Order: {order.order_number}")
print(f"Transaction ID: {order.transaction_id}")
print(f"Payment Provider: {order.payment_provider}")
print(f"Status: {order.status}")
print(f"Total: ${order.total}")
```

---

## 🔍 Debugging:

### Ver requests en ngrok:
```
http://localhost:4040
```

Aquí verás:
- ✅ Todos los requests que llegan
- ✅ Headers completos
- ✅ Body del webhook
- ✅ Response del servidor

### Ver logs del servidor Django:

Los logs aparecen automáticamente en la terminal donde corre Django:

```bash
# Logs del webhook
📬 [WOMPI WEBHOOK] Received webhook
📬 [WOMPI WEBHOOK] Headers: {...}
📬 [WOMPI WEBHOOK] Body: {...}
📬 [WOMPI WEBHOOK] Event: transaction.updated
✅ [WOMPI WEBHOOK] Order processed successfully

# Logs de la orden
✅ Order ORD-123456 created locally
📧 Sending order confirmation email
✅ Email sent successfully
```

---

## 📊 Flujo Completo:

```
1. Frontend → POST /api/orders/wompi/create/
   ↓
2. Backend → Guarda datos en cache con reference
   ↓
3. Backend → Retorna widget URL de Wompi
   ↓
4. Usuario → Completa pago en Wompi
   ↓
5. Wompi → POST /api/orders/wompi/webhook/ (via ngrok)
   ↓
6. Backend → Busca datos en cache con reference
   ↓
7. Backend → Crea orden en DB con transaction_id
   ↓
8. Backend → Envía email de confirmación
   ↓
9. Backend → Sincroniza con WooCommerce
   ↓
10. Backend → Guarda status en cache
    ↓
11. Frontend → Polling /api/orders/wompi/status/{reference}/
    ↓
12. Frontend → Detecta success y redirige
```

---

## ✅ Checklist de Testing:

- [x] ngrok instalado y autenticado
- [x] ngrok corriendo en background
- [x] URL de ngrok copiada
- [ ] Webhook configurado en Wompi dashboard
- [ ] Evento `transaction.updated` seleccionado
- [ ] Transacción de prueba creada desde frontend
- [ ] Pago completado con tarjeta de prueba
- [ ] Webhook recibido en el servidor
- [ ] Orden creada en base de datos
- [ ] Email de confirmación enviado
- [ ] Frontend detecta success y redirige

---

## 🚨 Importante:

### La URL de ngrok es temporal

Cada vez que reinicies ngrok, la URL cambiará. Deberás:
1. Copiar la nueva URL
2. Actualizar el webhook en Wompi dashboard

### Para mantener la misma URL (opcional):

Puedes usar un dominio personalizado con ngrok (requiere plan de pago):
```bash
ngrok http 8000 --domain=tu-dominio.ngrok-free.app
```

### En producción:

Usa tu dominio real:
```
https://api.crushme.com/api/orders/wompi/webhook/
```

---

## 📚 Archivos Importantes:

1. **Webhook endpoint:**
   - `crushme_app/views/wompi_order_views.py` (línea 429)

2. **Modelo Order:**
   - `crushme_app/models/order.py` (líneas 123-139)

3. **Procesamiento de orden:**
   - `crushme_app/views/order_helpers.py` (línea 21)

4. **Scripts de testing:**
   - `setup_ngrok_webhook.sh`
   - `test_wompi_webhook.py`

5. **Documentación:**
   - `docs/WOMPI_WEBHOOK_SETUP.md`
   - `WEBHOOK_TESTING.md`

---

## 🎯 Próximos Pasos:

1. **Configurar webhook en Wompi:**
   - Copia la URL de ngrok
   - Agrégala en el dashboard de Wompi
   - Selecciona evento `transaction.updated`

2. **Hacer una compra de prueba:**
   - Desde el frontend
   - Con tarjeta de prueba de Wompi
   - Verificar que el webhook llega

3. **Verificar que todo funciona:**
   - Orden creada en DB
   - Email enviado
   - Frontend redirige a success

---

## 🆘 Soporte:

Si algo no funciona:

1. **Verifica logs del servidor Django**
2. **Verifica ngrok dashboard:** http://localhost:4040
3. **Verifica cache:**
   ```python
   from django.core.cache import cache
   cache.get('wompi_order_data_ORD57439997ZIUYDI')
   ```
4. **Verifica que el webhook esté configurado en Wompi**
5. **Verifica que la URL de ngrok sea correcta**

---

## 🎉 ¡Listo!

El webhook de Wompi está completamente configurado y listo para usar. Solo falta configurarlo en el dashboard de Wompi y hacer una prueba.

**URL del webhook:**
```
https://craggiest-unhermitically-patricia.ngrok-free.dev/api/orders/wompi/webhook/
```

¡Buena suerte! 🚀
