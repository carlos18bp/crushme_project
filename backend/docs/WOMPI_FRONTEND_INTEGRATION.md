# Wompi Frontend Integration Guide

## 🎯 Resumen

Wompi es la pasarela de pagos para usuarios colombianos que pagan en **COP (Pesos Colombianos)**. El flujo es similar a PayPal pero con endpoints diferentes.

---

## 🔌 Endpoints Wompi

### **Base URL**
```
http://localhost:8000/api/orders/wompi/
```

### **Endpoints Disponibles**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/wompi/config/` | Obtener configuración (public_key) |
| POST | `/wompi/create/` | Crear transacción de pago |
| POST | `/wompi/confirm/` | Confirmar pago después de aprobación |
| POST | `/wompi/webhook/` | Webhook para eventos (backend only) |

---

## 📋 Flujo Completo Frontend

```
1. Usuario en checkout selecciona "Pagar con Wompi"
   ↓
2. Frontend llama POST /wompi/create/
   ↓
3. Backend retorna payment_url de Wompi
   ↓
4. Frontend redirige usuario a payment_url
   ↓
5. Usuario paga en Wompi
   ↓
6. Wompi redirige a: /checkout/wompi/success?id=xxx
   ↓
7. Frontend llama POST /wompi/confirm/
   ↓
8. Backend verifica pago y crea orden
   ↓
9. Frontend muestra confirmación
```

---

## 1️⃣ Obtener Configuración

### **GET /api/orders/wompi/config/**

**Request:**
```javascript
const response = await axios.get('/api/orders/wompi/config/');
```

**Response:**
```json
{
  "public_key": "pub_test_lHrCKMGf7JVnO4DgnYrdDPgj1DSqJ0OR",
  "currency": "COP",
  "environment": "test"
}
```

**Uso:**
- Obtener `public_key` para inicializar SDK de Wompi (si se usa)
- Verificar que la moneda sea COP
- Mostrar solo para usuarios en Colombia

---

## 2️⃣ Crear Transacción

### **POST /api/orders/wompi/create/**

**Request Body:**
```json
{
  "customer_email": "customer@example.com",
  "customer_name": "Juan Pérez",
  "items": [
    {
      "woocommerce_product_id": 1234,
      "product_name": "Producto Ejemplo",
      "quantity": 2,
      "unit_price": 50000,
      "variation_id": 5679
    }
  ],
  "shipping_address": "Carrera 80 #50-25 Apto 301",
  "shipping_city": "Medellín",
  "shipping_state": "Antioquia",
  "shipping_postal_code": "050031",
  "shipping_country": "CO",
  "phone_number": "+57 300 1234567",
  "shipping": 15000,
  "notes": "Notas opcionales",
  "gift_message": "¡Feliz cumpleaños!",
  "is_gift": false,
  "sender_username": "opcional",
  "receiver_username": "opcional",
  "is_from_wishlist": false,
  "wishlist_id": null,
  "wishlist_name": "opcional"
}
```

**Campos Requeridos:**
- ✅ `customer_email` - Email del cliente
- ✅ `customer_name` - Nombre completo
- ✅ `items` - Array de productos (mínimo 1)
  - ✅ `woocommerce_product_id` - ID del producto
  - ✅ `product_name` - Nombre del producto
  - ✅ `quantity` - Cantidad
  - ✅ `unit_price` - Precio unitario en COP
  - ⚪ `variation_id` - ID de variación (opcional)
- ✅ `shipping_address` - Dirección de envío
- ✅ `shipping_city` - Ciudad
- ✅ `shipping_state` - Departamento
- ✅ `shipping_postal_code` - Código postal
- ✅ `shipping_country` - País (siempre "CO")
- ✅ `phone_number` - Teléfono
- ✅ `shipping` - Costo de envío en COP

