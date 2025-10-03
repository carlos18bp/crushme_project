# 🔄 Flujo Completo: PayPal + WooCommerce

## 📊 Diagrama de Secuencia

```
┌─────────┐          ┌──────────┐          ┌─────────┐          ┌────────────┐
│ Usuario │          │ Frontend │          │ Backend │          │   PayPal   │
│         │          │ (React)  │          │ Django  │          │    API     │
└────┬────┘          └─────┬────┘          └────┬────┘          └──────┬─────┘
     │                     │                     │                      │
     │  1. Llena datos    │                     │                      │
     │   de shipping      │                     │                      │
     │─────────────────>  │                     │                      │
     │                     │                     │                      │
     │  2. Click PayPal   │                     │                      │
     │─────────────────>  │                     │                      │
     │                     │                     │                      │
     │                     │ POST /paypal/create/│                      │
     │                     │ + shipping data     │                      │
     │                     │──────────────────> │                      │
     │                     │                     │                      │
     │                     │                     │ Lee carrito del user │
     │                     │                     │ (productos, precios) │
     │                     │                     │                      │
     │                     │                     │  POST /v2/checkout/  │
     │                     │                     │      orders          │
     │                     │                     │───────────────────> │
     │                     │                     │                      │
     │                     │                     │  paypal_order_id     │
     │                     │                     │ <─────────────────  │
     │                     │                     │                      │
     │                     │   paypal_order_id   │                      │
     │                     │ <────────────────  │                      │
     │                     │                     │                      │
     │  3. Abre popup     │                     │                      │
     │    PayPal con      │                     │                      │
     │    order_id        │                     │                      │
     │ <──────────────────│                     │                      │
     │                     │                     │                      │
     │  4. Login PayPal   │                     │                      │
     │    Revisa orden    │                     │                      │
     │    Aprueba pago    │                     │                      │
     │────────────────────────────────────────────────────────────────>│
     │                     │                     │                      │
     │  ✅ Pago aprobado  │                     │                      │
     │ <────────────────────────────────────────────────────────────── │
     │                     │                     │                      │
     │                     │ POST /paypal/capture/                     │
     │                     │ + paypal_order_id   │                      │
     │                     │ + shipping data     │                      │
     │                     │──────────────────> │                      │
     │                     │                     │                      │
     │                     │                     │ POST /v2/checkout/   │
     │                     │                     │ orders/{id}/capture  │
     │                     │                     │───────────────────> │
     │                     │                     │                      │
     │                     │                     │ ✅ Payment captured  │
     │                     │                     │ <─────────────────  │
     │                     │                     │                      │
     │                     │                     │ 💾 Crea Order local  │
     │                     │                     │ 💾 Crea OrderItems   │
     │                     │                     │                      │
     │                     │                     │                      │
     │                     │                     ├──────────────┐       │
     │                     │                     │ WooCommerce  │       │
     │                     │                     │ POST orders  │       │
     │                     │                     │<─────────────┘       │
     │                     │                     │                      │
     │                     │                     │ 🧹 Vacía carrito     │
     │                     │                     │                      │
     │                     │   Order + Payment   │                      │
     │                     │   details           │                      │
     │                     │ <────────────────  │                      │
     │                     │                     │                      │
     │  5. Muestra éxito  │                     │                      │
     │    Redirige a      │                     │                      │
     │    /order-success  │                     │                      │
     │ <──────────────────│                     │                      │
     │                     │                     │                      │
```

---

## 🎯 Estados del Sistema

### Estado 1: Checkout Inicial
```
Cart: 
  - Product 2045 (Camiseta) x2 = $100
  - Product 2046 (Pantalón) x1 = $175
  Total: $275

Shipping Form:
  ✅ Dirección completa
  ✅ Ciudad, Estado
  ✅ Código postal
  ✅ Teléfono

Button: "Pagar con PayPal" (activo)
```

### Estado 2: Orden PayPal Creada
```
PayPal Order ID: "8EW12345678901234"
Status: "CREATED"
Amount: $275 USD

Backend temporal:
  - NO se ha creado Order en Django
  - NO se ha enviado a WooCommerce
  - Carrito sigue lleno
```

### Estado 3: Usuario Aprueba Pago
```
PayPal Order ID: "8EW12345678901234"
Status: "APPROVED"
Payer: customer@example.com

Popup de PayPal se cierra
Frontend ejecuta onApprove()
```

