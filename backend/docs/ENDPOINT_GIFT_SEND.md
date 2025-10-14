# 📚 ENDPOINT: Enviar Regalos Entre Usuarios

## 🎯 **Visión General**
Este endpoint permite enviar regalos entre usuarios verificando que el destinatario tenga información completa de envío registrada en el sistema.

## 🔗 **Endpoint**
```
POST /api/orders/gifts/send/
```

## 🔐 **Permisos**
- `AllowAny` - Accesible públicamente

---

## 📥 **Request Body**

```json
{
  "customer_email": "sender@example.com",     // Opcional - Email del remitente
  "sender_username": "sender_user",           // Opcional - Username del remitente
  "receiver_username": "receiver_user",       // Requerido - Username del destinatario
  "items": [                                  // Requerido - Productos del regalo
    {
      "woocommerce_product_id": 1234,         // ID del producto en WooCommerce
      "product_name": "Producto de Regalo",   // Nombre del producto
      "quantity": 1,                          // Cantidad
      "unit_price": 25.99,                    // Precio unitario
      "variation_id": 5679                    // Opcional - Para variaciones
    }
  ],
  "gift_message": "¡Feliz cumpleaños! ❤️"    // Opcional - Mensaje personalizado
}
```

### **Campos Requeridos:**
- ✅ `receiver_username` - Username del usuario que recibe el regalo
- ✅ `items` - Array con al menos 1 producto

### **Campos Opcionales:**
- ✅ `customer_email` - Email del remitente
- ✅ `sender_username` - Username del remitente
- ✅ `gift_message` - Mensaje personalizado para el regalo

---

## 🔍 **Validaciones**

### **1. Verificación del Usuario Destinatario**
- Busca el usuario por `receiver_username`
- Verifica que exista en el sistema

### **2. Verificación de Información de Envío**
El sistema verifica que el destinatario tenga registrada información completa de envío:

**Campos requeridos en `UserAddress`:**
- `address_line_1` - Dirección principal
- `city` - Ciudad
- `state` - Estado/Departamento
- `zip_code` - Código postal
- `country` - País

**Campos opcionales pero útiles:**
- `guest_phone` - Teléfono (se busca en UserAddress o User model)

### **3. Validación de Productos**
- Al menos 1 producto en el array `items`
- Cada producto debe tener: `woocommerce_product_id`, `product_name`, `quantity`, `unit_price`

---

## 📤 **Respuestas**

### **✅ Éxito - Usuario tiene datos de envío completos**
```json
{
  "success": true,
  "message": "Gift order created successfully for receiver_user",
  "paypal_order_id": "5O190127TN364715T",
  "total": "25.99",
  "receiver_info": {
    "username": "receiver_user",
    "email": "receiver@example.com",
    "name": "Receiver Full Name"
  }
}
```

### **❌ Error - Usuario no encontrado**
```json
{
  "error": "User with username \"receiver_user\" not found"
}
```
*Status: 404 Not Found*

### **❌ Error - Datos de envío incompletos**
```json
{
  "error": "User does not have complete shipping information for receiving gifts",
  "missing_fields": ["address_line_1", "city"],
  "user_info": {
    "username": "receiver_user",
    "email": "receiver@example.com",
    "has_shipping_address": false
  }
}
```
*Status: 400 Bad Request*

### **❌ Error - Datos de productos inválidos**
```json
{
  "error": "Invalid item format. Each item must have: woocommerce_product_id, product_name, quantity, unit_price"
}
```
*Status: 400 Bad Request*

---

## 🔄 **Flujo del Proceso**

1. **📥 Recibe Request** → Validar datos básicos
2. **👤 Buscar Usuario** → Verificar que `receiver_username` existe
3. **📦 Verificar Envío** → `_get_user_shipping_info()` valida datos completos
4. **❌ Si datos incompletos** → Retorna error con campos faltantes
5. **✅ Si datos completos** → Crear orden PayPal con datos del destinatario
6. **💳 Crear Orden PayPal** → Usa información de envío del destinatario
7. **📤 Retornar Response** → `paypal_order_id` para proceder con pago

---

## 🎁 **Características Especiales**

### **📬 Auto-verificación de Envío**
- Busca dirección de envío por defecto primero (`is_default_shipping=True`)
- Si no encuentra, busca cualquier dirección del usuario
- Valida que todos los campos requeridos estén completos

### **📱 Información de Contacto**
- Prioriza `guest_phone` de la dirección de envío
- Si no hay teléfono en dirección, busca en el modelo User

### **🎀 Mensajes Personalizados**
- El `gift_message` se incluye en las notas de la orden
- Aparece tanto en la orden local como en WooCommerce

---

## 🔒 **Seguridad**

- ✅ **Validación estricta** de datos requeridos
- ✅ **Verificación de existencia** del usuario destinatario
- ✅ **Campos opcionales** no bloquean el proceso
- ✅ **Mensajes de error claros** para debugging

---

## 💡 **Ejemplo de Uso**

```javascript
// Frontend - Enviar regalo
const giftData = {
  receiver_username: "amiga_secreta",
  customer_email: "yo@ejemplo.com",
  gift_message: "¡Para la mejor amiga del mundo! 🎁",
  items: [
    {
      woocommerce_product_id: 1234,
      product_name: "Chocolate Especial",
      quantity: 1,
      unit_price: 15.99
    }
  ]
};

fetch('/api/orders/gifts/send/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(giftData)
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    // Proceder con PayPal usando data.paypal_order_id
    console.log("Regalo enviado a:", data.receiver_info.name);
  } else {
    // Mostrar error al usuario
    console.error("Error:", data.error);
  }
});
```

---

## 🚨 **Casos de Error Comunes**

| Error | Causa | Solución |
|-------|-------|----------|
| `receiver_username` faltante | No se envió el username | Incluir `receiver_username` en request |
| Usuario no encontrado | Username incorrecto | Verificar username del destinatario |
| Datos envío incompletos | Usuario sin dirección registrada | Usuario debe completar perfil de envío |
| Items inválidos | Formato de productos incorrecto | Verificar estructura de `items` array |
| Error 500 | Problemas internos del servidor | Verificar logs del servidor y configuración |

## ✅ **Estado Actual**
- **✅ Implementado** - Endpoint funcional y probado
- **✅ Documentado** - Documentación completa disponible
- **✅ Seguro** - Validaciones estrictas de datos
- **🔧 Optimizado** - Código refactorizado y limpio

---

## 📋 **Notas de Implementación**

- **Función `_get_user_shipping_info()`** - Valida completamente los datos de envío
- **Función `create_paypal_order_for_gift()`** - Wrapper para usar función existente
- **Herencia del flujo PayPal** - Usa el mismo proceso que órdenes normales
- **Campos opcionales** - No bloquean el envío si están ausentes

---

## 🎯 **Próximas Mejoras**

- [ ] **Notificaciones push** al destinatario cuando recibe regalo
- [ ] **Historial de regalos** enviados/recibidos por usuario
- [ ] **Límite de regalos** por período de tiempo
- [ ] **Sistema de wishlist** integrado con regalos