**Campos Opcionales:**
- ⚪ `notes` - Notas adicionales
- ⚪ `gift_message` - Mensaje de regalo
- ⚪ `is_gift` - Si es un regalo (true/false)
- ⚪ `sender_username` - Usuario que envía el regalo
- ⚪ `receiver_username` - Usuario que recibe el regalo
- ⚪ `is_from_wishlist` - Si la compra viene de una wishlist (true/false)
- ⚪ `wishlist_id` - ID de la wishlist (si aplica)
- ⚪ `wishlist_name` - Nombre de la wishlist (referencia)

**Response Success (201):**
```json
{
  "success": true,
  "message": "Wompi transaction created successfully",
  "transaction_id": "12345-1234-1234-1234-123456789012",
  "payment_url": "https://checkout.wompi.co/l/aBcDeF123456",
  "reference": "ORD123456ABC",
  "total": "115000",
  "amount_in_cents": 11500000,
  "items_count": 2
}
```

**Response Error (400/500):**
```json
{
  "error": "Cart is empty",
  "details": "..."
}
```

**Ejemplo Frontend:**
```javascript
async function createWompiTransaction() {
  try {
    const orderData = {
      customer_email: user.email,
      customer_name: `${user.firstName} ${user.lastName}`,
      items: cartStore.items.map(item => ({
        woocommerce_product_id: item.productId,
        product_name: item.name,
        quantity: item.quantity,
        unit_price: item.price, // En COP
        variation_id: item.variationId || null
      })),
      shipping_address: shippingForm.address,
      shipping_city: shippingForm.city,
      shipping_state: shippingForm.state,
      shipping_postal_code: shippingForm.zipCode,
      shipping_country: 'CO',
      phone_number: shippingForm.phone,
      shipping: shippingCost, // En COP
      notes: shippingForm.notes || '',
      is_gift: giftMode,
      sender_username: giftMode ? user.username : null,
      receiver_username: giftMode ? recipientUsername : null,
      gift_message: giftMode ? giftMessage : ''
    };

    const response = await axios.post('/api/orders/wompi/create/', orderData);
    
    if (response.data.success) {
      // Guardar transaction_id para confirmar después
      localStorage.setItem('wompi_transaction_id', response.data.transaction_id);
      localStorage.setItem('wompi_order_data', JSON.stringify(orderData));
      
      // Redirigir a Wompi checkout
      window.location.href = response.data.payment_url;
    }
  } catch (error) {
    console.error('Error creating Wompi transaction:', error);
    showErrorMessage(error.response?.data?.error || 'Error al crear transacción');
  }
}
```

---

## 3️⃣ Confirmar Pago

### **POST /api/orders/wompi/confirm/**

**Cuándo llamar:**
- Después de que Wompi redirige al usuario de vuelta a tu sitio
- URL de retorno: `/checkout/wompi/success?id=TRANSACTION_ID`

**Request Body:**
```json
{
  "transaction_id": "12345-1234-1234-1234-123456789012",
  "customer_email": "customer@example.com",
  "customer_name": "Juan Pérez",
  "items": [
    {
      "woocommerce_product_id": 1234,
      "product_name": "Producto Ejemplo",
      "quantity": 2,
      "unit_price": 50000,
      "variation_id": 5679
    }
  ],
  "shipping_address": "Carrera 80 #50-25 Apto 301",
  "shipping_address_line_2": "Torre 2",
  "shipping_city": "Medellín",
  "shipping_state": "Antioquia",
  "shipping_postal_code": "050031",
  "shipping_country": "CO",
  "phone_number": "+57 300 1234567",
  "shipping": 15000,
  "notes": "Notas opcionales",
  "gift_message": "¡Feliz cumpleaños!"
}
```

**⚠️ IMPORTANTE:**
- Debes enviar **TODOS los datos de la orden** nuevamente (igual que en `/create/`)
- Agregar el `transaction_id` que retornó Wompi
- El backend verificará que el pago fue aprobado antes de crear la orden

