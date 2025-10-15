# 📚 ENDPOINTS PRIVADOS DEL USUARIO

## 🎯 **Visión General**
Documentación completa de los endpoints privados que permiten consultar el historial personal de compras, regalos enviados, regalos recibidos y estadísticas del usuario autenticado.

## 🔐 **Requisitos Comunes**
- **Autenticación requerida** - Todos los endpoints requieren token JWT válido
- **Información privada** - Cada usuario solo puede ver sus propios datos
- **Paginación incluida** - Para manejar grandes cantidades de datos

---

## 🎁 **ENDPOINT: Lista de Regalos Recibidos**

### **📍 URL**
```
GET /api/orders/gifts/?type=received
```

### **🔐 Permisos**
- `IsAuthenticated` - Requiere autenticación

### **📥 Parámetros de Consulta**
| Parámetro | Tipo | Descripción | Valor por Defecto | Requerido |
|-----------|------|-------------|-------------------|----------|
| `type` | string | Tipo de filtro: `received` | `sent` | ❌ |
| `page` | integer | Número de página | `1` | ❌ |
| `page_size` | integer | Items por página | `10` | ❌ |

### **📤 Respuesta Exitosa**
```json
{
  "orders": [
    {
      "id": 123,
      "order_number": "ORD1699123456ABC123",
      "status": "delivered",
      "total": "25.99",
      "is_gift": true,
      "sender_username": "amiga_secreta",
      "receiver_username": "yo_mismo",
      "gift_message": "¡Feliz cumpleaños! 🎂",
      "woocommerce_order_id": 56789,
      "gift_summary": {
        "type": "gift_order",
        "sender": "amiga_secreta",
        "receiver": "yo_mismo",
        "message": "¡Feliz cumpleaños! 🎂",
        "privacy_note": "Shipping details hidden for privacy"
      },
      "items": [
        {
          "id": 1,
          "woocommerce_product_id": 1234,
          "woocommerce_variation_id": null,
          "quantity": 1,
          "unit_price": "25.99",
          "subtotal": "25.99",
          "product_name": "Chocolate Especial Premium",
          "product_description": "Delicioso chocolate con nueces",
          "image_url": "https://tienda.com/wp-content/uploads/chocolate.jpg",
          "categories": ["Alimentos", "Dulces"],
          "stock_status": "instock"
        }
      ],
      "shipping_address": "Dirección de envío privada (regalo)",
      "shipping_city": null,
      "shipping_state": null,
      "shipping_postal_code": null,
      "shipping_country": null,
      "phone_number": null,
      "created_at": "2025-10-14T18:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "page_size": 10,
    "total_orders": 3,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  },
  "gift_summary": {
    "type": "received",
    "total_gifts": 3,
    "sent_gifts": 2,
    "received_gifts": 3
  },
  "user_stats": {
    "total_purchases": 15,
    "sent_gifts_count": 2,
    "received_gifts_count": 3
  }
}
```

---

## 📤 **ENDPOINT: Lista de Regalos Enviados**

### **📍 URL**
```
GET /api/orders/gifts/?type=sent
```

### **🔐 Permisos**
- `IsAuthenticated` - Requiere autenticación

### **📥 Parámetros de Consulta**
| Parámetro | Tipo | Descripción | Valor por Defecto | Requerido |
|-----------|------|-------------|-------------------|----------|
| `type` | string | Tipo de filtro: `sent` | `sent` | ❌ |
| `page` | integer | Número de página | `1` | ❌ |
| `page_size` | integer | Items por página | `10` | ❌ |

### **📤 Respuesta Exitosa**
```json
{
  "orders": [
    {
      "id": 124,
      "order_number": "ORD1699123457DEF456",
      "status": "shipped",
      "total": "15.50",
      "is_gift": true,
      "sender_username": "yo_mismo",
      "receiver_username": "amiga_secreta",
      "gift_message": "¡Para la mejor amiga! 💕",
      "woocommerce_order_id": 56790,
      "gift_summary": {
        "type": "gift_order",
        "sender": "yo_mismo",
        "receiver": "amiga_secreta",
        "message": "¡Para la mejor amiga! 💕",
        "privacy_note": "Shipping details hidden for privacy"
      },
      "items": [
        {
          "id": 2,
          "woocommerce_product_id": 5678,
          "woocommerce_variation_id": null,
          "quantity": 1,
          "unit_price": "15.50",
          "subtotal": "15.50",
          "product_name": "Libro Especial de Cocina",
          "product_description": "Recetas tradicionales colombianas",
          "image_url": "https://tienda.com/wp-content/uploads/libro-cocina.jpg",
          "categories": ["Libros", "Cocina"],
          "stock_status": "instock"
        }
      ],
      "shipping_address": "Dirección de envío privada (regalo)",
      "shipping_city": null,
      "shipping_state": null,
      "shipping_postal_code": null,
      "shipping_country": null,
      "phone_number": null,
      "created_at": "2025-10-13T14:20:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "page_size": 10,
    "total_orders": 2,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  },
  "gift_summary": {
    "type": "sent",
    "total_gifts": 2,
    "sent_gifts": 2,
    "received_gifts": 3
  },
  "user_stats": {
    "total_purchases": 15,
    "sent_gifts_count": 2,
    "received_gifts_count": 3
  }
}
```

