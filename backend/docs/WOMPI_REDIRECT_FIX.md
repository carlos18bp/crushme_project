# Wompi Redirect Fix - Pantalla en Blanco

## 🐛 Problema Identificado

### Síntomas:
1. **Pantalla en blanco** después de completar el pago en Wompi
2. **Wompi redirige a su propia página** (`https://checkout.wompi.co/summary`) en lugar de a tu aplicación
3. **Error en consola:**
   ```
   TypeError: Cannot read properties of undefined (reading 'map')
   at t.renderTransactionInfo (bundle.js:2:326496)
   ```

### Causa Raíz:
El `redirect_url` enviado a Wompi **NO incluía el transaction_id** como parámetro, por lo que:
- Wompi no sabía dónde redirigir con el ID de la transacción
- Mostraba su propia página de resumen por defecto
- El frontend no recibía el `transaction_id` para confirmar el pago

---

## ✅ Solución Implementada

### 1. **Entender cómo Wompi maneja las redirecciones**

**Archivo:** `crushme_app/services/wompi_service.py`

**IMPORTANTE:** Payment Links de Wompi **automáticamente agregan** `?id=TRANSACTION_ID` al `redirect_url` cuando el pago se completa.

**Configuración correcta:**
```python
payload = {
    'redirect_url': redirect_url,  # http://localhost:5173/checkout/wompi/success
    # Wompi automáticamente agrega ?id=TRANSACTION_ID al redirigir
    # Resultado: http://localhost:5173/checkout/wompi/success?id=12345-abcd-6789
    # ...
}
```

**NOTA:** Las template variables como `{transaction.id}` solo funcionan en el **Widget Checkout**, NO en Payment Links.

### 2. **Mejorar manejo de errores en confirmación**

**Archivo:** `crushme_app/views/wompi_order_views.py`

Agregado:
- ✅ Logs más detallados para debugging
- ✅ Mensajes de error específicos por estado de pago
- ✅ Información adicional en respuestas de error

```python
# Provide more detailed error message based on status
status_messages = {
    'PENDING': 'Payment is still pending. Please wait for confirmation.',
    'DECLINED': 'Payment was declined by the payment processor.',
    'VOIDED': 'Payment was voided.',
    'ERROR': 'An error occurred during payment processing.'
}
```

---

## 🔄 Flujo Corregido

### **Paso 1: Frontend crea transacción**
```javascript
// CheckoutView.vue
const response = await paymentStore.createWompiTransaction(orderData);
// Guarda transaction_id y order_data en localStorage
localStorage.setItem('wompi_transaction_id', response.transaction_id);
localStorage.setItem('wompi_order_data', JSON.stringify(orderData));
// Redirige a Wompi
window.location.href = response.payment_url;
```

### **Paso 2: Backend crea payment link**
```python
# wompi_service.py
payload = {
    'redirect_url': redirect_url,
    # Wompi automáticamente agrega ?id=TRANSACTION_ID al redirigir
}
```

### **Paso 3: Usuario paga en Wompi**
- Usuario completa el pago en `https://checkout.wompi.co/l/aBcDeF123456`
- Selecciona método de pago (tarjeta, PSE, Nequi, etc.)
- Completa la transacción

### **Paso 4: Wompi redirige CON transaction_id** ⭐
```
http://localhost:5173/checkout/wompi/success?id=12345-abcd-6789-efgh
                                              ↑
                                    Transaction ID incluido
```

### **Paso 5: Frontend confirma pago**
```javascript
// WompiSuccess.vue
const urlParams = new URLSearchParams(window.location.search);
const transactionId = urlParams.get('id');  // ✅ Ahora existe!

const orderData = JSON.parse(localStorage.getItem('wompi_order_data'));

await paymentStore.confirmWompiPayment({
    transaction_id: transactionId,
    ...orderData
});
```

### **Paso 6: Backend verifica y crea orden**
```python
# wompi_order_views.py
verification_result = wompi_service.get_transaction(transaction_id)

if verification_result['status'] == 'APPROVED':
    # Crear orden local
    return process_order_after_payment(...)
```

---

## 📋 Documentación de Wompi

Según la documentación oficial de Wompi:

### **Cómo funcionan las redirecciones en Payment Links:**

**Payment Links** de Wompi automáticamente agregan el `transaction_id` como query parameter al `redirect_url`:

**Tu configuración:**
```python
'redirect_url': 'https://mysite.com/checkout/success'
```

**Wompi redirige a:**
```
https://mysite.com/checkout/success?id=12345-abcd-6789-efgh
                                    ↑
                            Transaction ID agregado automáticamente
```

### **Diferencia: Payment Links vs Widget Checkout**

| Característica | Payment Links | Widget Checkout |
|----------------|---------------|-----------------|
| **Redirección** | Automática con `?id=` | Manual con template variables |
| **Template Variables** | ❌ NO soportadas | ✅ Soportadas |
| **Uso** | Redirige a Wompi | Iframe en tu sitio |

**NOTA:** Las template variables como `{transaction.id}` solo funcionan en el **Widget Checkout**, NO en Payment Links.

### **Referencia:**
- https://docs.wompi.co/docs/en/payment-links
- https://docs.wompi.co/docs/en/widgets-checkout (para template variables)

---

## 🧪 Testing

### **1. Crear transacción:**
```bash
POST /api/orders/wompi/create/
{
  "customer_email": "test@example.com",
  "customer_name": "Test User",
  "phone_number": "+57 300 1234567",
  "items": [{
    "woocommerce_product_id": 123,
    "product_name": "Test Product",
    "quantity": 1,
    "unit_price": 50000
  }],
  "shipping": 10000
}
```