**Response Success (201):**
```json
{
  "success": true,
  "message": "Order created successfully",
  "order": {
    "id": 123,
    "order_number": "ORD123456ABC",
    "total": "115000.00",
    "status": "processing",
    "email": "customer@example.com",
    "name": "Juan Pérez",
    "address_line_1": "Carrera 80 #50-25 Apto 301",
    "city": "Medellín",
    "state": "Antioquia",
    "country": "CO",
    "phone": "+57 300 1234567",
    "is_gift": false,
    "items": [
      {
        "id": 456,
        "woocommerce_product_id": 1234,
        "product_name": "Producto Ejemplo",
        "quantity": 2,
        "unit_price": "50000.00"
      }
    ],
    "created_at": "2025-01-23T12:00:00Z"
  },
  "payment": {
    "provider": "wompi",
    "transaction_id": "12345-1234-1234-1234-123456789012",
    "status": "APPROVED",
    "payer_email": "customer@example.com",
    "payer_name": "Juan Pérez"
  },
  "woocommerce_integration": {
    "status": "pending",
    "message": "Order is being sent to WooCommerce in background"
  }
}
```

**Response Error - Pago No Aprobado (400):**
```json
{
  "error": "Payment was not approved",
  "status": "DECLINED",
  "transaction_id": "12345-1234-1234-1234-123456789012"
}
```

**Response Error - Verificación Fallida (400):**
```json
{
  "error": "Payment verification failed",
  "details": "Transaction not found",
  "wompi_status": "FAILED"
}
```

**Ejemplo Frontend:**
```javascript
// Página: /checkout/wompi/success
async function confirmWompiPayment() {
  try {
    // Obtener transaction_id de la URL
    const urlParams = new URLSearchParams(window.location.search);
    const transactionId = urlParams.get('id');
    
    if (!transactionId) {
      throw new Error('No transaction ID found');
    }
    
    // Recuperar datos de la orden guardados en localStorage
    const orderData = JSON.parse(localStorage.getItem('wompi_order_data'));
    
    if (!orderData) {
      throw new Error('Order data not found');
    }
    
    // Confirmar pago con backend
    const response = await axios.post('/api/orders/wompi/confirm/', {
      transaction_id: transactionId,
      ...orderData
    });
    
    if (response.data.success) {
      // Limpiar localStorage
      localStorage.removeItem('wompi_transaction_id');
      localStorage.removeItem('wompi_order_data');
      
      // Limpiar carrito
      cartStore.clearCart();
      
      // Mostrar confirmación
      showSuccessMessage({
        orderNumber: response.data.order.order_number,
        total: response.data.order.total,
        email: response.data.order.email
      });
      
      // Redirigir a página de confirmación
      router.push(`/order-confirmation/${response.data.order.order_number}`);
    }
  } catch (error) {
    console.error('Error confirming Wompi payment:', error);
    
    if (error.response?.data?.status === 'DECLINED') {
      showErrorMessage('El pago fue rechazado. Por favor intenta con otro método de pago.');
    } else {
      showErrorMessage(error.response?.data?.error || 'Error al confirmar el pago');
    }
    
    // Redirigir de vuelta al checkout
    router.push('/checkout');
  }
}

// Llamar cuando la página carga
onMounted(() => {
  confirmWompiPayment();
});
```

---

## 🎨 Ejemplo de Componente Vue

