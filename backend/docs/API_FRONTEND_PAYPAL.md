# 📘 API PayPal - Documentación para Frontend

Esta documentación describe los endpoints públicos de la API de PayPal para la creación de órdenes con pago.

---

## 🌐 Endpoints Disponibles

### 1. Obtener Configuración de PayPal

**Endpoint:** `GET /api/orders/paypal/config/`

**Descripción:** Obtiene la configuración necesaria para inicializar el SDK de PayPal en el frontend.

**Autenticación:** ❌ No requerida (público)

**Respuesta Exitosa (200):**
```json
{
  "client_id": "AZDxjDScFpQtjWTOUtWKbyN_bDt4OgqaF4eYXlewfBP4-8aqX3PiV8e1GWU6liB2CUXlkA59kJXE7M6R",
  "currency": "USD",
  "mode": "sandbox"
}
```

**Ejemplo de uso:**
```javascript
// Obtener configuración de PayPal
const response = await fetch('http://localhost:8000/api/orders/paypal/config/');
const config = await response.json();

// Usar el client_id para cargar el SDK de PayPal
const script = document.createElement('script');
script.src = `https://www.paypal.com/sdk/js?client-id=${config.client_id}&currency=${config.currency}`;
document.body.appendChild(script);
```

---

### 2. Crear Orden de PayPal

**Endpoint:** `POST /api/orders/paypal/create/`

**Descripción:** Crea una orden de PayPal y devuelve el `order_id` para mostrar el popup de pago.

**Autenticación:** ❌ No requerida (público)

**Request Body:**
```json
{
  "customer_email": "cliente@example.com",
  "customer_name": "Juan Pérez",
  "items": [
    {
      "woocommerce_product_id": 1234,
      "product_name": "Producto Ejemplo",
      "quantity": 2,
      "unit_price": 25.99
    },
    {
      "woocommerce_product_id": 5678,
      "product_name": "Otro Producto",
      "quantity": 1,
      "unit_price": 15.50
    }
  ],
  "shipping_address": "Carrera 80 #50-25 Apto 301",
  "shipping_city": "Medellín",
  "shipping_state": "Antioquia",
  "shipping_postal_code": "050031",
  "shipping_country": "CO",
  "phone_number": "+57 300 1234567",
  "notes": "Dejar con el portero"
}
```

**Campos Requeridos:**
- ✅ `items` (array): Lista de productos
  - `woocommerce_product_id` (number): ID del producto en WooCommerce
  - `product_name` (string): Nombre del producto
  - `quantity` (number): Cantidad
  - `unit_price` (number): Precio unitario
- ✅ `shipping_address` (string): Dirección de envío
- ✅ `shipping_city` (string): Ciudad
- ✅ `shipping_state` (string): Departamento/Estado
- ✅ `shipping_postal_code` (string): Código postal
- ✅ `shipping_country` (string): Código del país (ej: "CO")

**Campos Opcionales:**
- `customer_email` (string): Email del cliente (default: "")
- `customer_name` (string): Nombre del cliente (default: "Guest")
- `phone_number` (string): Teléfono
- `notes` (string): Notas adicionales

**Respuesta Exitosa (201):**
```json
{
  "success": true,
  "message": "PayPal order created successfully",
  "paypal_order_id": "8HK12345ABCD6789",
  "total": "67.48",
  "items_count": 2
}
```

**Respuestas de Error:**

**400 - Carrito vacío:**
```json
{
  "error": "Cart is empty"
}
```

**400 - Formato de item inválido:**
```json
{
  "error": "Invalid item format. Each item must have: woocommerce_product_id, product_name, quantity, unit_price"
}
```

**400 - Información de envío incompleta:**
```json
{
  "error": "Missing required shipping information"
}
```

**500 - Error interno:**
```json
{
  "error": "Failed to create PayPal order",
  "details": "Detalle del error"
}
```

**Ejemplo de uso:**
```javascript
async function createPayPalOrder() {
  const orderData = {
    customer_email: 'cliente@example.com',
    customer_name: 'Juan Pérez',
    items: [
      {
        woocommerce_product_id: 1234,
        product_name: 'Producto Ejemplo',
        quantity: 2,
        unit_price: 25.99
      }
    ],
    shipping_address: 'Carrera 80 #50-25 Apto 301',
    shipping_city: 'Medellín',
    shipping_state: 'Antioquia',
    shipping_postal_code: '050031',
    shipping_country: 'CO',
    phone_number: '+57 300 1234567',
    notes: 'Dejar con el portero'
  };

  const response = await fetch('http://localhost:8000/api/orders/paypal/create/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(orderData)
  });

  const result = await response.json();
  
  if (result.success) {
    return result.paypal_order_id; // Usar este ID para el popup de PayPal
  } else {
    throw new Error(result.error);
  }
}
```

---

### 3. Capturar Pago de PayPal

**Endpoint:** `POST /api/orders/paypal/capture/`

**Descripción:** Captura el pago aprobado por el usuario y crea la orden en el sistema.

**Autenticación:** ❌ No requerida (público)

**Request Body:**
```json
{
  "paypal_order_id": "8HK12345ABCD6789",
  "customer_email": "cliente@example.com",
  "customer_name": "Juan Pérez",
  "items": [
    {
      "woocommerce_product_id": 1234,
      "product_name": "Producto Ejemplo",
      "quantity": 2,
      "unit_price": 25.99
    }
  ],
  "shipping_address": "Carrera 80 #50-25 Apto 301",
  "shipping_city": "Medellín",
  "shipping_state": "Antioquia",
  "shipping_postal_code": "050031",
  "shipping_country": "CO",
  "phone_number": "+57 300 1234567",
  "notes": "Dejar con el portero"
}
```

**Campos Requeridos:**
- ✅ `paypal_order_id` (string): ID de la orden de PayPal
- ✅ `items` (array): Mismos items enviados en create
- ✅ Mismos campos de envío que en create

**Respuesta Exitosa (201):**
```json
{
  "success": true,
  "message": "Order created successfully",
  "order": {
    "id": 123,
    "order_number": "ORD-20250103-1234",
    "status": "processing",
    "status_display": "Processing",
    "total": "67.48",
    "total_items": 2,
    "items": [
      {
        "id": 456,
        "product": {
          "id": 1234,
          "woocommerce_product_id": 1234,
          "name": "Producto Ejemplo",
          "price": "25.99",
          "image_url": null
        },
        "quantity": 2,
        "unit_price": "25.99",
        "subtotal": "51.98",
        "created_at": "2025-01-03T10:30:00Z"
      }
    ],
    "shipping_address": "Carrera 80 #50-25 Apto 301",
    "shipping_city": "Medellín",
    "shipping_state": "Antioquia",
    "shipping_postal_code": "050031",
    "shipping_country": "CO",
    "phone_number": "+57 300 1234567",
    "full_shipping_address": "Carrera 80 #50-25 Apto 301, Medellín, Antioquia 050031, CO",
    "notes": "Dejar con el portero",
    "created_at": "2025-01-03T10:30:00Z",
    "updated_at": "2025-01-03T10:30:00Z",
    "shipped_at": null,
    "delivered_at": null
  },
  "payment": {
    "provider": "paypal",
    "paypal_order_id": "8HK12345ABCD6789",
    "status": "COMPLETED",
    "payer_email": "cliente@paypal.com",
    "payer_name": "Juan Pérez"
  },
  "woocommerce_integration": {
    "sent": true,
    "woocommerce_order_id": 9876,
    "woocommerce_order_number": "9876"
  }
}
```

**Respuestas de Error:**

**400 - Falta ID de orden:**
```json
{
  "error": "PayPal order ID is required"
}
```

**400 - Pago fallido:**
```json
{
  "error": "Payment capture failed",
  "details": "Detalle del error de PayPal",
  "paypal_status": "FAILED"
}
```

**Ejemplo de uso:**
```javascript
async function capturePayPalOrder(paypalOrderId, orderData) {
  const captureData = {
    paypal_order_id: paypalOrderId,
    ...orderData // Mismos datos enviados en create
  };

  const response = await fetch('http://localhost:8000/api/orders/paypal/capture/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(captureData)
  });

  const result = await response.json();
  
  if (result.success) {
    console.log('✅ Orden creada:', result.order.order_number);
    console.log('💳 Pago:', result.payment.status);
    console.log('🛒 WooCommerce:', result.woocommerce_integration);
    return result.order;
  } else {
    throw new Error(result.error);
  }
}
```

---

## 🔄 Flujo Completo

```javascript
// PASO 1: Obtener configuración y cargar SDK de PayPal
async function initializePayPal() {
  const config = await fetch('http://localhost:8000/api/orders/paypal/config/')
    .then(res => res.json());
  
  // Cargar SDK de PayPal
  const script = document.createElement('script');
  script.src = `https://www.paypal.com/sdk/js?client-id=${config.client_id}&currency=${config.currency}`;
  script.onload = () => renderPayPalButtons();
  document.body.appendChild(script);
}

