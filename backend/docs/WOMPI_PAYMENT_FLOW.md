# Wompi - Flujo de Pago Correcto

## 🔄 Diferencia: PayPal vs Wompi

### **PayPal (Backend-First)**
```
1. Frontend → Backend: Crear orden PayPal
2. Backend → PayPal API: Crear orden
3. PayPal → Backend: Order ID
4. Backend → Frontend: Order ID
5. Frontend: Mostrar popup PayPal
6. Usuario: Paga en popup
7. Frontend → Backend: Capturar pago
8. Backend → PayPal: Capturar
9. Backend: Crear orden local
```

### **Wompi (Payment Link)**
```
1. Frontend → Backend: Crear payment link
2. Backend → Wompi API: Crear payment link
3. Wompi → Backend: Payment URL
4. Backend → Frontend: Payment URL
5. Frontend: Redirigir a Wompi
6. Usuario: Selecciona método y paga en Wompi
7. Wompi: Redirige de vuelta
8. Frontend → Backend: Confirmar pago
9. Backend → Wompi: Verificar transacción
10. Backend: Crear orden local
```

---

## 🐛 Error Anterior

```
"No se especificó método de pago o fuente de pago"
```

### **Causa:**
Estábamos usando el endpoint `/transactions` que requiere que el método de pago ya esté seleccionado.

### **Solución:**
Usar el endpoint `/payment_links` que genera un link donde el usuario selecciona el método de pago.

---

## 🔧 Cambios Realizados

### **Antes (❌ Incorrecto)**
```python
# Endpoint: /transactions
url = f"{self.base_url}/transactions"
headers = {
    'Authorization': f'Bearer {self.public_key}'
}
# Requiere payment_method especificado
```

### **Después (✅ Correcto)**
```python
# Endpoint: /payment_links
url = f"{self.base_url}/payment_links"
headers = {
    'Authorization': f'Bearer {self.private_key}'  # Usa private key
}
# No requiere payment_method, usuario lo selecciona en Wompi
```

---

## 📋 Flujo Detallado

### **Paso 1: Frontend - Crear Payment Link**

```javascript
// CheckoutView.vue
async function createWompiPayment() {
  const orderData = {
    customer_email: user.email,
    customer_name: user.fullName,
    phone_number: shippingForm.phone,
    items: cartStore.items.map(item => ({
      woocommerce_product_id: item.productId,
      product_name: item.name,
      quantity: item.quantity,
      unit_price: item.price  // En COP
    })),
    shipping_address: shippingForm.address,
    shipping_city: shippingForm.city,
    shipping_state: shippingForm.state,
    shipping_postal_code: shippingForm.zipCode,
    shipping_country: 'CO',
    shipping: shippingCost
  };

  // Crear payment link
  const response = await axios.post('/api/orders/wompi/create/', orderData);
  
  if (response.data.success) {
    // Guardar datos para confirmar después
    localStorage.setItem('wompi_transaction_id', response.data.transaction_id);
    localStorage.setItem('wompi_order_data', JSON.stringify(orderData));
    
    // Redirigir a Wompi
    window.location.href = response.data.payment_url;
  }
}
```

### **Paso 2: Backend - Crear Payment Link**

```python
# wompi_order_views.py - create_wompi_transaction()

# Crear payment link en Wompi
wompi_result = wompi_service.create_transaction(
    amount_in_cents=amount_in_cents,
    reference=reference,
    customer_email=customer_email,
    customer_name=customer_name,
    redirect_url=redirect_url,
    phone_number=phone_number,
    currency='COP'
)

# Response:
{
    'success': True,
    'transaction_id': '12345-1234-1234-1234',
    'payment_url': 'https://checkout.wompi.co/l/aBcDeF123456',
    'status': 'PENDING'
}
```

### **Paso 3: Usuario Paga en Wompi**

El usuario es redirigido a `https://checkout.wompi.co/l/aBcDeF123456` donde:

1. **Selecciona método de pago:**
   - Tarjeta de crédito/débito
   - PSE (transferencia bancaria)
   - Nequi
   - Bancolombia
   - Etc.

2. **Completa el pago**

3. **Wompi redirige de vuelta:**
   ```
   http://localhost:5173/checkout/wompi/success?id=TRANSACTION_ID
   ```

### **Paso 4: Frontend - Confirmar Pago**

```javascript
// WompiSuccessView.vue
async function confirmWompiPayment() {
  // Obtener transaction_id de la URL
  const urlParams = new URLSearchParams(window.location.search);
  const transactionId = urlParams.get('id');
  
  // Recuperar datos de la orden
  const orderData = JSON.parse(localStorage.getItem('wompi_order_data'));
  
  // Confirmar pago con backend
  const response = await axios.post('/api/orders/wompi/confirm/', {
    transaction_id: transactionId,
    ...orderData
  });
  
  if (response.data.success) {
    // Mostrar confirmación
    showSuccessMessage(response.data.order);
    
    // Limpiar
    localStorage.removeItem('wompi_transaction_id');
    localStorage.removeItem('wompi_order_data');
    cartStore.clearCart();
  }
}
```

### **Paso 5: Backend - Verificar y Crear Orden**