---

## 🛒 **ENDPOINT: Historial de Compras del Usuario**

### **📍 URL**
```
GET /api/orders/history/
```

### **🔐 Permisos**
- `IsAuthenticated` - Requiere autenticación

### **📥 Parámetros de Consulta**
| Parámetro | Tipo | Descripción | Valor por Defecto | Requerido |
|-----------|------|-------------|-------------------|----------|
| `include_gifts` | boolean | Incluir órdenes de regalo | `true` | ❌ |
| `page` | integer | Número de página | `1` | ❌ |
| `page_size` | integer | Items por página | `10` | ❌ |

### **📤 Respuesta Exitosa**
```json
{
  "purchases": [
    {
      "id": 125,
      "order_number": "ORD1699123458GHI789",
      "status": "delivered",
      "total": "45.00",
      "is_gift": false,
      "woocommerce_order_id": 56791,
      "items": [
        {
          "id": 3,
          "woocommerce_product_id": 9012,
          "woocommerce_variation_id": null,
          "quantity": 2,
          "unit_price": "22.50",
          "subtotal": "45.00",
          "product_name": "Producto Regular Premium",
          "product_description": "Producto de alta calidad",
          "image_url": "https://tienda.com/wp-content/uploads/producto.jpg",
          "categories": ["Electrónicos", "Premium"],
          "stock_status": "instock"
        }
      ],
      "shipping_address": "Avenida Principal #10-20",
      "shipping_city": "Cali",
      "shipping_state": "Valle del Cauca",
      "shipping_postal_code": "760001",
      "shipping_country": "CO",
      "phone_number": "+57 300 1234567",
      "created_at": "2025-10-12T10:15:00Z"
    },
    {
      "id": 123,
      "order_number": "ORD1699123456ABC123",
      "status": "delivered",
      "total": "25.99",
      "is_gift": true,
      "sender_username": "amiga_secreta",
      "receiver_username": "yo_mismo",
      "gift_message": "¡Feliz cumpleaños! 🎂",
      "woocommerce_order_id": 56789,
      "gift_summary": {
        "type": "gift_order",
        "sender": "amiga_secreta",
        "receiver": "yo_mismo",
        "message": "¡Feliz cumpleaños! 🎂",
        "privacy_note": "Shipping details hidden for privacy"
      },
      "items": [
        {
          "id": 1,
          "woocommerce_product_id": 1234,
          "woocommerce_variation_id": null,
          "quantity": 1,
          "unit_price": "25.99",
          "subtotal": "25.99",
          "product_name": "Chocolate Especial Premium",
          "product_description": "Delicioso chocolate con nueces",
          "image_url": "https://tienda.com/wp-content/uploads/chocolate.jpg",
          "categories": ["Alimentos", "Dulces"],
          "stock_status": "instock"
        }
      ],
      "shipping_address": "Dirección de envío privada (regalo)",
      "shipping_city": null,
      "shipping_state": null,
      "shipping_postal_code": null,
      "shipping_country": null,
      "phone_number": null,
      "created_at": "2025-10-14T18:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "page_size": 10,
    "total_purchases": 15,
    "total_pages": 2,
    "has_next": true,
    "has_previous": false
  },
  "user_stats": {
    "total_purchases": 15,
    "regular_purchases": 12,
    "gift_purchases": 3,
    "sent_gifts_count": 2,
    "received_gifts_count": 3,
    "total_spent": "450.75"
  }
}
```

---

## 📊 **ENDPOINT: Estadísticas del Usuario (Contador de Regalos)**

### **📍 URL**
```
GET /api/orders/gifts/?type=all&page_size=1
```

### **🔐 Permisos**
- `IsAuthenticated` - Requiere autenticación

### **📥 Parámetros de Consulta**
| Parámetro | Tipo | Descripción | Valor por Defecto | Requerido |
|-----------|------|-------------|-------------------|----------|
| `type` | string | Tipo: `all` para estadísticas generales | `sent` | ❌ |
| `page_size` | integer | Usar `1` para solo estadísticas | `10` | ❌ |