// PASO 2: Renderizar botones de PayPal
function renderPayPalButtons() {
  paypal.Buttons({
    // Crear orden en backend
    createOrder: async () => {
      const orderData = {
        customer_email: 'cliente@example.com',
        customer_name: 'Juan Pérez',
        items: [
          {
            woocommerce_product_id: 1234,
            product_name: 'Producto Ejemplo',
            quantity: 2,
            unit_price: 25.99
          }
        ],
        shipping_address: 'Carrera 80 #50-25 Apto 301',
        shipping_city: 'Medellín',
        shipping_state: 'Antioquia',
        shipping_postal_code: '050031',
        shipping_country: 'CO',
        phone_number: '+57 300 1234567',
        notes: 'Dejar con el portero'
      };

      const response = await fetch('http://localhost:8000/api/orders/paypal/create/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData)
      });

      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error);
      }
      
      // Guardar datos de la orden para usarlos después
      window.currentOrderData = orderData;
      
      return result.paypal_order_id;
    },

    // Capturar pago después de aprobación
    onApprove: async (data) => {
      const captureData = {
        paypal_order_id: data.orderID,
        ...window.currentOrderData // Usar los mismos datos
      };

      const response = await fetch('http://localhost:8000/api/orders/paypal/capture/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(captureData)
      });

      const result = await response.json();
      
      if (result.success) {
        alert(`✅ Pago exitoso! Orden: ${result.order.order_number}`);
        // Redirigir a página de confirmación
        window.location.href = `/order-confirmation/${result.order.id}`;
      } else {
        alert(`❌ Error: ${result.error}`);
      }
    },

    // Manejar errores
    onError: (err) => {
      console.error('Error en PayPal:', err);
      alert('❌ Hubo un problema con el pago. Por favor intenta de nuevo.');
    }
  }).render('#paypal-button-container');
}