```vue
<template>
  <div class="checkout-payment">
    <!-- Selector de método de pago -->
    <div class="payment-methods">
      <button 
        @click="selectPaymentMethod('paypal')"
        :class="{ active: paymentMethod === 'paypal' }"
      >
        <img src="/paypal-logo.png" alt="PayPal" />
        PayPal (USD)
      </button>
      
      <button 
        @click="selectPaymentMethod('wompi')"
        :class="{ active: paymentMethod === 'wompi' }"
        v-if="isColombianUser"
      >
        <img src="/wompi-logo.png" alt="Wompi" />
        Wompi (COP)
      </button>
    </div>

    <!-- Botón de pago -->
    <button 
      @click="processPayment"
      :disabled="processing"
      class="btn-pay"
    >
      {{ processing ? 'Procesando...' : `Pagar ${formatTotal}` }}
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useCartStore } from '@/stores/cart';
import { useCurrencyStore } from '@/stores/currency';
import axios from 'axios';

const cartStore = useCartStore();
const currencyStore = useCurrencyStore();

const paymentMethod = ref('paypal');
const processing = ref(false);

// Detectar si es usuario colombiano
const isColombianUser = computed(() => {
  return currencyStore.currentCurrency === 'COP';
});

// Formatear total según método de pago
const formatTotal = computed(() => {
  const total = cartStore.totalWithShipping;
  if (paymentMethod.value === 'wompi') {
    return `$${total.toLocaleString('es-CO')} COP`;
  } else {
    return `$${total.toFixed(2)} USD`;
  }
});

function selectPaymentMethod(method) {
  paymentMethod.value = method;
}

async function processPayment() {
  processing.value = true;
  
  try {
    if (paymentMethod.value === 'wompi') {
      await processWompiPayment();
    } else {
      await processPayPalPayment();
    }
  } catch (error) {
    console.error('Payment error:', error);
    alert('Error al procesar el pago');
  } finally {
    processing.value = false;
  }
}

async function processWompiPayment() {
  // Preparar datos de la orden
  const orderData = {
    customer_email: user.value.email,
    customer_name: user.value.fullName,
    items: cartStore.items.map(item => ({
      woocommerce_product_id: item.productId,
      product_name: item.name,
      quantity: item.quantity,
      unit_price: item.price,
      variation_id: item.variationId
    })),
    shipping_address: shippingForm.value.address,
    shipping_city: shippingForm.value.city,
    shipping_state: shippingForm.value.state,
    shipping_postal_code: shippingForm.value.zipCode,
    shipping_country: 'CO',
    phone_number: shippingForm.value.phone,
    shipping: cartStore.shippingCost,
    notes: shippingForm.value.notes,
    // Wishlist data (if coming from wishlist)
    is_from_wishlist: route.query.wishlistId ? true : false,
    wishlist_id: route.query.wishlistId || null,
    wishlist_name: route.query.wishlistName || null
  };

  // Crear transacción
  const response = await axios.post('/api/orders/wompi/create/', orderData);
  
  if (response.data.success) {
    // Guardar datos para confirmar después
    localStorage.setItem('wompi_transaction_id', response.data.transaction_id);
    localStorage.setItem('wompi_order_data', JSON.stringify(orderData));
    
    // Redirigir a Wompi
    window.location.href = response.data.payment_url;
  }
}

async function processPayPalPayment() {
  // Flujo PayPal existente (sin cambios)
  // ...
}
</script>
```

---

## 🔄 Página de Confirmación Wompi