### **📤 Respuesta Exitosa**
```json
{
  "orders": [],
  "pagination": {
    "current_page": 1,
    "page_size": 1,
    "total_orders": 5,
    "total_pages": 5,
    "has_next": true,
    "has_previous": false
  },
  "gift_summary": {
    "type": "all",
    "total_gifts": 5,
    "sent_gifts": 2,
    "received_gifts": 3
  },
  "user_stats": {
    "total_purchases": 15,
    "sent_gifts_count": 2,
    "received_gifts_count": 3
  }
}
```

---

## 💡 **Ejemplos de Uso en Frontend**

### **1. Obtener Regalos Recibidos**
```javascript
const fetchReceivedGifts = async (page = 1, pageSize = 10) => {
  try {
    const response = await fetch(`/api/orders/gifts/?type=received&page=${page}&page_size=${pageSize}`, {
      headers: {
        'Authorization': `Bearer ${userToken}`
      }
    });
    const data = await response.json();

    console.log(`Recibí ${data.gift_summary.received_gifts} regalos`);
    console.log(`Total gastado en compras: $${data.user_stats.total_spent}`);

    return data;
  } catch (error) {
    console.error('Error fetching received gifts:', error);
  }
};
```

### **2. Obtener Regalos Enviados**
```javascript
const fetchSentGifts = async (page = 1, pageSize = 10) => {
  try {
    const response = await fetch(`/api/orders/gifts/?type=sent&page=${page}&page_size=${pageSize}`, {
      headers: {
        'Authorization': `Bearer ${userToken}`
      }
    });
    const data = await response.json();

    console.log(`Envié ${data.gift_summary.sent_gifts} regalos`);
    return data;
  } catch (error) {
    console.error('Error fetching sent gifts:', error);
  }
};
```

### **3. Obtener Historial Completo de Compras**
```javascript
const fetchPurchaseHistory = async (includeGifts = true, page = 1, pageSize = 10) => {
  try {
    const response = await fetch(
      `/api/orders/history/?include_gifts=${includeGifts}&page=${page}&page_size=${pageSize}`,
      {
        headers: {
          'Authorization': `Bearer ${userToken}`
        }
      }
    );
    const data = await response.json();

    console.log(`Total de compras: ${data.user_stats.total_purchases}`);
    console.log(`Compras regulares: ${data.user_stats.regular_purchases}`);
    console.log(`Compras de regalo: ${data.user_stats.gift_purchases}`);

    return data;
  } catch (error) {
    console.error('Error fetching purchase history:', error);
  }
};
```

### **4. Obtener Solo Estadísticas**
```javascript
const fetchUserStats = async () => {
  try {
    const response = await fetch('/api/orders/gifts/?type=all&page_size=1', {
      headers: {
        'Authorization': `Bearer ${userToken}`
      }
    });
    const data = await response.json();

    return {
      sentGifts: data.gift_summary.sent_gifts,
      receivedGifts: data.gift_summary.received_gifts,
      totalPurchases: data.user_stats.total_purchases,
      totalSpent: data.user_stats.total_spent
    };
  } catch (error) {
    console.error('Error fetching user stats:', error);
  }
};
```

---

## 🚨 **Casos de Error**

### **401 Unauthorized**
```json
{
  "detail": "Authentication credentials were not provided."
}
```
*Causa:* Usuario no autenticado o token inválido

### **403 Forbidden**
```json
{
  "detail": "You do not have permission to perform this action."
}
```
*Causa:* Problemas de permisos (aunque normalmente no ocurre con endpoints privados)

### **500 Internal Server Error**
```json
{
  "error": "Internal server error",
  "details": "Error message"
}
```
*Causa:* Problemas internos del servidor

---

## 🔒 **Características de Seguridad**

### **Autenticación JWT**
- ✅ **Token requerido** en header `Authorization: Bearer <token>`
- ✅ **Validación automática** del token
- ✅ **Usuario identificado** automáticamente

### **Privacidad de Datos**
- ✅ **Solo datos propios** - No se pueden ver datos de otros usuarios
- ✅ **Filtrado automático** por usuario autenticado
- ✅ **Información sensible** protegida

### **Validaciones Implementadas**
- ✅ **Usuario existe** y está activo
- ✅ **Token válido** y no expirado
- ✅ **Permisos correctos** para la operación

---

## 📈 **Estadísticas Incluidas**

### **En Todos los Endpoints**
- ✅ **Total de compras** del usuario
- ✅ **Compras regulares** vs **compras de regalo**
- ✅ **Contador de regalos enviados**
- ✅ **Contador de regalos recibidos**

