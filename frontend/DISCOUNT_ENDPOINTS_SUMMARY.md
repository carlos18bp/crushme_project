# 🎟️ Endpoints de Pago con Descuento - Resumen Completo

## 📌 Respuesta a tu pregunta

**¿Wompi tiene un endpoint separado para regalos?**

**NO** - Wompi usa el **MISMO endpoint** tanto para órdenes regulares como para regalos.

## 🔄 Endpoints del Backend

### 1️⃣ PayPal - Orden Regular
- **Endpoint**: `POST /api/orders/paypal/create/`
- **Función Frontend**: `paymentStore.createPayPalOrder(orderData)`
- **Ubicación**: `src/stores/modules/paymentStore.js` línea 66
- **Llamado desde**: `CheckoutView.vue` línea 984

### 2️⃣ PayPal - Regalo
- **Endpoint**: `POST /api/orders/gifts/send/`
- **Función Frontend**: `paymentStore.sendGift(orderData)`
- **Ubicación**: `src/stores/modules/paymentStore.js` línea 147
- **Llamado desde**: `CheckoutView.vue` línea 978

### 3️⃣ Wompi - Orden Regular Y Regalo (MISMO ENDPOINT)
- **Endpoint**: `POST /api/orders/wompi/create/`
- **Función Frontend**: `paymentStore.createWompiTransaction(orderData)`
- **Ubicación**: `src/stores/modules/paymentStore.js` línea 217
- **Llamado desde**: `CheckoutView.vue` línea 855
- **Diferenciación**: El backend usa el campo `is_gift: true/false` para saber si es regalo

## 📊 Datos Enviados (TODOS los endpoints)

```javascript
{
  // Items del carrito
  items: [
    {
      woocommerce_product_id: 123,
      product_name: "Producto",
      quantity: 2,
      unit_price: 7.93,
      woocommerce_variation_id: null,
      attributes: null
    }
  ],
  
  // Precios
  subtotal: 15.86,           // ⭐ SIN descuento (para validación)
  total: 17.32,              // ⭐ CON descuento aplicado
  shipping: 3.75,
  
  // Descuento
  discount_code: "SUMMER20", // ⭐ Solo si fue validado (puede ser null)
  
  // Datos del cliente
  customer_email: "user@example.com",
  customer_name: "John Doe",
  
  // Datos de envío (si es orden regular)
  shipping_address: "Calle 123",
  shipping_city: "Medellín",
  shipping_state: "Antioquia",
  shipping_postal_code: "050001",
  shipping_country: "Colombia",
  phone_number: "+57 300 1234567",
  notes: "Notas adicionales",
  
  // Datos de regalo (si is_gift: true)
  is_gift: true,
  receiver_username: "destinatario",
  gift_message: "¡Feliz cumpleaños!",
  sender_username: "remitente",
  
  // Datos de wishlist (si es de wishlist)
  is_from_wishlist: true,
  wishlist_id: 1,
  wishlist_name: "Mi Wishlist"
}
```

## 🎯 Resumen por Pasarela

### PayPal (USD)
- **2 endpoints diferentes**:
  1. Orden regular: `/api/orders/paypal/create/`
  2. Regalo: `/api/orders/gifts/send/`
- Ambos reciben `discount_code`, `subtotal` y `total`

### Wompi (COP)
- **1 solo endpoint**:
  1. Todo: `/api/orders/wompi/create/`
- Diferencia órdenes regulares de regalos por el campo `is_gift`
- Recibe `discount_code`, `subtotal` y `total`

## ✅ Estado Actual del Frontend

El frontend **YA está enviando** el `discount_code` correctamente en los **3 endpoints**:

1. ✅ `POST /api/orders/paypal/create/` - Recibe `discount_code`
2. ✅ `POST /api/orders/gifts/send/` - Recibe `discount_code`
3. ✅ `POST /api/orders/wompi/create/` - Recibe `discount_code`

**Código relevante** (CheckoutView.vue):
```javascript
// Línea 760 (para regalos) y 799 (para órdenes regulares)
discount_code: discountData.value ? discountData.value.code : null
```

El campo solo se envía si:
- El usuario ingresó un código
- El código fue validado exitosamente

## 🔧 Lo que el Backend Debe Hacer

En los **3 endpoints**, el backend debe:

1. **Leer** el campo `discount_code` del request
2. **Usar** el campo `total` (que ya incluye el descuento) en lugar de recalcularlo
3. **Crear** la orden en PayPal/Wompi con ese total
4. **Guardar** el `discount_code` en la orden (opcional, para reportes)

**Código sugerido para el backend**:
```python
# Leer datos del request
discount_code = data.get('discount_code')
total_from_frontend = data.get('total')
subtotal = data.get('subtotal')

# Usar el total del frontend (ya incluye descuento)
if total_from_frontend is not None:
    total_amount = float(total_from_frontend)
    logger.info(f"💰 Total con descuento: {total_amount}")
    
    if discount_code:
        logger.info(f"🎟️ Descuento aplicado: {discount_code}")
else:
    # Fallback: calcular si no viene del frontend
    items_total = sum(item['unit_price'] * item['quantity'] for item in items)
    shipping_cost = float(data.get('shipping', 0))
    total_amount = items_total + shipping_cost
```

## 📝 Archivos del Backend a Modificar

1. **`paypal_order_views.py`**
   - `create_paypal_order_data()` - Línea ~130
   
2. **`gift_views.py`**
   - `send_gift()` - Donde calcula el total
   
3. **`wompi_order_views.py`** (o similar)
   - `create_wompi_transaction()` - Donde calcula el total