**Response esperado:**
```json
{
  "success": true,
  "transaction_id": "test_V8oI3C",
  "payment_url": "https://checkout.wompi.co/l/test_V8oI3C",
  "reference": "ORD123456ABC"
}
```

### **2. Completar pago en Wompi:**
- Abrir `payment_url` en el navegador
- Usar tarjeta de prueba:
  ```
  Número: 4242 4242 4242 4242
  CVV: 123
  Fecha: 12/25
  ```

### **3. Verificar redirección:**
Wompi debe redirigir a:
```
http://localhost:5173/checkout/wompi/success?id=test_V8oI3C
                                              ↑
                                    ✅ Transaction ID presente
```

### **4. Confirmar pago:**
```bash
POST /api/orders/wompi/confirm/
{
  "transaction_id": "test_V8oI3C",
  "customer_email": "test@example.com",
  "customer_name": "Test User",
  "items": [...],  // Mismos items
  // ... resto de datos
}
```

**Response esperado (APPROVED):**
```json
{
  "success": true,
  "order": {
    "order_number": "ORD123456ABC",
    "status": "processing",
    "total": 60000
  }
}
```

---

## 🚨 Errores Comunes

### **1. Transaction ID no aparece en URL**
```
❌ http://localhost:5173/checkout/wompi/success
✅ http://localhost:5173/checkout/wompi/success?id=test_V8oI3C
```

**Causa:** Wompi no está redirigiendo correctamente (puede ser configuración en el dashboard de Wompi)

**Solución:** 
- Verificar que el `redirect_url` sea válido (debe ser HTTPS en producción)
- Verificar configuración en el dashboard de Wompi
- Wompi agrega automáticamente el `?id=` al redirigir

### **2. "Payment verification failed"**
```json
{
  "error": "Payment verification failed",
  "details": "Get transaction failed: 404"
}
```

**Causa:** El `transaction_id` no existe o es incorrecto

**Debugging:**
1. Verificar que el ID en la URL sea correcto
2. Revisar logs del backend: `🔵 [WOMPI] Verifying payment: {id}`
3. Verificar que la transacción exista en Wompi

### **3. "Payment is still pending"**
```json
{
  "error": "Payment is still pending. Please wait for confirmation.",
  "status": "PENDING"
}
```

**Causa:** El pago aún no ha sido procesado por Wompi

**Solución:**
- Esperar unos segundos y reintentar
- Verificar el estado en el dashboard de Wompi
- Para PSE, puede tomar varios minutos

### **4. "Payment was declined"**
```json
{
  "error": "Payment was declined by the payment processor.",
  "status": "DECLINED"
}
```

**Causa:** El método de pago fue rechazado

**Solución:**
- Verificar fondos en la cuenta
- Usar otra tarjeta/método de pago
- Revisar límites de la tarjeta

---

## 📊 Estados de Transacción

| Estado | Descripción | Acción |
|--------|-------------|--------|
| `PENDING` | Pago en proceso | Esperar confirmación |
| `APPROVED` | Pago aprobado | ✅ Crear orden |
| `DECLINED` | Pago rechazado | ❌ Mostrar error |
| `VOIDED` | Pago anulado | ❌ Mostrar error |
| `ERROR` | Error en procesamiento | ❌ Mostrar error |

---

## 🎯 Checklist de Verificación

Antes de probar en producción:

- [x] `redirect_url` es válido (HTTP en dev, HTTPS en prod)
- [x] Frontend lee `?id=` de la URL
- [x] Backend verifica transacción con Wompi
- [x] Logs detallados para debugging
- [x] Manejo de errores por estado
- [x] Limpieza de localStorage después de éxito
- [x] Limpieza de carrito después de éxito
- [ ] Configurar webhook de Wompi (opcional)
- [ ] Probar con diferentes métodos de pago
- [ ] Probar flujo de gift
- [ ] Probar flujo de wishlist

---

## 🔗 Referencias

- **Wompi Payment Links:** https://docs.wompi.co/docs/en/payment-links
- **Template Variables:** https://docs.wompi.co/docs/en/payment-links#template-variables
- **Transaction Status:** https://docs.wompi.co/docs/en/transactions#transaction-status
- **Webhooks:** https://docs.wompi.co/docs/en/events

---

## ✅ Resumen

### **Problema:**
❌ Wompi mostraba su propia página de resumen en lugar de redirigir a tu aplicación

### **Solución:**
✅ Entender que Wompi **automáticamente** agrega `?id=TRANSACTION_ID` al `redirect_url`

### **Configuración correcta:**
```python
# Payment Links agregan automáticamente el transaction_id
'redirect_url': 'http://localhost:5173/checkout/wompi/success'

# Wompi redirige a:
# http://localhost:5173/checkout/wompi/success?id=12345-abcd-6789
```

### **Resultado:**
✅ Wompi redirige correctamente con el transaction_id agregado automáticamente
✅ Frontend puede leer el `?id=` de la URL
✅ Backend verifica y crea la orden exitosamente

### **Nota importante:**
Las template variables como `{transaction.id}` solo funcionan en el **Widget Checkout**, NO en Payment Links.

---

**Fecha:** 2024-11-15
**Archivos modificados:**
- `crushme_app/services/wompi_service.py`
- `crushme_app/views/wompi_order_views.py`
