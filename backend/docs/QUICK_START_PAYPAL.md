# ⚡ Quick Start: PayPal Checkout (5 minutos)

## 🎯 Integración Mínima

### 1️⃣ HTML Simple (Sin Framework)

```html
<!DOCTYPE html>
<html>
<head>
    <title>PayPal Checkout</title>
    <script src="https://www.paypal.com/sdk/js?client-id=AfoqONwK05N0j548Xeff7ZdHfg699MJQj79RYRdCaGvN3ZQCA4Yu6ioEHD0zF1vdnLo_2UKaCqrwRAok&currency=USD"></script>
</head>
<body>
    <h1>Checkout</h1>
    
    <!-- Formulario de Envío -->
    <form id="shipping-form">
        <input type="text" id="address" placeholder="Dirección" required>
        <input type="text" id="city" placeholder="Ciudad" required>
        <input type="text" id="state" placeholder="Departamento" required>
        <input type="text" id="zipcode" placeholder="Código Postal" required>
        <input type="tel" id="phone" placeholder="Teléfono" required>
    </form>
    
    <!-- Botón de PayPal -->
    <div id="paypal-button-container"></div>
    
    <div id="result"></div>
    
    <script>
        const API_URL = 'http://localhost:8000/api';
        const TOKEN = localStorage.getItem('access_token'); // Tu token JWT
        
        // Función para obtener datos del formulario
        function getShippingData() {
            return {
                shipping_address: document.getElementById('address').value,
                shipping_city: document.getElementById('city').value,
                shipping_state: document.getElementById('state').value,
                shipping_postal_code: document.getElementById('zipcode').value,
                shipping_country: 'CO',
                phone_number: document.getElementById('phone').value,
                notes: ''
            };
        }
        
        // Renderizar botones de PayPal
        paypal.Buttons({
            // Paso 1: Crear orden
            createOrder: async function() {
                const shippingData = getShippingData();
                
                const response = await fetch(`${API_URL}/orders/paypal/create/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${TOKEN}`
                    },
                    body: JSON.stringify(shippingData)
                });
                
                const data = await response.json();
                return data.paypal_order_id;
            },
            
            // Paso 2: Capturar pago
            onApprove: async function(data) {
                const shippingData = getShippingData();
                
                const response = await fetch(`${API_URL}/orders/paypal/capture/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${TOKEN}`
                    },
                    body: JSON.stringify({
                        paypal_order_id: data.orderID,
                        ...shippingData
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('result').innerHTML = 
                        `<h2>✅ Pago exitoso!</h2>
                         <p>Orden: ${result.order.order_number}</p>`;
                } else {
                    document.getElementById('result').innerHTML = 
                        `<h2>❌ Error</h2><p>${result.error}</p>`;
                }
            }
        }).render('#paypal-button-container');
    </script>
</body>
</html>
```

---

### 2️⃣ React (Versión Mínima)

```jsx
// PayPalCheckout.jsx
import { useEffect, useRef } from 'react';

const PayPalCheckout = () => {
  const paypalRef = useRef();
  const API_URL = 'http://localhost:8000/api';
  const TOKEN = localStorage.getItem('access_token');
  
  useEffect(() => {
    const script = document.createElement('script');
    script.src = `https://www.paypal.com/sdk/js?client-id=AfoqONwK05N0j548Xeff7ZdHfg699MJQj79RYRdCaGvN3ZQCA4Yu6ioEHD0zF1vdnLo_2UKaCqrwRAok&currency=USD`;
    script.async = true;
    script.onload = () => {
      window.paypal.Buttons({
        createOrder: async () => {
          const res = await fetch(`${API_URL}/orders/paypal/create/`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${TOKEN}`
            },
            body: JSON.stringify({
              shipping_address: "Carrera 80 #50-25",
              shipping_city: "Medellín",
              shipping_state: "Antioquia",
              shipping_postal_code: "050031",
              shipping_country: "CO",
              phone_number: "+57 300 1234567"
            })
          });
          const data = await res.json();
          return data.paypal_order_id;
        },
        
        onApprove: async (data) => {
          const res = await fetch(`${API_URL}/orders/paypal/capture/`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${TOKEN}`
            },
            body: JSON.stringify({
              paypal_order_id: data.orderID,
              shipping_address: "Carrera 80 #50-25",
              shipping_city: "Medellín",
              shipping_state: "Antioquia",
              shipping_postal_code: "050031",
              shipping_country: "CO",
              phone_number: "+57 300 1234567"
            })
          });
          const result = await res.json();
          console.log('Orden creada:', result);
          alert(`¡Pago exitoso! Orden: ${result.order.order_number}`);
        }
      }).render(paypalRef.current);
    };
    document.body.appendChild(script);
  }, []);
  
  return <div ref={paypalRef}></div>;
};

export default PayPalCheckout;
```

---

### 3️⃣ Vue.js (Versión Mínima)

```vue
<template>
  <div>
    <h2>Checkout con PayPal</h2>
    <div ref="paypalContainer"></div>
  </div>
</template>

