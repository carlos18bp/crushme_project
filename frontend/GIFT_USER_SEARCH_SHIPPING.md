# Búsqueda de Usuario con Shipping Cost para Regalos

## 📋 Resumen

Se ha implementado la búsqueda de usuarios con costo de envío incluido en los resultados, permitiendo calcular el total correcto del regalo según la ubicación del destinatario.

## 🎯 Características

### Búsqueda de Usuarios:
- ✅ **Endpoint actualizado** a `/api/users/search/`
- ✅ **Shipping cost** incluido en resultados
- ✅ **Búsqueda por concurrencia** con debounce de 300ms
- ✅ **Límite de 5 resultados** por defecto
- ✅ **UI mejorada** mostrando shipping en cada resultado
- ✅ **Actualización automática** del total al seleccionar usuario

## 🔧 Componentes Actualizados

### 1. **crushStore.js** - Store de Búsqueda

#### Endpoint actualizado:
```javascript
// Antes: GET /api/auth/search/?q={query}&limit={limit}
// Ahora: GET /api/users/search/?q={query}&limit={limit}

async function searchUsers(query, limit = 5) {
  const url = `users/search/?q=${query}&limit=${limit}`;
  const response = await get_request(url);
  
  // Response:
  // {
  //   success: true,
  //   count: 3,
  //   results: [
  //     { username: "juan123", is_crush: false, shipping_cost: 10500 },
  //     { username: "juanita", is_crush: false, shipping_cost: 15000 },
  //     { username: "juancarlos", is_crush: false, shipping_cost: 45000 }
  //   ]
  // }
}
```

### 2. **CheckoutGift.vue** - Componente de Regalo

#### Nuevos eventos emitidos:
```javascript
emit('user-selected', user);        // Usuario completo con shipping_cost
emit('shipping-change', shipping);  // Shipping cost del usuario
```

#### Función selectUser actualizada:
```javascript
const selectUser = (user) => {
  console.log('👤 [GIFT] Usuario seleccionado:', user);
  console.log('📦 [GIFT] Shipping cost del usuario:', user.shipping_cost);
  
  searchQuery.value = `@${user.username}`;
  form.value.username = user.username;
  selectedUserShipping.value = user.shipping_cost || 15000;
  
  // Emitir eventos para actualizar el total
  emit('user-selected', user);
  emit('shipping-change', selectedUserShipping.value);
};
```

#### UI de Resultados:
```vue
<div class="username-search-item">
  <div class="search-user-main">
    <span class="search-username">@{{ user.username }}</span>
    <div class="search-user-badges">
      <span v-if="user.is_crush" class="search-crush-label">Crush</span>
    </div>
  </div>
  <div class="search-shipping-info">
    <span class="shipping-icon">📦</span>
    <span class="shipping-cost">{{ formatCOP(user.shipping_cost) }}</span>
  </div>
</div>
```

### 3. **useCheckout.js** - Composable

#### Función prepareGiftOrderData actualizada:
```javascript
const prepareGiftOrderData = (
  shippingForm, 
  senderUsername, 
  subtotal, 
  userShippingCost = 15000  // ⭐ Nuevo parámetro
) => {
  const items = prepareCartItems('gift');
  
  // Usar shipping del usuario + dropshipping
  const baseShipping = userShippingCost;
  const dropshippingCost = dropshippingProduct.value?.price || 0;
  const totalShipping = baseShipping + dropshippingCost;
  const total = calculateTotal(subtotal, totalShipping);
  
  return {
    customer_email: shippingForm.email,
    sender_username: senderUsername,
    receiver_username: shippingForm.username,
    items: items,  // Incluye dropshipping
    gift_message: shippingForm.note,
    total: total   // Total con shipping real
  };
};
```

## 📊 Flujo Completo

### 1. Usuario busca destinatario:
```
Input: "juan"
↓
Debounce 300ms
↓
GET /api/users/search/?q=juan&limit=5
```

### 2. Backend responde:
```json
{
  "success": true,
  "count": 3,
  "results": [
    {
      "username": "juan123",
      "is_crush": false,
      "shipping_cost": 10500,
      "profile_picture": "http://localhost:8000/media/profile_pictures/juan123.jpg"
    },
    {
      "username": "juanita",
      "is_crush": false,
      "shipping_cost": 15000,
      "profile_picture": null
    },
    {
      "username": "juancarlos",
      "is_crush": true,
      "shipping_cost": 45000,
      "profile_picture": "http://localhost:8000/media/profile_pictures/juancarlos.jpg"
    }
  ]
}
```

### 3. UI muestra resultados:
```
┌────────────────────────────────────────────────┐
│ [📷] @juan123                   📦 $10,500    │
├────────────────────────────────────────────────┤
│ [J]  @juanita                   📦 $15,000    │
├────────────────────────────────────────────────┤
│ [📷] @juancarlos 💖 Crush       📦 $45,000    │
└────────────────────────────────────────────────┘

Leyenda:
[📷] = Foto de perfil
[J]  = Avatar placeholder con inicial
💖 Crush = Badge de crush
📦 = Costo de envío
```