```python
# wompi_order_views.py - confirm_wompi_payment()

# Verificar transacción con Wompi
verification_result = wompi_service.get_transaction(transaction_id)

if verification_result['status'] == 'APPROVED':
    # Pago aprobado, crear orden local
    payment_info = {
        'transaction_id': transaction_id,
        'status': 'APPROVED',
        'payer_email': customer_email,
        'payer_name': customer_name
    }
    
    # Usar flujo común
    return process_order_after_payment(
        request_data=dict(request.data),
        payment_info=payment_info,
        payment_provider='wompi'
    )
```

---

## 🎨 Payment Link vs Widget

Wompi ofrece 2 formas de integración:

### **1. Payment Link (Implementado)** ⭐

**Ventajas:**
- ✅ Más simple de implementar
- ✅ No requiere JavaScript adicional
- ✅ Wompi maneja todo el UI
- ✅ Funciona en cualquier dispositivo

**Desventajas:**
- ❌ Usuario sale de tu sitio
- ❌ Menos control sobre UX

**Flujo:**
```
Tu sitio → Redirige a Wompi → Usuario paga → Redirige de vuelta
```

### **2. Widget Checkout (Avanzado)**

**Ventajas:**
- ✅ Usuario permanece en tu sitio
- ✅ Mejor UX
- ✅ Más control sobre diseño

**Desventajas:**
- ❌ Más complejo de implementar
- ❌ Requiere JavaScript de Wompi
- ❌ Más código frontend

**Flujo:**
```
Tu sitio → Widget Wompi (iframe) → Usuario paga → Callback
```

---

## 📊 Endpoints de Wompi

| Endpoint | Método | Autenticación | Uso |
|----------|--------|---------------|-----|
| `/payment_links` | POST | Private Key | Crear link de pago ⭐ |
| `/transactions` | POST | Public Key | Crear transacción directa |
| `/transactions/{id}` | GET | Public Key | Verificar transacción |
| `/payment_sources` | POST | Public Key | Tokenizar tarjeta |

---

## 🔐 Autenticación

| Endpoint | Header | Llave |
|----------|--------|-------|
| `/payment_links` | `Bearer {private_key}` | Private Key |
| `/transactions` | `Bearer {public_key}` | Public Key |
| `/transactions/{id}` | `Bearer {public_key}` | Public Key |

---

## 🧪 Testing

### **1. Crear Payment Link**

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
  "shipping_address": "Calle 123",
  "shipping_city": "Medellín",
  "shipping_state": "Antioquia",
  "shipping_postal_code": "050001",
  "shipping_country": "CO",
  "shipping": 10000
}
```

**Response:**
```json
{
  "success": true,
  "transaction_id": "12345-1234-1234-1234",
  "payment_url": "https://checkout.wompi.co/l/aBcDeF123456",
  "reference": "ORD123456ABC",
  "total": "60000",
  "amount_in_cents": 6000000
}
```

### **2. Usuario Paga**

Abrir `payment_url` en el navegador:
```
https://checkout.wompi.co/l/aBcDeF123456
```

Usar tarjeta de prueba:
```
Número: 4242 4242 4242 4242
CVV: 123
Fecha: 12/25
```

### **3. Confirmar Pago**

Después de que Wompi redirige:
```bash
POST /api/orders/wompi/confirm/
{
  "transaction_id": "12345-1234-1234-1234",
  "customer_email": "test@example.com",
  "customer_name": "Test User",
  "phone_number": "+57 300 1234567",
  "items": [...],  // Mismos items
  "shipping_address": "...",
  // ... resto de datos
}
```

---

## 🚨 Errores Comunes

### **1. "No se especificó método de pago"**
```
ERROR: "No se especificó método de pago o fuente de pago"
```

**Causa:** Usando `/transactions` en lugar de `/payment_links`

**Solución:** ✅ Ya corregido - ahora usa `/payment_links`

### **2. "Invalid access token"**
```
ERROR: "La llave proporcionada no corresponde a este ambiente"
```

**Causa:** Payment links requieren **private key**, no public key

**Solución:** ✅ Ya corregido - ahora usa `private_key`

### **3. "Phone number required"**
```
ERROR: "customer_data": {"phone_number": ["Debe ser completado"]}
```

**Solución:** ✅ Ya corregido - ahora envía `phone_number`

---

## 📚 Documentación de Wompi

- **Payment Links:** https://docs.wompi.co/docs/en/payment-links
- **Transactions:** https://docs.wompi.co/docs/en/transactions
- **Widget Checkout:** https://docs.wompi.co/docs/en/widgets-checkout

---

## ✅ Resumen

### **Problema:**
❌ Intentaba crear transacción sin método de pago

### **Solución:**
✅ Usar Payment Links para que usuario seleccione método en Wompi

### **Cambios:**
1. Endpoint: `/transactions` → `/payment_links`
2. Auth: `public_key` → `private_key`
3. Response: `checkout_url` → `url`

### **Flujo:**
```
Frontend → Backend crea link → Redirige a Wompi → 
Usuario paga → Redirige de vuelta → Backend confirma
```

### **Archivos Modificados:**
- `crushme_app/services/wompi_service.py` - Usa `/payment_links`

¡Ahora el flujo de Wompi funciona correctamente! 🎉
