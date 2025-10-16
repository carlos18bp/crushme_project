# 📚 USUARIO: Historial de Compras y Sistema de Regalos

## 🎯 **Visión General**
Este sistema permite rastrear el historial completo de compras y regalos de cada usuario, incluyendo estadísticas detalladas y seguimiento de regalos enviados y recibidos.

## 🔗 **Nuevos Campos en Modelo User**

### **Campos de Historial y Regalos**
```python
# En modelo User - Campos añadidos:
purchase_history = models.ManyToManyField('Order')        # Historial de compras
received_gifts = models.ManyToManyField('Order')          # Regalos recibidos
sent_gifts_count = models.PositiveIntegerField(default=0) # Contador de regalos enviados
```

### **Campo en Modelo Order**
```python
# En modelo Order - Campo añadido:
woocommerce_order_id = models.IntegerField(null=True)     # ID de orden en WooCommerce
```

---

## 🔄 **Flujo de Actualización Automática**

### **Creación de Orden** (Después del pago exitoso de PayPal)
1. ✅ **Crear orden local** con `woocommerce_order_id = None`
2. ✅ **Actualizar historial del usuario** automáticamente
3. ✅ **Enviar a WooCommerce en background**
4. ✅ **Actualizar `woocommerce_order_id`** cuando WooCommerce responda

### **Actualización de Historial** (Función `_update_user_history_and_gifts`)
```python
def _update_user_history_and_gifts(order, receiver_username=None):
    # 1. Añadir orden al historial de compras del usuario
    order.user.purchase_history.add(order)

    # 2. Si es regalo, añadir al historial del destinatario
    if order.is_gift and receiver_username:
        recipient_user.received_gifts.add(order)

        # 3. Incrementar contador de regalos enviados del remitente
        if order.sender_username:
            sender_user.sent_gifts_count += 1
            sender_user.save()
```

---

## 🎁 **Campos de Regalo en Órdenes**

### **Campos que se Guardan Automáticamente**
```json
{
  "is_gift": true,                    // Marca como regalo
  "sender_username": "quien_envio",   // Username del remitente
  "receiver_username": "quien_recibe", // Username del destinatario
  "gift_message": "Mensaje personalizado", // Mensaje del regalo
  "woocommerce_order_id": 12345       // ID de orden en WooCommerce (se actualiza después)
}
```

---

## 📊 **Endpoints para Historial de Usuario**

### **1. Órdenes de Regalo** ⭐
```
GET /api/orders/gifts/?type=sent|received|all&page=1&page_size=10
```

**Características:**
- ✅ **Filtrado inteligente**: `sent`, `received`, `all`
- ✅ **Estadísticas incluidas**: Conteo de regalos enviados/recibidos
- ✅ **Paginación completa**: Navegación eficiente

**Respuesta:**
```json
{
  "orders": [/* órdenes detalladas */],
  "pagination": {/* info de paginación */},
  "gift_summary": {
    "sent_gifts": 3,
    "received_gifts": 2,
    "total_gifts": 5
  },
  "user_stats": {
    "total_purchases": 15,
    "sent_gifts_count": 3,
    "received_gifts_count": 2
  }
}
```

### **2. Historial Completo de Compras** ⭐
```
GET /api/orders/history/?include_gifts=true&page=1&page_size=10
```

**Características:**
- ✅ **Historial completo** de todas las compras del usuario
- ✅ **Filtro opcional** para incluir/excluir regalos
- ✅ **Estadísticas detalladas** incluyendo monto total gastado

**Respuesta:**
```json
{
  "purchases": [/* órdenes detalladas */],
  "pagination": {/* info de paginación */},
  "user_stats": {
    "total_purchases": 15,
    "regular_purchases": 12,
    "gift_purchases": 3,
    "sent_gifts_count": 3,
    "received_gifts_count": 2,
    "total_spent": "450.75"
  }
}
```

---

## 🔍 **Consultas en Base de Datos**

### **Órdenes de Regalo**
```sql
-- Todas las órdenes de regalo
SELECT * FROM crushme_app_order WHERE is_gift = True;

-- Regalos enviados por un usuario
SELECT * FROM crushme_app_order WHERE sender_username = 'usuario_remitente';

-- Regalos recibidos por un usuario
SELECT * FROM crushme_app_order WHERE receiver_username = 'usuario_destinatario';
```

### **Historial de Usuario**
```sql
-- Compras de un usuario
SELECT * FROM crushme_app_user_purchase_history WHERE user_id = 1;

-- Regalos recibidos por un usuario
SELECT * FROM crushme_app_user_received_gifts WHERE user_id = 1;

-- Contador de regalos enviados
SELECT sent_gifts_count FROM crushme_app_user WHERE id = 1;
```