```vue
<template>
  <div class="wompi-confirmation">
    <div v-if="loading" class="loading">
      <spinner />
      <p>Verificando tu pago...</p>
    </div>

    <div v-else-if="success" class="success">
      <check-icon />
      <h2>¡Pago Exitoso!</h2>
      <p>Número de orden: <strong>{{ orderNumber }}</strong></p>
      <p>Total: <strong>${{ total }} COP</strong></p>
      <p>Recibirás un email de confirmación en: {{ email }}</p>
      <button @click="goToOrders">Ver mis órdenes</button>
    </div>

    <div v-else class="error">
      <error-icon />
      <h2>Error en el Pago</h2>
      <p>{{ errorMessage }}</p>
      <button @click="goToCheckout">Volver al checkout</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

const loading = ref(true);
const success = ref(false);
const orderNumber = ref('');
const total = ref('');
const email = ref('');
const errorMessage = ref('');

onMounted(async () => {
  await confirmPayment();
});

async function confirmPayment() {
  try {
    // Obtener transaction_id de la URL
    const urlParams = new URLSearchParams(window.location.search);
    const transactionId = urlParams.get('id');
    
    if (!transactionId) {
      throw new Error('No se encontró el ID de transacción');
    }
    
    // Recuperar datos de la orden
    const orderData = JSON.parse(localStorage.getItem('wompi_order_data'));
    
    if (!orderData) {
      throw new Error('No se encontraron los datos de la orden');
    }
    
    // Confirmar pago
    const response = await axios.post('/api/orders/wompi/confirm/', {
      transaction_id: transactionId,
      ...orderData
    });
    
    if (response.data.success) {
      success.value = true;
      orderNumber.value = response.data.order.order_number;
      total.value = parseFloat(response.data.order.total).toLocaleString('es-CO');
      email.value = response.data.order.email;
      
      // Limpiar localStorage
      localStorage.removeItem('wompi_transaction_id');
      localStorage.removeItem('wompi_order_data');
      
      // Limpiar carrito
      cartStore.clearCart();
    }
  } catch (error) {
    console.error('Error confirming payment:', error);
    success.value = false;
    errorMessage.value = error.response?.data?.error || 'Error al confirmar el pago';
  } finally {
    loading.value = false;
  }
}

function goToOrders() {
  router.push('/orders');
}

function goToCheckout() {
  router.push('/checkout');
}
</script>
```

---

## 📱 Estados de Transacción Wompi

| Estado | Descripción | Acción Frontend |
|--------|-------------|-----------------|
| `APPROVED` | Pago aprobado | ✅ Crear orden |
| `DECLINED` | Pago rechazado | ❌ Mostrar error, volver a checkout |
| `PENDING` | Pago pendiente | ⏳ Mostrar mensaje de espera |
| `ERROR` | Error en transacción | ❌ Mostrar error, contactar soporte |
| `VOIDED` | Transacción anulada | ❌ Mostrar error |

---

## 🔐 Seguridad

### **Datos Sensibles**
- ❌ **NO** guardar datos de tarjeta en frontend
- ❌ **NO** enviar datos de tarjeta al backend
- ✅ Wompi maneja todos los datos sensibles
- ✅ Solo guardar `transaction_id` temporalmente

### **Validación**
```javascript
// Validar antes de crear transacción
function validateOrderData(data) {
  if (!data.customer_email || !data.customer_email.includes('@')) {
    throw new Error('Email inválido');
  }
  
  if (!data.items || data.items.length === 0) {
    throw new Error('El carrito está vacío');
  }
  
  if (!data.shipping_address || !data.shipping_city) {
    throw new Error('Dirección de envío incompleta');
  }
  
  if (!data.phone_number) {
    throw new Error('Teléfono requerido');
  }
  
  return true;
}
```

---

## 🎁 Compra de Wishlist con Wompi

Wompi soporta completamente el flujo de compra desde wishlist, igual que PayPal.

### **Campos Adicionales para Wishlist**

Cuando el usuario compra desde una wishlist, envía estos campos adicionales:

```javascript
{
  // ... todos los campos normales ...
  
  // Campos de wishlist
  "is_from_wishlist": true,
  "wishlist_id": 123,
  "wishlist_name": "Mi Lista de Deseos"
}
```

### **Comportamiento del Backend**

1. **Durante `/create/`**: Guarda datos de wishlist en cache
2. **Durante `/confirm/`**: 
   - Verifica que el pago fue aprobado
   - Crea la orden
   - **Remueve automáticamente** los items comprados de la wishlist
   - Si se compraron todos los items → wishlist queda vacía

### **Ejemplo: Comprar Wishlist Completa**