<script>
export default {
  name: 'PayPalCheckout',
  mounted() {
    const script = document.createElement('script');
    script.src = `https://www.paypal.com/sdk/js?client-id=AfoqONwK05N0j548Xeff7ZdHfg699MJQj79RYRdCaGvN3ZQCA4Yu6ioEHD0zF1vdnLo_2UKaCqrwRAok&currency=USD`;
    script.async = true;
    script.onload = this.renderPayPalButton;
    document.body.appendChild(script);
  },
  
  methods: {
    async renderPayPalButton() {
      window.paypal.Buttons({
        createOrder: async () => {
          const response = await fetch('http://localhost:8000/api/orders/paypal/create/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({
              shipping_address: "Carrera 80 #50-25",
              shipping_city: "Medellín",
              shipping_state: "Antioquia",
              shipping_postal_code: "050031",
              shipping_country: "CO",
              phone_number: "+57 300 1234567"
            })
          });
          const data = await response.json();
          return data.paypal_order_id;
        },
        
        onApprove: async (data) => {
          const response = await fetch('http://localhost:8000/api/orders/paypal/capture/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({
              paypal_order_id: data.orderID,
              shipping_address: "Carrera 80 #50-25",
              shipping_city: "Medellín",
              shipping_state: "Antioquia",
              shipping_postal_code: "050031",
              shipping_country: "CO",
              phone_number: "+57 300 1234567"
            })
          });
          const result = await response.json();
          alert(`¡Orden creada! ${result.order.order_number}`);
        }
      }).render(this.$refs.paypalContainer);
    }
  }
};
</script>
```

---

## 📋 Resumen de 3 Pasos

### **Paso 1: Cargar SDK**
```html
<script src="https://www.paypal.com/sdk/js?client-id=TU_CLIENT_ID&currency=USD"></script>
```

### **Paso 2: Crear Orden**
```javascript
POST /api/orders/paypal/create/
{
  "shipping_address": "Dirección",
  "shipping_city": "Ciudad",
  "shipping_state": "Estado",
  "shipping_postal_code": "Código",
  "shipping_country": "CO",
  "phone_number": "Teléfono"
}

→ Retorna: { "paypal_order_id": "XXX" }
```

### **Paso 3: Capturar Pago**
```javascript
POST /api/orders/paypal/capture/
{
  "paypal_order_id": "XXX",
  // ... mismo shipping data
}

→ Retorna: { "success": true, "order": {...} }
```

---

## ✅ Checklist Rápido

- [ ] Agregar script de PayPal SDK
- [ ] Obtener token JWT del usuario
- [ ] Crear formulario de shipping
- [ ] Implementar `createOrder`
- [ ] Implementar `onApprove`
- [ ] Probar con cuenta sandbox de PayPal

---

## 🧪 Testing Rápido

1. **Asegúrate de tener productos en el carrito:**
```javascript
// Agregar producto al carrito primero
POST /api/cart/add-product/
{
  "woocommerce_product_id": 2045,
  "quantity": 2
}
```

2. **Usar cuenta sandbox:**
   - Email: `sb-buyer@personal.example.com`
   - Password: (generada por PayPal)

3. **Ver logs en backend:**
```bash
# Terminal del backend
✅ PayPal order created for user...
✅ PayPal payment captured...
✅ Order ORD... created locally
```

---

## 🔗 URLs de los Endpoints

```
Backend Base: http://localhost:8000/api

Config:   GET    /orders/paypal/config/
Create:   POST   /orders/paypal/create/
Capture:  POST   /orders/paypal/capture/
```

---

## 💡 Tips Rápidos

1. **No se crea orden si:**
   - Carrito está vacío
   - Usuario no autenticado
   - Datos de shipping incompletos

2. **PayPal rechaza pago:**
   - No se crea orden local
   - Usuario puede reintentar
   - Carrito sigue intacto

3. **Errores comunes:**
   - Token expirado → Renovar token
   - CORS error → Verificar CORS_ALLOWED_ORIGINS
   - PayPal SDK no carga → Verificar client_id

---

## 📱 Responsive (Opcional)

Para que funcione bien en móvil:

```javascript
paypal.Buttons({
  style: {
    layout: 'vertical',
    height: 55
  },
  // ... resto del código
})
```

---

## 🎨 Personalizar Botón

```javascript
style: {
  layout: 'vertical',    // o 'horizontal'
  color:  'gold',        // 'blue', 'silver', 'white', 'black'
  shape:  'rect',        // o 'pill'
  label:  'paypal',      // 'checkout', 'pay', 'buynow'
  height: 55
}
```

---

## 🚀 ¿Listo para Producción?

1. Cambiar en `settings.py`:
```python
PAYPAL_MODE = 'live'  # Cambiar de 'sandbox' a 'live'
PAYPAL_CLIENT_ID = 'TU_CLIENT_ID_DE_PRODUCCION'
PAYPAL_CLIENT_SECRET = 'TU_CLIENT_SECRET_DE_PRODUCCION'
```

2. Usar URL de producción en frontend:
```javascript
const API_URL = 'https://tu-dominio.com/api';
```

3. **IMPORTANTE:** Mover credenciales a variables de entorno:
```bash
export PAYPAL_CLIENT_ID="..."
export PAYPAL_CLIENT_SECRET="..."
```

---

**¡Eso es todo!** En 5 minutos deberías tener PayPal funcionando. 🎉

Para más detalles, revisa: `FRONTEND_PAYPAL_CHECKOUT.md`

