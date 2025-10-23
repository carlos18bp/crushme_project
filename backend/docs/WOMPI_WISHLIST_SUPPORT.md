# Wompi - Soporte de Wishlist y Gifts

## ✅ Confirmación

Los endpoints de Wompi **SÍ manejan gifts y wishlists** completamente, igual que PayPal.

---

## 🎁 Manejo de Gifts

### **Campos Soportados**
```json
{
  "is_gift": true,
  "sender_username": "juan",
  "receiver_username": "maria",
  "gift_message": "¡Feliz cumpleaños!"
}
```

### **Flujo**
1. **`/wompi/create/`**: Guarda gift data en cache (1 hora)
2. Usuario paga en Wompi
3. **`/wompi/confirm/`**: Recupera gift data del cache y crea orden con datos de gift

---

## 📋 Manejo de Wishlist

### **Campos Soportados**
```json
{
  "is_from_wishlist": true,
  "wishlist_id": 123,
  "wishlist_name": "Mi Lista de Deseos"
}
```

### **Flujo Completo**

#### **1. Create Transaction (`/wompi/create/`)**
```python
# Guarda wishlist data en cache junto con gift data
gift_data = {
    'is_gift': request.data.get('is_gift', False),
    'sender_username': request.data.get('sender_username'),
    'receiver_username': request.data.get('receiver_username'),
    'gift_message': request.data.get('gift_message', ''),
    # Wishlist data
    'is_from_wishlist': request.data.get('is_from_wishlist', False),
    'wishlist_id': request.data.get('wishlist_id'),
    'wishlist_name': request.data.get('wishlist_name')
}

cache.set(f'gift_data_{transaction_id}', gift_data, 3600)
```

#### **2. Confirm Payment (`/wompi/confirm/`)**
Llama a `process_order_after_payment()` que:

```python
# STEP 1: Recupera gift y wishlist data del cache
gift_data = cache.get(f'gift_data_{transaction_id}', {})

# STEP 2: Crea orden con datos de gift
order = Order.objects.create(
    is_gift=gift_data.get('is_gift'),
    sender_username=gift_data.get('sender_username'),
    receiver_username=gift_data.get('receiver_username'),
    gift_message=gift_data.get('gift_message'),
    ...
)

# STEP 3: Remueve items comprados de la wishlist
is_from_wishlist = gift_data.get('is_from_wishlist', False)
wishlist_id = gift_data.get('wishlist_id')

if is_from_wishlist and wishlist_id:
    _remove_purchased_items_from_wishlist(wishlist_id, items, receiver_username)
    # Items comprados se remueven automáticamente
    # Si se compraron todos → wishlist queda vacía
```

---

## 🔄 Comparación con PayPal

| Característica | PayPal | Wompi |
|---------------|--------|-------|
| **Gifts** | ✅ Soportado | ✅ Soportado |
| **Wishlist** | ✅ Soportado | ✅ Soportado |
| **Remove Items** | ✅ Automático | ✅ Automático |
| **Cache Data** | ✅ 1 hora | ✅ 1 hora |
| **Flujo Común** | ✅ `process_order_after_payment()` | ✅ `process_order_after_payment()` |

**Ambas pasarelas usan exactamente el mismo flujo después de capturar el pago.**

---

## 📝 Request Body Completo

### **Ejemplo: Comprar Wishlist como Gift con Wompi**

```json
{
  "customer_email": "juan@example.com",
  "customer_name": "Juan Pérez",
  "items": [
    {
      "woocommerce_product_id": 1234,
      "product_name": "Producto 1",
      "quantity": 2,
      "unit_price": 50000,
      "variation_id": 5678
    }
  ],
  "shipping_address": "Carrera 80 #50-25",
  "shipping_city": "Medellín",
  "shipping_state": "Antioquia",
  "shipping_postal_code": "050031",
  "shipping_country": "CO",
  "phone_number": "+57 300 1234567",
  "shipping": 10500,
  
  "is_gift": true,
  "sender_username": "juan",
  "receiver_username": "maria",
  "gift_message": "¡Espero que te guste!",
  
  "is_from_wishlist": true,
  "wishlist_id": 123,
  "wishlist_name": "Lista de María"
}
```

---

## 🎯 Casos de Uso

### **1. Compra Normal (No Gift, No Wishlist)**
```json
{
  "is_gift": false,
  "is_from_wishlist": false
}
```
✅ Crea orden normal

### **2. Gift (No Wishlist)**
```json
{
  "is_gift": true,
  "sender_username": "juan",
  "receiver_username": "maria",
  "gift_message": "Para ti",
  "is_from_wishlist": false
}
```
✅ Crea orden como gift  
✅ Actualiza historial de gifts del usuario

### **3. Wishlist (Siempre es Gift)**
```json
{
  "is_gift": true,
  "sender_username": "juan",
  "receiver_username": "maria",
  "gift_message": "De tu wishlist",
  "is_from_wishlist": true,
  "wishlist_id": 123,
  "wishlist_name": "Lista de María"
}
```
✅ Crea orden como gift  
✅ Actualiza historial de gifts  
✅ **Remueve items comprados de la wishlist**  
✅ Si se compraron todos los items → wishlist queda vacía

---

## 🔧 Implementación Backend

### **Archivos Modificados**