```javascript
// Usuario hace click en "Buy this wishlist"
async function buyWishlist(wishlist) {
  const orderData = {
    customer_email: user.email,
    customer_name: user.fullName,
    items: wishlist.items.map(item => ({
      woocommerce_product_id: item.product_id,
      product_name: item.product_name,
      quantity: item.quantity,
      unit_price: item.product_price,
      variation_id: item.variation_id
    })),
    shipping_address: shippingForm.address,
    shipping_city: shippingForm.city,
    shipping_state: shippingForm.state,
    shipping_postal_code: shippingForm.zipCode,
    shipping_country: 'CO',
    phone_number: shippingForm.phone,
    shipping: shippingCost,
    // Gift data (wishlist siempre es gift)
    is_gift: true,
    sender_username: user.username,
    receiver_username: wishlist.user_username,
    gift_message: giftMessage,
    // Wishlist data
    is_from_wishlist: true,
    wishlist_id: wishlist.id,
    wishlist_name: wishlist.name
  };

  // Crear transacción Wompi
  const response = await axios.post('/api/orders/wompi/create/', orderData);
  
  // Guardar y redirigir
  localStorage.setItem('wompi_order_data', JSON.stringify(orderData));
  window.location.href = response.data.payment_url;
}
```

### **Resultado Después de Confirmar**

```json
{
  "success": true,
  "order": {
    "id": 123,
    "is_gift": true,
    "sender_username": "juan",
    "receiver_username": "maria"
  },
  "payment": {
    "provider": "wompi",
    "status": "APPROVED"
  }
}
```

**⚠️ Nota:** Los items comprados se remueven automáticamente de la wishlist en el backend. No necesitas hacer ninguna llamada adicional desde el frontend.

---

## 🎯 Comparación PayPal vs Wompi

| Característica | PayPal | Wompi |
|---------------|--------|-------|
| **Moneda** | USD | COP |
| **Usuarios** | Internacionales | Colombia |
| **Create Endpoint** | `/paypal/create/` | `/wompi/create/` |
| **Confirm Endpoint** | `/paypal/capture/` | `/wompi/confirm/` |
| **Payment UI** | Popup | Redirect |
| **Datos a enviar** | ✅ Iguales | ✅ Iguales |
| **Response** | ✅ Mismo formato | ✅ Mismo formato |

---

## ✅ Checklist de Integración

- [ ] Agregar selector de método de pago en checkout
- [ ] Implementar función `createWompiTransaction()`
- [ ] Crear página `/checkout/wompi/success`
- [ ] Implementar función `confirmWompiPayment()`
- [ ] Guardar `transaction_id` y `order_data` en localStorage
- [ ] Limpiar localStorage después de confirmar
- [ ] Manejar errores de pago rechazado
- [ ] Mostrar mensajes de confirmación
- [ ] Limpiar carrito después de pago exitoso
- [ ] Probar flujo completo con credenciales de test

---

## 🧪 Testing

### **Credenciales de Test**
```
Public Key: pub_test_lHrCKMGf7JVnO4DgnYrdDPgj1DSqJ0OR
Environment: test
```

### **Tarjetas de Prueba Wompi**
```
Visa Aprobada:
  Número: 4242 4242 4242 4242
  CVV: 123
  Fecha: Cualquier fecha futura

Visa Rechazada:
  Número: 4111 1111 1111 1111
  CVV: 123
  Fecha: Cualquier fecha futura
```

### **Flujo de Prueba**
1. Agregar productos al carrito
2. Ir a checkout
3. Seleccionar "Wompi"
4. Completar datos de envío
5. Click en "Pagar"
6. Usar tarjeta de prueba en Wompi
7. Verificar redirección a `/checkout/wompi/success?id=xxx`
8. Verificar creación de orden en backend
9. Verificar email de confirmación

---

## 📞 Soporte

- **Documentación Wompi**: https://docs.wompi.co/
- **Panel de Comercios**: https://comercios.wompi.co/
- **Soporte Wompi**: soporte@wompi.co

---

## 🎉 Resumen

✅ **3 endpoints** para integrar Wompi  
✅ **Mismos datos** que PayPal  
✅ **Flujo simple**: Create → Redirect → Confirm  
✅ **Manejo de errores** incluido  
✅ **Ejemplos completos** de Vue  

**¿Dudas?** Revisa los ejemplos de código o consulta la documentación de Wompi.