---

## 💡 **Ejemplos de Uso Frontend**

### **Dashboard de Usuario**
```javascript
// Obtener estadísticas del usuario
const fetchUserStats = async () => {
  const [historyRes, giftsRes] = await Promise.all([
    fetch('/api/orders/history/?page_size=1'),
    fetch('/api/orders/gifts/?type=all&page_size=1')
  ]);

  const historyData = await historyRes.json();
  const giftsData = await giftsRes.json();

  setUserStats({
    totalPurchases: historyData.user_stats.total_purchases,
    totalSpent: historyData.user_stats.total_spent,
    sentGifts: giftsData.user_stats.sent_gifts_count,
    receivedGifts: giftsData.user_stats.received_gifts_count
  });
};
```

### **Lista de Compras**
```javascript
// Obtener historial de compras con filtros
const fetchPurchases = async (includeGifts = true, page = 1) => {
  const response = await fetch(
    `/api/orders/history/?include_gifts=${includeGifts}&page=${page}&page_size=10`
  );
  return await response.json();
};
```

### **Lista de Regalos**
```javascript
// Obtener regalos con diferentes filtros
const fetchGifts = async (type = 'all', page = 1) => {
  const response = await fetch(
    `/api/orders/gifts/?type=${type}&page=${page}&page_size=10`
  );
  return await response.json();
};
```

---

## 🔒 **Características de Seguridad**

- ✅ **Autenticación requerida** - Solo usuarios autenticados
- ✅ **Datos privados** - Cada usuario solo ve sus propios datos
- ✅ **Validación estricta** - No se pueden manipular datos de otros usuarios
- ✅ **Transacciones atómicas** - Las actualizaciones son consistentes

---

## 📈 **Estadísticas Disponibles**

### **Estadísticas de Usuario**
- ✅ **Total de compras** realizadas
- ✅ **Compras regulares** vs **compras de regalo**
- ✅ **Monto total gastado**
- ✅ **Regalos enviados** (contador)
- ✅ **Regalos recibidos** (contador)

### **Estadísticas de Regalo**
- ✅ **Total de regalos** enviados/recibidos
- ✅ **Por tipo** (enviados, recibidos, todos)
- ✅ **Con paginación** para grandes cantidades

---

## 🎯 **Estado de Implementación**

### **✅ Completamente Implementado**
- **Modelo User** actualizado con campos de historial y regalos
- **Modelo Order** actualizado con `woocommerce_order_id`
- **Flujo automático** de actualización de historial
- **Endpoints funcionales** para historial y regalos
- **Actualización automática** del `woocommerce_order_id`
- **Documentación completa** disponible

### **🔧 Próximas Mejoras**
- [ ] **Filtros avanzados** por fecha, monto, producto
- [ ] **Búsqueda de texto** en mensajes de regalo
- [ ] **Exportación** de historial a PDF/Excel
- [ ] **Gráficos y métricas** visuales del historial

---

## 🚀 **URLs Disponibles**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/orders/gifts/` | Órdenes de regalo del usuario |
| `GET` | `/api/orders/history/` | Historial completo de compras |
| `POST` | `/api/orders/gifts/send/` | Enviar regalo verificando destinatario |
| `POST` | `/api/orders/paypal/create/` | Crear orden (puede marcarse como regalo) |

---

## 💫 **Beneficios del Sistema**

### **Para Usuarios:**
- ✅ **Historial completo** de todas sus compras
- ✅ **Seguimiento detallado** de regalos enviados y recibidos
- ✅ **Estadísticas personales** de comportamiento de compra
- ✅ **Recordatorios** de regalos especiales con mensajes personalizados

### **Para el Sistema:**
- ✅ **Rastreo completo** de actividad del usuario
- ✅ **Análisis de datos** para mejoras futuras
- ✅ **Integración** con WooCommerce para consistencia
- ✅ **Escalabilidad** para múltiples usuarios

---

## 🎊 **¡Sistema de Historial y Regalos Completamente Operativo!**

**El sistema ahora permite:**
1. **Rastrear todas las compras** de cada usuario
2. **Gestionar regalos** con seguimiento completo
3. **Guardar IDs de WooCommerce** para referencia cruzada
4. **Proporcionar estadísticas** detalladas al usuario
5. **Mantener historial** persistente y accesible

**¿Quieres que añada alguna funcionalidad adicional o ajuste específico?**

