# 💳 Integración Frontend: Checkout con PayPal

## 📋 Resumen del Flujo Completo

```
┌──────────────┐
│   Usuario    │
│ agrega items │
│  al carrito  │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│   Checkout Page  │
│  (Shipping Form) │
└──────┬───────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  1. Frontend → Backend: Crear orden PayPal          │
│     POST /api/orders/paypal/create/                 │
│     Recibe: paypal_order_id                         │
└──────┬──────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  2. PayPal SDK abre popup con paypal_order_id       │
│     Usuario aprueba/rechaza pago                    │
└──────┬──────────────────────────────────────────────┘
       │
       ├─── RECHAZADO → Mostrar error, no continuar
       │
       └─── APROBADO ▼
┌─────────────────────────────────────────────────────┐
│  3. Frontend → Backend: Capturar pago               │
│     POST /api/orders/paypal/capture/                │
│     • Captura pago en PayPal                        │
│     • Crea orden local                              │
│     • Envía a WooCommerce                           │
│     • Vacía carrito                                 │
└──────┬──────────────────────────────────────────────┘
       │
       ▼
┌──────────────────┐
│  Orden Creada ✅ │
│  Pago Confirmado │
└──────────────────┘
```

---

## 🔧 Setup Inicial

### 1. Instalar PayPal SDK (En tu HTML)

Agrega el script de PayPal en tu checkout page:

```html
<!-- En tu index.html o checkout page -->
<script src="https://www.paypal.com/sdk/js?client-id=YOUR_CLIENT_ID&currency=USD"></script>
```

**Nota:** Puedes obtener el `client-id` dinámicamente desde tu backend (ver endpoint de configuración).

### 2. Obtener Configuración de PayPal

```javascript
// GET /api/orders/paypal/config/
const getPayPalConfig = async () => {
  const response = await fetch('http://localhost:8000/api/orders/paypal/config/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const config = await response.json();
  // config = {
  //   client_id: "AfoqONwK05N...",
  //   currency: "USD",
  //   mode: "sandbox"
  // }
  
  return config;
};
```

---

## 🚀 Implementación del Flujo de Pago

### Paso 1: Crear Componente de Checkout