### **En Endpoint de Historial**
- ✅ **Monto total gastado**
- ✅ **Promedio por compra**
- ✅ **Fechas de primera y última compra**

---

## 🎯 **URLs Relacionadas**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/orders/gifts/?type=received` | Regalos recibidos por el usuario |
| `GET` | `/api/orders/gifts/?type=sent` | Regalos enviados por el usuario |
| `GET` | `/api/orders/history/` | Historial completo de compras |
| `GET` | `/api/orders/gifts/?type=all&page_size=1` | Estadísticas rápidas del usuario |

---

## 💫 **Casos de Uso del Frontend**

### **Dashboard del Usuario**
```javascript
// Cargar estadísticas generales
const loadUserDashboard = async () => {
  const stats = await fetchUserStats();
  updateDashboard({
    totalCompras: stats.totalPurchases,
    totalGastado: stats.totalSpent,
    regalosEnviados: stats.sentGifts,
    regalosRecibidos: stats.receivedGifts
  });
};
```

### **Lista de Regalos Recibidos**
```javascript
// Mostrar regalos recibidos con mensajes
const showReceivedGifts = async () => {
  const data = await fetchReceivedGifts();
  data.orders.forEach(gift => {
    displayGift({
      from: gift.sender_username,
      message: gift.gift_message,
      product: gift.items[0].product_name,
      date: gift.created_at
    });
  });
};
```

### **Perfil de Usuario**
```javascript
// Estadísticas en perfil
const updateProfileStats = async () => {
  const stats = await fetchUserStats();
  document.getElementById('profile-stats').innerHTML = `
    <div>Total Compras: ${stats.totalPurchases}</div>
    <div>Total Gastado: $${stats.totalSpent}</div>
    <div>Regalos Enviados: ${stats.sentGifts}</div>
    <div>Regalos Recibidos: ${stats.receivedGifts}</div>
  `;
};
```

---

## 🎁 **Información de Regalos y Envío Condicional**

### **Campos de Regalo Incluidos**
Cada orden incluye automáticamente información de regalo:

```json
{
  "is_gift": true,                    // Marca que es regalo
  "sender_username": "quien_envio",   // Username del remitente
  "receiver_username": "quien_recibe", // Username del destinatario
  "gift_message": "Mensaje personalizado" // Mensaje del regalo
}
```

### **Información de Envío Condicional** ⭐ **NUEVO**
- **Órdenes normales** (`is_gift: false`): Incluyen información completa de envío
- **Órdenes de regalo** (`is_gift: true`): Ocultan detalles privados de envío por privacidad

**Para órdenes de regalo:**
```json
{
  "shipping_address": "Dirección de envío privada (regalo)",
  "shipping_city": null,
  "shipping_state": null,
  "shipping_postal_code": null,
  "shipping_country": null,
  "phone_number": null,
  "gift_summary": {
    "type": "gift_order",
    "sender": "usuario_remitente",
    "receiver": "usuario_destinatario",
    "message": "Mensaje personalizado",
    "privacy_note": "Shipping details hidden for privacy"
  }
}
```

### **Productos Enriquecidos** ⭐ **NUEVO**
Cada producto incluye información actualizada de WooCommerce:

```json
{
  "items": [
    {
      "woocommerce_product_id": 1234,
      "woocommerce_variation_id": null,
      "product_name": "Producto Actual Premium",
      "product_description": "Descripción actualizada",
      "image_url": "https://tienda.com/wp-content/uploads/imagen.jpg",
      "categories": ["Categoría 1", "Categoría 2"],
      "stock_status": "instock",
      "unit_price": "25.99",
      "subtotal": "25.99"
    }
  ]
}
```

---

## ✅ **Estado de Implementación**

### **✅ Completamente Implementado**
- **Endpoints funcionales** con autenticación JWT
- **Respuestas completas** con toda la información necesaria
- **Paginación eficiente** para grandes cantidades de datos
- **Estadísticas automáticas** incluidas en respuestas
- **Documentación detallada** disponible

### **🔧 Próximas Mejoras**
- [ ] **Filtros avanzados** por fecha, monto, producto específico
- [ ] **Búsqueda de texto** en mensajes de regalo
- [ ] **Exportación** de historial a PDF/Excel
- [ ] **Gráficos estadísticos** del comportamiento de compra

---

## 🎊 **¡Endpoints Privados Completamente Operativos!**

**Los usuarios ahora pueden:**
1. **Ver todos sus regalos recibidos** con mensajes personalizados
2. **Revisar regalos que han enviado** a otros usuarios
3. **Consultar historial completo** de compras personales
4. **Obtener estadísticas detalladas** de su actividad

**¿Necesitas algún ajuste específico o funcionalidad adicional?**