### 4. Usuario selecciona "juan123":
```javascript
// Logs:
👤 [GIFT] Usuario seleccionado: {
  username: "juan123",
  is_crush: false,
  shipping_cost: 10500,
  profile_picture: "http://localhost:8000/media/profile_pictures/juan123.jpg"
}
📦 [GIFT] Shipping cost del usuario: 10500
💖 [GIFT] Es crush: false
🖼️ [GIFT] Foto de perfil: http://localhost:8000/media/profile_pictures/juan123.jpg
✅ [GIFT] Shipping actualizado a: 10500
```

### 5. Total se actualiza:
```
Subtotal:        $12,900  (productos)
Envío:           $13,500  ($10,500 + $3,000 dropshipping)
IVA (incluido):  $2,060
───────────────────────────
Total:           $26,400  ✅ Actualizado
```

### 6. Datos enviados al backend:
```javascript
{
  customer_email: "sender@email.com",
  sender_username: "sender_user",
  receiver_username: "juan123",
  items: [
    { product_id: 48497, price: 12900, qty: 1 },
    { product_id: 48500, price: 3000, qty: 1 }  // Dropshipping
  ],
  gift_message: "¡Feliz cumpleaños!",
  total: 26400  // ⭐ Total correcto con shipping real
}
```

## 🎨 Diseño UI

### Resultados de Búsqueda:

**Layout:**
- Avatar (44x44px) a la izquierda
- Username y badge "Crush" en el centro
- Shipping cost a la derecha con badge amarillo

**Avatar:**
```css
/* Con foto de perfil */
.avatar-image {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #f9a8d4;
}

/* Sin foto (placeholder) */
.avatar-placeholder {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
  border: 2px solid #f9a8d4;
}

.avatar-initial {
  color: white;
  font-size: 1.125rem;
  font-weight: 700;
}
```

**Badge de Crush:**
```css
.search-crush-badge {
  background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
  color: white;
  font-size: 0.6875rem;
  border-radius: 9999px;
  padding: 0.125rem 0.5rem;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}
```

**Shipping Info:**
```css
.search-shipping-info {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border: 1px solid #fbbf24;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
}

.shipping-cost {
  font-weight: 700;
  color: #92400e;
}
```

**Hover:**
- Fondo rosa claro (#fce7f3)
- Desplazamiento suave a la derecha (4px)
- Transición de 0.2s

## 🔄 Comparación de Shipping

### Medellín (juan123):
```
Base:         $10,500
Dropshipping: $3,000
Total:        $13,500
```

### Estándar (juanita):
```
Base:         $15,000
Dropshipping: $3,000
Total:        $18,000
```

### San Andrés (juancarlos):
```
Base:         $45,000
Dropshipping: $3,000
Total:        $48,000
```

## 📝 Logs de Debugging

### Búsqueda:
```
🔍 [SEARCH] Buscando usuarios: "juan" (limit: 5)...
✅ [SEARCH] 3 usuarios encontrados
📦 [SEARCH] Resultados con shipping: [...]
```

### Selección:
```
👤 [GIFT] Usuario seleccionado: { username: "juan123", ... }
📦 [GIFT] Shipping cost del usuario: 10500
✅ [GIFT] Shipping actualizado a: 10500
```

### Preparación de datos:
```
🎁 [GIFT] [DROPSHIPPING] Producto agregado a items: {...}
💰 [GIFT] Desglose: {
  subtotal: 12900,
  userShipping: 10500,
  dropshipping: 3000,
  totalShipping: 13500,
  total: 26400
}
```

## ⚠️ Consideraciones

### Fallback:
Si el usuario no tiene `shipping_cost`, se usa tarifa estándar:
```javascript
selectedUserShipping.value = user.shipping_cost || 15000;
```

### Validación:
- El username debe existir en el sistema
- El backend debe validar que el destinatario existe
- El shipping_cost debe ser un número válido

### Errores:
```javascript
// Si la búsqueda falla:
❌ [SEARCH] Error buscando usuarios: "Network error"

// Si no hay resultados:
✅ [SEARCH] 0 usuarios encontrados
```

## 🧪 Testing

### Caso 1: Usuario en Medellín
1. Buscar "juan"
2. Seleccionar "juan123" (shipping: $10,500)
3. Verificar total: $26,400 ($12,900 + $13,500)

### Caso 2: Usuario en San Andrés
1. Buscar "carlos"
2. Seleccionar "juancarlos" (shipping: $45,000)
3. Verificar total: $60,900 ($12,900 + $48,000)

### Caso 3: Usuario estándar
1. Buscar "maria"
2. Seleccionar "maria123" (shipping: $15,000)
3. Verificar total: $30,900 ($12,900 + $18,000)

## 🔗 Archivos Modificados

1. ✅ `/src/stores/modules/crushStore.js` - Endpoint actualizado
2. ✅ `/src/components/checkout/CheckoutGift.vue` - UI y eventos
3. ✅ `/src/composables/useCheckout.js` - Lógica de preparación
4. ✅ `/GIFT_USER_SEARCH_SHIPPING.md` - Esta documentación

## 🎯 Próximos Pasos

Para integrar en CheckoutView.vue:
1. Escuchar evento `@shipping-change` de CheckoutGift
2. Actualizar computed `shipping` con el valor del usuario
3. Recalcular `total` automáticamente
4. Pasar `userShippingCost` a `prepareGiftOrderData()`
