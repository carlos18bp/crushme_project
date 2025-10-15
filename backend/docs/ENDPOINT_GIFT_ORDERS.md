# 📚 ENDPOINT: Órdenes de Regalo

## 🎯 **Visión General**
Este endpoint permite obtener las órdenes marcadas como regalos para el usuario autenticado, tanto las que envió como las que recibió.

## 🔗 **Endpoint**
```
GET /api/orders/gifts/
```

## 🔐 **Permisos**
- `IsAuthenticated` - Requiere autenticación

---

## 📥 **Query Parameters**

| Parámetro | Tipo | Descripción | Valor por Defecto |
|-----------|------|-------------|-------------------|
| `type` | string | Tipo de órdenes: `sent`, `received`, `all` | `sent` |
| `page` | integer | Número de página para paginación | `1` |
| `page_size` | integer | Cantidad de resultados por página | `10` |

### **Valores de `type`:**
- **`sent`** - Órdenes donde el usuario es el remitente (regalos enviados)
- **`received`** - Órdenes donde el usuario es el destinatario (regalos recibidos)
- **`all`** - Ambas categorías combinadas

---

## 📤 **Respuesta Exitosa**

```json
{
  "orders": [
    {
      "id": 123,
      "order_number": "ORD1699123456ABC123",
      "status": "processing",
      "total": "25.99",
      "is_gift": true,
      "sender_username": "usuario_remitente",
      "receiver_username": "usuario_destinatario",
      "gift_message": "¡Feliz cumpleaños! 🎂",
      "email": "destinatario@ejemplo.com",
      "name": "Usuario Destinatario",
      "items": [
        {
          "id": 1,
          "woocommerce_product_id": 1234,
          "quantity": 1,
          "unit_price": "25.99",
          "product_name": "Producto de Regalo",
          "subtotal": "25.99"
        }
      ],
      "shipping_address": "Carrera 80 #50-25 Apto 301",
      "shipping_city": "Medellín",
      "shipping_state": "Antioquia",
      "shipping_postal_code": "050031",
      "shipping_country": "CO",
      "phone_number": "+57 300 1234567",
      "notes": "",
      "created_at": "2025-10-14T18:30:00Z",
      "updated_at": "2025-10-14T18:30:00Z"
      // ... otros campos de OrderDetailSerializer
    }
  ],
  "pagination": {
    "current_page": 1,
    "page_size": 10,
    "total_orders": 5,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  },
  "gift_summary": {
    "type": "sent",
    "total_gifts": 3,
    "sent_gifts": 3,
    "received_gifts": 2
  }
}
```

---

## 🔍 **Funcionalidades**

### **Filtrado Inteligente**
- ✅ **Por tipo**: `sent`, `received`, o `all`
- ✅ **Paginación**: Navegación eficiente para grandes cantidades de datos
- ✅ **Ordenamiento**: Más recientes primero (`-created_at`)

### **Estadísticas Incluidas**
- ✅ **Conteo total** de regalos según el tipo seleccionado
- ✅ **Resumen global** de regalos enviados y recibidos

### **Información Completa**
- ✅ **Datos completos** de cada orden usando `OrderDetailSerializer`
- ✅ **Campos de regalo** incluidos automáticamente
- ✅ **Información de items** detallada

---

## 💡 **Ejemplos de Uso**

### **1. Regalos Enviados**
```javascript
// Obtener regalos que el usuario envió
fetch('/api/orders/gifts/?type=sent')
  .then(response => response.json())
  .then(data => {
    console.log(`Envió ${data.gift_summary.sent_gifts} regalos`);
    data.orders.forEach(order => {
      console.log(`Regalo para ${order.receiver_username}: ${order.gift_message}`);
    });
  });
```

### **2. Regalos Recibidos**
```javascript
// Obtener regalos que el usuario recibió
fetch('/api/orders/gifts/?type=received')
  .then(response => response.json())
  .then(data => {
    console.log(`Recibió ${data.gift_summary.received_gifts} regalos`);
    // Mostrar mensajes de agradecimiento, etc.
  });
```

### **3. Todos los Regalos**
```javascript
// Obtener todos los regalos (enviados y recibidos)
fetch('/api/orders/gifts/?type=all')
  .then(response => response.json())
  .then(data => {
    console.log(`Total de ${data.gift_summary.total_gifts} regalos`);
  });
```

### **4. Paginación**
```javascript
// Obtener página 2 con 5 resultados por página
fetch('/api/orders/gifts/?page=2&page_size=5')
  .then(response => response.json())
  .then(data => {
    console.log(`Página ${data.pagination.current_page} de ${data.pagination.total_pages}`);
  });
```

---

## 🔒 **Seguridad**

- ✅ **Autenticación requerida** - Solo usuarios autenticados
- ✅ **Datos privados** - Solo muestra órdenes del usuario autenticado
- ✅ **Filtrado automático** - No puede ver órdenes de otros usuarios

---

## 🎁 **Campos de Regalo Incluidos**

Cada orden de regalo incluye automáticamente:

```json
{
  "is_gift": true,                    // Marca que es regalo
  "sender_username": "quien_envio",   // Username del remitente
  "receiver_username": "quien_recibe", // Username del destinatario
  "gift_message": "Mensaje personalizado" // Mensaje del regalo
}
```

---

## 📊 **Casos de Uso del Frontend**

### **Dashboard de Usuario**
```javascript
// En componente de dashboard
useEffect(() => {
  fetchGiftOrders();
}, []);

const fetchGiftOrders = async () => {
  try {
    const response = await fetch('/api/orders/gifts/?type=all');
    const data = await response.json();

    setGiftStats({
      sent: data.gift_summary.sent_gifts,
      received: data.gift_summary.received_gifts,
      recent: data.orders.slice(0, 3) // Últimos 3 regalos
    });
  } catch (error) {
    console.error('Error fetching gift orders:', error);
  }
};
```

### **Lista de Regalos**
```javascript
// En componente de lista de regalos
const [giftOrders, setGiftOrders] = useState([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
  loadGiftOrders();
}, [currentType, currentPage]);

const loadGiftOrders = async () => {
  setLoading(true);
  try {
    const response = await fetch(
      `/api/orders/gifts/?type=${currentType}&page=${currentPage}&page_size=10`
    );
    const data = await response.json();
    setGiftOrders(data);
  } catch (error) {
    console.error('Error:', error);
  } finally {
    setLoading(false);
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
*Causa:* Usuario no autenticado

### **500 Internal Server Error**
```json
{
  "error": "Internal server error",
  "details": "Error message"
}
```
*Causa:* Problemas internos del servidor

---

## 🔗 **URLs Relacionadas**

- **📤 Enviar Regalo:** `POST /api/orders/gifts/send/`
- **📋 Órdenes del Usuario:** `GET /api/orders/`
- **🔍 Detalle de Orden:** `GET /api/orders/{order_id}/`
- **📊 Estadísticas:** `GET /api/orders/admin/statistics/`

---

## ✅ **Estado de Implementación**

- **✅ Endpoint funcional** - Probado y operativo
- **✅ Documentación completa** - Disponible y actualizada
- **✅ Seguridad implementada** - Validaciones y permisos correctos
- **✅ Integración completa** - Funciona con el resto del sistema

---

## 🎯 **Próximas Mejoras**

- [ ] **Filtros avanzados** - Por fecha, monto, estado
- [ ] **Búsqueda** - Buscar por mensaje de regalo o username
- [ ] **Notificaciones** - Alertas cuando recibe regalos
- [ ] **Estadísticas detalladas** - Gráficos y métricas avanzadas
