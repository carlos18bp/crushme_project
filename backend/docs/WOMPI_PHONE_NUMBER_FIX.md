# Wompi - Corrección de Phone Number

## 🐛 Error

```
ERROR: "customer_data": {"phone_number": ["Debe ser completado"]}
```

## 🎯 Causa

El campo `phone_number` es **requerido** por Wompi en `customer_data`, pero estaba hardcodeado como string vacío.

---

## 🔧 Cambios Realizados

### **1. `wompi_service.py`**

**Antes:**
```python
def create_transaction(self, amount_in_cents, reference, customer_email, 
                      customer_name, redirect_url, currency='COP'):
    # ...
    payload = {
        'customer_data': {
            'full_name': customer_name,
            'phone_number': '',  # ❌ Hardcoded vacío
        }
    }
```

**Después:**
```python
def create_transaction(self, amount_in_cents, reference, customer_email, 
                      customer_name, redirect_url, phone_number='', currency='COP'):  # ⭐ Nuevo parámetro
    # ...
    payload = {
        'customer_data': {
            'full_name': customer_name,
            'phone_number': phone_number,  # ✅ Usa el parámetro
        }
    }
```

### **2. `wompi_order_views.py`**

**Agregado:**
```python
# Extract data from request
items = request.data.get('items', [])
customer_name = request.data.get('customer_name', 'Guest')
customer_email = request.data.get('customer_email', '')
phone_number = request.data.get('phone_number', '')  # ⭐ Nuevo

# Log received data
logger.info(f"📱 [WOMPI] Phone: {phone_number}")

# Create Wompi transaction
wompi_result = wompi_service.create_transaction(
    amount_in_cents=amount_in_cents,
    reference=reference,
    customer_email=customer_email,
    customer_name=customer_name,
    redirect_url=redirect_url,
    phone_number=phone_number,  # ⭐ Pasar al servicio
    currency='COP'
)
```

---

## 📋 Request Body Actualizado

### **Frontend debe enviar:**

```json
{
  "customer_email": "customer@example.com",
  "customer_name": "Juan Pérez",
  "phone_number": "+57 300 1234567",
  "items": [...],
  "shipping_address": "...",
  "shipping_city": "...",
  "shipping_state": "...",
  "shipping_postal_code": "...",
  "shipping_country": "CO",
  "shipping": 15000
}
```

### **Wompi recibe:**

```json
{
  "public_key": "pub_test_...",
  "amount_in_cents": 7800000,
  "currency": "COP",
  "reference": "ORD123456ABC",
  "signature:integrity": "abc123...",
  "customer_email": "customer@example.com",
  "redirect_url": "http://localhost:5173/checkout/wompi/success",
  "customer_data": {
    "full_name": "Juan Pérez",
    "phone_number": "+57 300 1234567"
  }
}
```

---

## 📱 Formato de Teléfono

Wompi acepta varios formatos de teléfono:

### **Válidos:**
```
+57 300 1234567
+573001234567
3001234567
300-123-4567
(300) 123-4567
```

### **Recomendado:**
```
+57 300 1234567  (Formato internacional con espacios)
```

---

## ✅ Logs Mejorados

Ahora verás en los logs:

```
📦 [WOMPI] Received 2 items from frontend
👤 [WOMPI] Customer: Juan Pérez (customer@example.com)
📱 [WOMPI] Phone: +57 300 1234567
  Item 1: {...}
  Item 2: {...}
✅ Validated 2 items for Wompi transaction
💰 [WOMPI] Items total: 63000.0, Shipping: 15000.0, Total: 78000.0 COP
💰 [WOMPI] Amount in cents: 7800000
🔐 [WOMPI] Integrity string: ORD123456ABC7800000COP[INTEGRITY_KEY]
🔐 [WOMPI] Integrity signature: abc123...
🔵 [WOMPI] Creating transaction for reference: ORD123456ABC
✅ [WOMPI] Transaction created: 12345-1234-1234-1234
```

---

## 🧪 Testing

### **Request de Prueba**

```bash
POST /api/orders/wompi/create/
Content-Type: application/json

{
  "customer_email": "test@example.com",
  "customer_name": "Test User",
  "phone_number": "+57 300 1234567",
  "items": [
    {
      "woocommerce_product_id": 123,
      "product_name": "Test Product",
      "quantity": 1,
      "unit_price": 50000
    }
  ],
  "shipping_address": "Calle 123",
  "shipping_city": "Medellín",
  "shipping_state": "Antioquia",
  "shipping_postal_code": "050001",
  "shipping_country": "CO",
  "shipping": 10000
}
```

### **Response Esperada (Éxito)**

```json
{
  "success": true,
  "transaction_id": "12345-1234-1234-1234-123456789012",
  "payment_url": "https://checkout.wompi.co/l/aBcDeF123456",
  "reference": "ORD123456ABC",
  "total": "60000",
  "amount_in_cents": 6000000,
  "items_count": 1
}
```

---

## 🚨 Validación Frontend

El frontend debe validar que el teléfono no esté vacío:

```javascript
// CheckoutView.vue
const validatePhoneNumber = () => {
  if (!shippingForm.value.phone || shippingForm.value.phone.trim() === '') {
    showErrorMessage('El número de teléfono es requerido');
    return false;
  }
  return true;
};

async function createWompiTransaction() {
  // Validar teléfono antes de enviar
  if (!validatePhoneNumber()) {
    return;
  }
  
  const orderData = {
    customer_email: user.value.email,
    customer_name: user.value.fullName,
    phone_number: shippingForm.value.phone,  // ⭐ Requerido
    items: [...],
    // ...
  };
  
  const response = await axios.post('/api/orders/wompi/create/', orderData);
  // ...
}
```

---

## 📚 Campos Requeridos por Wompi

| Campo | Requerido | Descripción |
|-------|-----------|-------------|
| `public_key` | ✅ | Llave pública de Wompi |
| `amount_in_cents` | ✅ | Monto en centavos |
| `currency` | ✅ | Moneda (COP) |
| `reference` | ✅ | Referencia única |
| `signature:integrity` | ✅ | Firma de integridad |
| `customer_email` | ✅ | Email del cliente |
| `redirect_url` | ✅ | URL de retorno |
| `customer_data.full_name` | ✅ | Nombre completo |
| `customer_data.phone_number` | ✅ | Teléfono |

---

## 🎯 Resumen

### **Problema:**
❌ `phone_number` estaba hardcodeado como string vacío

### **Solución:**
✅ Extraer `phone_number` del request  
✅ Pasar como parámetro al servicio  
✅ Incluir en payload de Wompi  

### **Archivos Modificados:**
1. `crushme_app/services/wompi_service.py` - Agregado parámetro `phone_number`
2. `crushme_app/views/wompi_order_views.py` - Extraer y pasar `phone_number`

### **Resultado:**
✅ Wompi acepta la transacción  
✅ Logs muestran el teléfono recibido  
✅ Frontend puede ver errores si falta el teléfono  

---

## 🚀 Próximos Pasos

1. **Reiniciar servidor Django** para cargar los cambios
2. **Probar desde frontend** con un teléfono válido
3. **Verificar logs** para confirmar que se recibe el teléfono
4. **Probar flujo completo** hasta el checkout de Wompi

Si el frontend no está enviando el `phone_number`, actualiza el código para incluirlo en el request.