// Inicializar
initializePayPal();
```

---

## 📝 Notas Importantes

### ✅ Ventajas del Flujo Actual

1. **Endpoints públicos**: No requieren autenticación
2. **Sin estado en backend**: No depende de carrito almacenado
3. **Flexibilidad**: Funciona para usuarios anónimos
4. **Seguridad**: El pago debe ser aprobado antes de crear la orden

### ⚠️ Consideraciones

1. **Los mismos datos deben enviarse en create y capture**: Guarda los datos de la orden después de `create` para enviarlos en `capture`
2. **Validación de PayPal**: El pago se valida en PayPal antes de crear la orden en el sistema
3. **Órdenes anónimas**: Las órdenes se crean sin usuario asociado (`user=null`)
4. **Integración con WooCommerce**: Después de crear la orden, se envía automáticamente a WooCommerce

### 🔐 Seguridad

- Los endpoints son públicos pero seguros porque:
  - El pago debe ser aprobado por PayPal
  - PayPal valida el monto y los datos
  - Solo después de la aprobación se crea la orden

### 💡 Tips

1. **Validación frontend**: Valida los campos requeridos antes de llamar a `create`
2. **Manejo de errores**: Muestra mensajes claros al usuario
3. **Loading states**: Muestra indicadores de carga durante las llamadas
4. **Guardar datos**: Guarda `orderData` después de `create` para usarlo en `capture`
5. **Testing**: Usa el modo `sandbox` para pruebas

---

## 🐛 Errores Comunes

### Error: "Cart is empty"
- **Causa**: El array `items` está vacío
- **Solución**: Asegúrate de enviar al menos un producto

### Error: "Missing required shipping information"
- **Causa**: Falta algún campo de envío requerido
- **Solución**: Verifica que todos los campos requeridos estén presentes

### Error: "Invalid item format"
- **Causa**: Los items no tienen todos los campos requeridos
- **Solución**: Cada item debe tener: `woocommerce_product_id`, `product_name`, `quantity`, `unit_price`

### Error: "Payment capture failed"
- **Causa**: El pago no fue aprobado en PayPal o hubo un error
- **Solución**: Verifica que el pago se haya aprobado correctamente

---

## 📞 Soporte

Para más información, consulta:
- [Documentación de PayPal SDK](https://developer.paypal.com/sdk/js/)
- [Guía rápida de PayPal](../QUICK_START_PAYPAL.md)
- [Diagrama de flujo](../PAYPAL_FLOW_DIAGRAM.md)