### Estado 4: Captura Completa ✅
```
Django Order:
  - ID: 45
  - Number: "ORD123456ABCD1234"
  - Status: "processing"
  - Total: $275

PayPal:
  - Captured: ✅
  - Transaction ID: "CAPTURE123456"

WooCommerce:
  - Order ID: 8765
  - Status: "on-hold"

Cart: VACÍO ✅
```

---

## 📋 Datos en Cada Etapa

### Etapa 1: POST /api/orders/paypal/create/

**Request:**
```json
{
  "shipping_address": "Carrera 80 #50-25 Apto 301",
  "shipping_city": "Medellín",
  "shipping_state": "Antioquia",
  "shipping_postal_code": "050031",
  "shipping_country": "CO",
  "phone_number": "+57 300 1234567",
  "notes": "Llamar antes de entregar"
}
```

**Backend lee del Cart del usuario:**
```python
Cart.objects.get(user=request.user)
# Items:
#   - CartItem(woocommerce_product_id=2045, product_name="Camiseta", quantity=2, unit_price=50.00)
#   - CartItem(woocommerce_product_id=2046, product_name="Pantalón", quantity=1, unit_price=175.00)
# Total: 275.00
```

**Backend envía a PayPal:**
```json
{
  "intent": "CAPTURE",
  "purchase_units": [{
    "amount": {
      "currency_code": "USD",
      "value": "275.00",
      "breakdown": {
        "item_total": { "currency_code": "USD", "value": "275.00" }
      }
    },
    "items": [
      {
        "name": "Camiseta",
        "quantity": "2",
        "unit_amount": { "currency_code": "USD", "value": "50.00" }
      },
      {
        "name": "Pantalón",
        "quantity": "1",
        "unit_amount": { "currency_code": "USD", "value": "175.00" }
      }
    ],
    "shipping": {
      "name": { "full_name": "Juan Pérez" },
      "address": {
        "address_line_1": "Carrera 80 #50-25 Apto 301",
        "admin_area_2": "Medellín",
        "admin_area_1": "Antioquia",
        "postal_code": "050031",
        "country_code": "CO"
      }
    }
  }]
}
```

**Response:**
```json
{
  "success": true,
  "paypal_order_id": "8EW12345678901234",
  "total": "275.00",
  "items_count": 2
}
```

---

### Etapa 2: Usuario en PayPal

**PayPal muestra:**
```
┌─────────────────────────────────┐
│        PayPal Checkout          │
├─────────────────────────────────┤
│ Log in to your PayPal account  │
│                                 │
│ Email: [customer@example.com ]  │
│ Password: [**************]      │
│                                 │
│ ─────────────────────────────  │
│                                 │
│ Order Summary:                  │
│ • Camiseta x2      $100.00      │
│ • Pantalón x1      $175.00      │
│                                 │
│ Total:             $275.00 USD  │
│                                 │
│ Ship to:                        │
│ Juan Pérez                      │
│ Carrera 80 #50-25 Apto 301     │
│ Medellín, Antioquia            │
│ 050031, Colombia                │
│                                 │
│ [Cancel]    [Pay Now]           │
└─────────────────────────────────┘
```

---

### Etapa 3: POST /api/orders/paypal/capture/

**Request:**
```json
{
  "paypal_order_id": "8EW12345678901234",
  "shipping_address": "Carrera 80 #50-25 Apto 301",
  "shipping_city": "Medellín",
  "shipping_state": "Antioquia",
  "shipping_postal_code": "050031",
  "shipping_country": "CO",
  "phone_number": "+57 300 1234567",
  "notes": "Llamar antes de entregar"
}
```

**Backend procesa:**

1. **Captura pago en PayPal:**
```python
paypal_service.capture_order("8EW12345678901234")
# Response: {
#   "success": True,
#   "status": "COMPLETED",
#   "payer_email": "customer@example.com"
# }
```

2. **Crea Order en Django:**
```python
Order.objects.create(
    user=request.user,
    email="customer@example.com",
    name="Juan Pérez",
    total=275.00,
    address_line_1="Carrera 80 #50-25 Apto 301",
    city="Medellín",
    state="Antioquia",
    zipcode="050031",
    country="CO",
    phone="+57 300 1234567",
    status="processing"
)
# order_number: "ORD123456ABCD1234"
```