```jsx
// CheckoutPage.jsx (React ejemplo)
import { useState, useEffect } from 'react';

const CheckoutPage = () => {
  const [shippingData, setShippingData] = useState({
    shipping_address: '',
    shipping_city: '',
    shipping_state: '',
    shipping_postal_code: '',
    shipping_country: 'CO',
    phone_number: '',
    notes: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Cargar PayPal SDK dinámicamente
  useEffect(() => {
    loadPayPalScript();
  }, []);
  
  const loadPayPalScript = async () => {
    const config = await getPayPalConfig();
    
    const script = document.createElement('script');
    script.src = `https://www.paypal.com/sdk/js?client-id=${config.client_id}&currency=${config.currency}`;
    script.async = true;
    script.onload = () => {
      renderPayPalButton();
    };
    document.body.appendChild(script);
  };
  
  const renderPayPalButton = () => {
    window.paypal.Buttons({
      // Paso 1: Crear orden PayPal
      createOrder: async () => {
        try {
          const orderId = await createPayPalOrder();
          return orderId;
        } catch (error) {
          console.error('Error creating PayPal order:', error);
          setError('Failed to create payment order');
          throw error;
        }
      },
      
      // Paso 2: Usuario aprueba pago
      onApprove: async (data) => {
        try {
          setLoading(true);
          await capturePayPalOrder(data.orderID);
          // Redirigir a página de éxito
          window.location.href = '/order-success';
        } catch (error) {
          console.error('Error capturing payment:', error);
          setError('Payment capture failed');
        } finally {
          setLoading(false);
        }
      },
      
      // Usuario cancela pago
      onCancel: () => {
        setError('Payment was cancelled');
      },
      
      // Error en PayPal
      onError: (err) => {
        console.error('PayPal Error:', err);
        setError('An error occurred with PayPal');
      }
    }).render('#paypal-button-container');
  };
  
  return (
    <div className="checkout-page">
      <h1>Checkout</h1>
      
      {/* Formulario de envío */}
      <ShippingForm data={shippingData} onChange={setShippingData} />
      
      {/* Resumen del carrito */}
      <CartSummary />
      
      {/* Botón de PayPal (se renderiza aquí) */}
      <div id="paypal-button-container"></div>
      
      {/* Loading y errores */}
      {loading && <div>Processing payment...</div>}
      {error && <div className="error">{error}</div>}
    </div>
  );
};
```

---

## 📡 Endpoints del Backend

### **Endpoint 1: Obtener Configuración de PayPal**

```http
GET /api/orders/paypal/config/
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "client_id": "AfoqONwK05N0j548Xeff7ZdHfg699MJQj79RYRdCaGvN3ZQCA4Yu6ioEHD0zF1vdnLo_2UKaCqrwRAok",
  "currency": "USD",
  "mode": "sandbox"
}
```

---

### **Endpoint 2: Crear Orden PayPal**

```http
POST /api/orders/paypal/create/
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "shipping_address": "Carrera 80 #50-25 Apto 301",
  "shipping_city": "Medellín",
  "shipping_state": "Antioquia",
  "shipping_postal_code": "050031",
  "shipping_country": "CO",
  "phone_number": "+57 300 1234567",
  "notes": "Por favor llamar antes de entregar"
}
```

**Validaciones:**
- ✅ Usuario debe estar autenticado
- ✅ Debe tener carrito con productos
- ✅ Todos los campos de dirección son requeridos

**Respuesta Exitosa (201):**
```json
{
  "success": true,
  "message": "PayPal order created successfully",
  "paypal_order_id": "8EW12345678901234",
  "total": "150000.00",
  "items_count": 3
}
```

**Respuesta Error (400/500):**
```json
{
  "error": "Cart is empty"
}
```

---

### **Endpoint 3: Capturar Pago y Crear Orden**

```http
POST /api/orders/paypal/capture/
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "paypal_order_id": "8EW12345678901234",
  "shipping_address": "Carrera 80 #50-25 Apto 301",
  "shipping_city": "Medellín",
  "shipping_state": "Antioquia",
  "shipping_postal_code": "050031",
  "shipping_country": "CO",
  "phone_number": "+57 300 1234567",
  "notes": "Por favor llamar antes de entregar"
}
```

**¿Por qué enviar datos de nuevo?**  
Aunque ya los enviaste en el paso 1, el usuario puede cambiar datos en PayPal, así que enviamos los datos finales confirmados.

**Respuesta Exitosa (201):**
```json
{
  "success": true,
  "message": "Order created successfully",
  "order": {
    "id": 45,
    "order_number": "ORD123456ABCD1234",
    "status": "processing",
    "status_display": "Processing",
    "total": "150000.00",
    "total_items": 3,
    "items": [
      {
        "id": 1,
        "product": {
          "id": 2045,
          "woocommerce_product_id": 2045,
          "name": "Camiseta Básica",
          "price": "50000.00"
        },
        "quantity": 2,
        "unit_price": "50000.00",
        "subtotal": "100000.00"
      }
    ],
    "shipping_address": "Carrera 80 #50-25 Apto 301",
    "shipping_city": "Medellín",
    "shipping_state": "Antioquia",
    "shipping_postal_code": "050031",
    "shipping_country": "CO",
    "phone_number": "+57 300 1234567",
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

**Respuesta Error - Pago Rechazado (400):**
```json
{
  "error": "Payment capture failed",
  "details": "Insufficient funds",
  "paypal_status": "FAILED"
}
```

---

## 💻 Código Completo de Ejemplo

### Funciones JavaScript/TypeScript

```javascript
// api/orders.js
const API_URL = 'http://localhost:8000/api';

// Obtener token del localStorage o contexto
const getAuthToken = () => {
  return localStorage.getItem('access_token');
};

// 1. Obtener configuración de PayPal
export const getPayPalConfig = async () => {
  const response = await fetch(`${API_URL}/orders/paypal/config/`, {
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to get PayPal config');
  }
  
  return response.json();
};

// 2. Crear orden PayPal
export const createPayPalOrder = async (shippingData) => {
  const response = await fetch(`${API_URL}/orders/paypal/create/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(shippingData)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to create order');
  }
  
  const data = await response.json();
  return data.paypal_order_id;
};