#### **1. `wompi_order_views.py`**
```python
# create_wompi_transaction() - Líneas 135-149
# Guarda gift y wishlist data en cache

gift_data = {
    'is_gift': request.data.get('is_gift', False),
    'sender_username': request.data.get('sender_username'),
    'receiver_username': request.data.get('receiver_username'),
    'gift_message': request.data.get('gift_message', ''),
    # Wishlist data
    'is_from_wishlist': request.data.get('is_from_wishlist', False),
    'wishlist_id': request.data.get('wishlist_id'),
    'wishlist_name': request.data.get('wishlist_name')
}

cache.set(f'gift_data_{transaction_id}', gift_data, 3600)
```

#### **2. `order_helpers.py`**
```python
# process_order_after_payment() - Líneas 112-124
# Remueve items de wishlist después de crear orden

is_from_wishlist = gift_data.get('is_from_wishlist', False)
wishlist_id = gift_data.get('wishlist_id')

if is_from_wishlist and wishlist_id:
    from .gift_views import _remove_purchased_items_from_wishlist
    receiver_username = gift_data.get('receiver_username')
    _remove_purchased_items_from_wishlist(wishlist_id, items, receiver_username)
    logger.info(f"✅ Removed purchased items from wishlist {wishlist_id}")
```

---

## 📱 Frontend Integration

### **Detectar si es Wishlist**
```javascript
// En CheckoutView.vue
const isFromWishlist = computed(() => {
  return route.query.wishlistId !== undefined;
});

const wishlistData = computed(() => {
  if (!isFromWishlist.value) return null;
  
  return {
    is_from_wishlist: true,
    wishlist_id: parseInt(route.query.wishlistId),
    wishlist_name: route.query.wishlistName || 'Wishlist'
  };
});
```

### **Incluir en Request**
```javascript
async function createWompiTransaction() {
  const orderData = {
    // ... campos normales ...
    
    // Gift data
    is_gift: giftMode.value,
    sender_username: user.value.username,
    receiver_username: selectedGiftUser.value?.username,
    gift_message: giftMessage.value,
    
    // Wishlist data (si aplica)
    ...(wishlistData.value || {})
  };
  
  const response = await axios.post('/api/orders/wompi/create/', orderData);
  // ...
}
```

---

## ✅ Testing

### **Test 1: Gift Normal (Sin Wishlist)**
```bash
POST /api/orders/wompi/create/
{
  "items": [...],
  "is_gift": true,
  "sender_username": "juan",
  "receiver_username": "maria",
  "gift_message": "Para ti",
  "is_from_wishlist": false
}
```
**Resultado:**
- ✅ Orden creada como gift
- ✅ Historial actualizado
- ❌ No afecta wishlist

### **Test 2: Comprar Wishlist Completa**
```bash
POST /api/orders/wompi/create/
{
  "items": [
    {"woocommerce_product_id": 123, "quantity": 1, ...},
    {"woocommerce_product_id": 456, "quantity": 2, ...}
  ],
  "is_gift": true,
  "sender_username": "juan",
  "receiver_username": "maria",
  "is_from_wishlist": true,
  "wishlist_id": 10,
  "wishlist_name": "Lista de María"
}
```
**Resultado:**
- ✅ Orden creada como gift
- ✅ Historial actualizado
- ✅ Items 123 y 456 removidos de wishlist #10
- ✅ Si eran los únicos items → wishlist queda vacía

### **Test 3: Comprar Algunos Items de Wishlist**
```bash
POST /api/orders/wompi/create/
{
  "items": [
    {"woocommerce_product_id": 123, "quantity": 1, ...}
  ],
  "is_from_wishlist": true,
  "wishlist_id": 10
}
```
**Resultado:**
- ✅ Solo item 123 removido
- ✅ Otros items permanecen en wishlist
- ✅ Wishlist sigue activa

---

## 🚨 Notas Importantes

### **1. Wishlist Siempre es Gift**
Si `is_from_wishlist: true`, entonces `is_gift` debe ser `true` también.

### **2. Cache Expira en 1 Hora**
Si el usuario no completa el pago en 1 hora, los datos se pierden. Esto es intencional para seguridad.

### **3. No Falla si Wishlist Update Falla**
Si hay un error al remover items de la wishlist, la orden se crea de todas formas. Solo se loguea el error.

### **4. Matching de Items**
- Con `variation_id`: Match por `product_id` + `variation_id`
- Sin `variation_id`: Match solo por `product_id`

---

## 📚 Documentación Relacionada

- **Flujo completo**: `docs/PAYMENT_FLOW_ARCHITECTURE.md`
- **Frontend integration**: `docs/WOMPI_FRONTEND_INTEGRATION.md`
- **Gift views**: `crushme_app/views/gift_views.py`
- **Order helpers**: `crushme_app/views/order_helpers.py`

---

## 🎉 Resumen

✅ **Wompi soporta gifts** - Igual que PayPal  
✅ **Wompi soporta wishlists** - Igual que PayPal  
✅ **Remueve items automáticamente** - Sin llamadas adicionales  
✅ **Mismo flujo común** - `process_order_after_payment()`  
✅ **Cache seguro** - 1 hora de expiración  

**Conclusión:** Wompi tiene paridad completa con PayPal en cuanto a gifts y wishlists.