3. **Crea OrderItems:**
```python
OrderItem.objects.create(
    order=order,
    woocommerce_product_id=2045,
    product_name="Camiseta",
    quantity=2,
    unit_price=50.00
)
OrderItem.objects.create(
    order=order,
    woocommerce_product_id=2046,
    product_name="Pantalón",
    quantity=1,
    unit_price=175.00
)
```

4. **Envía a WooCommerce:**
```python
woocommerce_order_service.send_order(order)
# Parsea dirección colombiana
# Envía POST a WooCommerce API
```

5. **Vacía carrito:**
```python
cart.clear()
```

**Response Final:**
```json
{
  "success": true,
  "message": "Order created successfully",
  "order": {
    "id": 45,
    "order_number": "ORD123456ABCD1234",
    "status": "processing",
    "total": "275.00",
    "total_items": 3,
    "items": [
      {
        "product": {
          "woocommerce_product_id": 2045,
          "name": "Camiseta"
        },
        "quantity": 2,
        "unit_price": "50.00",
        "subtotal": "100.00"
      },
      {
        "product": {
          "woocommerce_product_id": 2046,
          "name": "Pantalón"
        },
        "quantity": 1,
        "unit_price": "175.00",
        "subtotal": "175.00"
      }
    ],
    "shipping_address": "Carrera 80 #50-25 Apto 301",
    "shipping_city": "Medellín",
    "created_at": "2025-10-03T15:30:00Z"
  },
  "payment": {
    "provider": "paypal",
    "paypal_order_id": "8EW12345678901234",
    "status": "COMPLETED",
    "payer_email": "customer@example.com",
    "payer_name": "Juan Pérez"
  },
  "woocommerce_integration": {
    "sent": true,
    "woocommerce_order_id": 8765,
    "woocommerce_order_number": "8765"
  }
}
```

---

## ❌ Flujos de Error

### Error 1: PayPal Rechaza Pago

```
Usuario en PayPal → Fondos insuficientes

PayPal → Backend: "DECLINED"

Backend NO crea Order
Backend NO envía a WooCommerce
Carrito sigue intacto

Frontend recibe:
{
  "error": "Payment capture failed",
  "details": "Insufficient funds",
  "paypal_status": "FAILED"
}

Usuario puede:
- Intentar con otra tarjeta
- Usar otro método de pago
```

### Error 2: WooCommerce Falla

```
PayPal: ✅ Pago capturado
Django: ✅ Order creada (ID: 45)
WooCommerce: ❌ API error (timeout)

Response:
{
  "success": true,
  "order": { ... },  ✅
  "payment": { ... }, ✅
  "woocommerce_integration": {
    "sent": false, ❌
    "error": "Connection timeout"
  }
}

Orden se guardó localmente
Pago se procesó correctamente
WooCommerce se puede reintentar manualmente
```

### Error 3: Carrito Vacío

```
POST /api/orders/paypal/create/

Backend verifica:
  cart = Cart.objects.get(user=user)
  if cart.is_empty: ❌

Response (400):
{
  "error": "Cart is empty"
}

No se crea orden en PayPal
Usuario debe agregar productos primero
```

---

## 🔐 Seguridad

### Validaciones Implementadas

1. **Autenticación:** ✅ JWT Token requerido
2. **Cart ownership:** ✅ Solo el dueño puede crear orden de su carrito
3. **PayPal verification:** ✅ Captura se verifica con PayPal API
4. **Amount matching:** ✅ Total calculado en backend, no viene del frontend
5. **Transaction atomic:** ✅ Todo o nada (Order + OrderItems + clear cart)

### Datos Sensibles

- ❌ Cliente ID/Secret NUNCA van al frontend
- ✅ Solo `client_id` público se envía
- ✅ Access tokens se manejan en backend
- ✅ Captura de pago solo se hace desde backend autenticado

---

## 📈 Métricas y Logs

### Logs que verás en el backend:

```
✅ PayPal order created for user juanperez: 8EW12345678901234
✅ PayPal payment captured: 8EW12345678901234
✅ Order ORD123456ABCD1234 created locally
✅ Order ORD123456ABCD1234 sent to WooCommerce successfully
✅ Cart cleared for user juanperez
```

### Logs de error:

```
❌ PayPal order creation failed: Authentication failed
❌ PayPal capture failed: Insufficient funds
⚠️ Order ORD123456ABCD1234 created but WooCommerce sync failed: Connection timeout
```

---

**Versión:** 1.0  
**Última actualización:** Octubre 3, 2025