// 3. Capturar pago PayPal
export const capturePayPalOrder = async (paypalOrderId, shippingData) => {
  const response = await fetch(`${API_URL}/orders/paypal/capture/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      paypal_order_id: paypalOrderId,
      ...shippingData
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to capture payment');
  }
  
  return response.json();
};
```

---

## 🎨 Componente React Completo

```jsx
// components/PayPalCheckout.jsx
import React, { useState, useEffect, useRef } from 'react';
import { createPayPalOrder, capturePayPalOrder, getPayPalConfig } from '../api/orders';

const PayPalCheckout = () => {
  const [shippingData, setShippingData] = useState({
    shipping_address: '',
    shipping_city: '',
    shipping_state: '',
    shipping_postal_code: '',
    shipping_country: 'CO',
    phone_number: '',
    notes: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const paypalRef = useRef();
  
  useEffect(() => {
    const loadPayPal = async () => {
      try {
        const config = await getPayPalConfig();
        
        // Cargar script de PayPal
        const script = document.createElement('script');
        script.src = `https://www.paypal.com/sdk/js?client-id=${config.client_id}&currency=${config.currency}`;
        script.async = true;
        
        script.onload = () => {
          // Renderizar botones de PayPal
          window.paypal.Buttons({
            style: {
              layout: 'vertical',
              color: 'gold',
              shape: 'rect',
              label: 'paypal'
            },
            
            createOrder: async () => {
              try {
                // Validar formulario
                if (!validateShippingData()) {
                  throw new Error('Please fill all required fields');
                }
                
                setLoading(true);
                setError(null);
                
                const orderId = await createPayPalOrder(shippingData);
                return orderId;
              } catch (err) {
                setError(err.message);
                throw err;
              } finally {
                setLoading(false);
              }
            },
            
            onApprove: async (data) => {
              try {
                setLoading(true);
                setError(null);
                
                const result = await capturePayPalOrder(data.orderID, shippingData);
                
                console.log('Order created:', result);
                setSuccess(true);
                
                // Redirigir a página de éxito
                setTimeout(() => {
                  window.location.href = `/order-success?order=${result.order.order_number}`;
                }, 2000);
                
              } catch (err) {
                setError(err.message);
              } finally {
                setLoading(false);
              }
            },
            
            onCancel: () => {
              setError('Payment was cancelled. Please try again.');
            },
            
            onError: (err) => {
              console.error('PayPal error:', err);
              setError('An error occurred with PayPal. Please try again.');
            }
          }).render(paypalRef.current);
        };
        
        document.body.appendChild(script);
      } catch (err) {
        setError('Failed to load PayPal. Please refresh the page.');
      }
    };
    
    loadPayPal();
  }, []);
  
  const validateShippingData = () => {
    const required = [
      'shipping_address',
      'shipping_city',
      'shipping_state',
      'shipping_postal_code',
      'phone_number'
    ];
    
    return required.every(field => shippingData[field] && shippingData[field].trim() !== '');
  };
  
  const handleInputChange = (field, value) => {
    setShippingData(prev => ({
      ...prev,
      [field]: value
    }));
  };
  
  return (
    <div className="paypal-checkout">
      <h2>Información de Envío</h2>
      
      <form className="shipping-form">
        <div className="form-group">
          <label>Dirección *</label>
          <input
            type="text"
            placeholder="Carrera 80 #50-25 Apto 301"
            value={shippingData.shipping_address}
            onChange={(e) => handleInputChange('shipping_address', e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label>Ciudad *</label>
          <input
            type="text"
            placeholder="Medellín"
            value={shippingData.shipping_city}
            onChange={(e) => handleInputChange('shipping_city', e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label>Departamento *</label>
          <input
            type="text"
            placeholder="Antioquia"
            value={shippingData.shipping_state}
            onChange={(e) => handleInputChange('shipping_state', e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label>Código Postal *</label>
          <input
            type="text"
            placeholder="050031"
            value={shippingData.shipping_postal_code}
            onChange={(e) => handleInputChange('shipping_postal_code', e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label>Teléfono *</label>
          <input
            type="tel"
            placeholder="+57 300 1234567"
            value={shippingData.phone_number}
            onChange={(e) => handleInputChange('phone_number', e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label>Notas (opcional)</label>
          <textarea
            placeholder="Instrucciones especiales..."
            value={shippingData.notes}
            onChange={(e) => handleInputChange('notes', e.target.value)}
          />
        </div>
      </form>
      
      {/* Botón de PayPal se renderiza aquí */}
      <div ref={paypalRef} className="paypal-buttons"></div>
      
      {/* Estados */}
      {loading && (
        <div className="loading">
          <p>Procesando pago...</p>
        </div>
      )}
      
      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
        </div>
      )}
      
      {success && (
        <div className="success-message">
          <p>✅ ¡Pago confirmado! Redirigiendo...</p>
        </div>
      )}
    </div>
  );
};

export default PayPalCheckout;
```

---

## 🎯 Flujo de Datos Completo

### Datos que van en cada paso:

#### **Paso 1: Crear Orden PayPal**
```javascript
// Frontend → Backend
POST /api/orders/paypal/create/
{
  shipping_address: "Carrera 80 #50-25 Apto 301",
  shipping_city: "Medellín",
  shipping_state: "Antioquia",
  shipping_postal_code: "050031",
  shipping_country: "CO",
  phone_number: "+57 300 1234567",
  notes: "Llamar antes de entregar"
}

// Backend lee del carrito:
// - Productos (woocommerce_product_id)
// - Cantidades
// - Precios
// - Total

// Backend → PayPal API
// Crea orden con todos los detalles

// PayPal → Backend → Frontend
{
  paypal_order_id: "8EW12345678901234"
}
```

#### **Paso 2: Usuario Aprueba en PayPal**
- PayPal abre popup
- Usuario login/aprueba
- PayPal cierra popup
- Frontend recibe `orderID` en `onApprove()`

#### **Paso 3: Capturar Pago**
```javascript
// Frontend → Backend
POST /api/orders/paypal/capture/
{
  paypal_order_id: "8EW12345678901234",
  shipping_address: "Carrera 80 #50-25 Apto 301",
  // ... mismo shipping data
}

// Backend:
// 1. Captura pago en PayPal ✅
// 2. Crea orden local ✅
// 3. Envía a WooCommerce ✅
// 4. Vacía carrito ✅

// Backend → Frontend
{
  success: true,
  order: { ... },
  payment: { ... },
  woocommerce_integration: { ... }
}
```

---

## ⚠️ Manejo de Errores

### Errores Comunes y Soluciones

**1. "Cart is empty"**
```javascript
// Verificar que hay productos en el carrito antes de mostrar checkout
const cartItems = await getCart();
if (cartItems.length === 0) {
  navigate('/cart');
}
```

**2. "Missing required shipping information"**
```javascript
// Validar campos antes de permitir pago
const validateForm = () => {
  if (!shippingAddress || !city || !state) {
    setError('Please fill all required fields');
    return false;
  }
  return true;
};
```

**3. "Payment capture failed"**
```javascript
// Mostrar mensaje al usuario y permitir reintentar
onError: (err) => {
  setError('Payment failed. Please try again or use a different payment method.');
  // No se creó orden, carrito sigue intacto
}
```

**4. "PayPal SDK not loaded"**
```javascript
// Verificar que el script cargó correctamente
useEffect(() => {
  const checkPayPal = setInterval(() => {
    if (window.paypal) {
      clearInterval(checkPayPal);
      renderPayPalButtons();
    }
  }, 100);
  
  // Timeout después de 10 segundos
  setTimeout(() => {
    clearInterval(checkPayPal);
    if (!window.paypal) {
      setError('Failed to load PayPal. Please refresh.');
    }
  }, 10000);
}, []);
```

---

## ✅ Checklist de Implementación

### Backend (Ya está listo ✅)
- [x] Servicio de PayPal configurado
- [x] Endpoints de crear orden
- [x] Endpoints de capturar pago
- [x] Integración con WooCommerce
- [x] Manejo de errores

### Frontend (Tu tarea)
- [ ] Instalar/cargar PayPal SDK
- [ ] Crear formulario de shipping
- [ ] Implementar función `createOrder`
- [ ] Implementar función `onApprove`
- [ ] Manejar estados de loading/error/success
- [ ] Validar formulario antes de pago
- [ ] Redirigir a página de éxito
- [ ] Manejar cancelación de pago
- [ ] Testing en sandbox

---

## 🧪 Testing en Sandbox

### Cuentas de Prueba PayPal

Usa estas cuentas para probar:

**Buyer Account (Comprador):**
- Email: `sb-buyer@personal.example.com`
- Password: `TestBuyer123`

**Seller Account (Vendedor - tu tienda):**
- Ya configurada con tus credenciales en settings.py

### Tarjetas de Prueba

PayPal proporciona tarjetas de prueba automáticamente en sandbox.

### Ver Transacciones

1. Login en https://www.sandbox.paypal.com
2. Ve a "Activity" para ver todas las transacciones de prueba

---

## 📱 Mobile Considerations

El SDK de PayPal es responsive, pero considera:

```javascript
style: {
  layout: 'vertical',  // Mejor para mobile
  color: 'gold',
  shape: 'rect',
  label: 'paypal',
  height: 55  // Altura táctil adecuada
}
```

---

## 🌍 Cambiar Moneda

Para cambiar de USD a COP (Pesos Colombianos):

**Backend:** `paypal_service.py`
```python
'currency_code': 'COP',  # Cambiar todas las instancias
```

**Frontend:** PayPal SDK
```html
<script src="https://www.paypal.com/sdk/js?client-id=XXX&currency=COP"></script>
```

**⚠️ Nota:** PayPal puede tener limitaciones de moneda según tu país. Verifica en [PayPal Currency Codes](https://developer.paypal.com/docs/reports/reference/paypal-supported-currencies/).

---

## 📞 Soporte

Si tienes dudas:
1. Revisa logs del backend (búsca "PayPal" o "❌")
2. Revisa consola del navegador
3. Verifica que las credenciales sean correctas en `settings.py`
4. Usa el modo sandbox para testing

---

**Última actualización:** Octubre 3, 2025  
**Versión:** 1.0  
**PayPal SDK:** v2 (Orders API)

