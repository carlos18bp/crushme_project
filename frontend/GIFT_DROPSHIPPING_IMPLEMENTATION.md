# Implementación de Dropshipping para Regalos

## 📋 Resumen

Se ha implementado la misma lógica de dropshipping (recargo oculto) para las órdenes de regalo, manteniendo la consistencia con las compras regulares.

## 🎯 Características

### Para Regalos:
- ✅ **Producto dropshipping** se agrega automáticamente a los items
- ✅ **Shipping estimado** se muestra visualmente (incluye recargo)
- ✅ **Backend recibe** lista de items completa (con dropshipping)
- ✅ **Shipping real** se calcula en backend según ubicación del destinatario
- ✅ **Total correcto** se envía para validación

## 🔧 Componentes Actualizados

### 1. **CheckoutGift.vue**

Se agregó sección informativa de shipping:

```vue
<div v-if="shippingCost" class="gift-shipping-info">
  <div class="shipping-info-header">
    <span class="shipping-icon">📦</span>
    <span class="shipping-label">Costo de envío al destinatario</span>
  </div>
  <div class="shipping-cost">
    {{ formatCOP(shippingCost) }}
  </div>
  <p class="shipping-note">
    El envío será calculado según la ubicación del destinatario
  </p>
</div>
```

**Props:**
- `modelValue`: Formulario de regalo
- `shippingCost`: Costo de envío estimado (incluye dropshipping)

### 2. **useCheckout.js** (Composable)

Se agregaron funciones específicas:

#### `prepareCartItems(type)`
```javascript
const prepareCartItems = (type = 'regular') => {
  const items = cartStore.items.map(item => ({...}));
  
  // Agregar dropshipping
  if (dropshippingProduct.value) {
    items.push({
      woocommerce_product_id: dropshippingProduct.value.id,
      product_name: dropshippingProduct.value.name,
      quantity: 1,
      unit_price: parseFloat(dropshippingProduct.value.price)
    });
  }
  
  return items;
};
```

#### `prepareGiftOrderData(shippingForm, senderUsername, subtotal)`
```javascript
const prepareGiftOrderData = (shippingForm, senderUsername, subtotal) => {
  const items = prepareCartItems('gift'); // ⭐ Incluye dropshipping
  
  // Shipping estimado (tarifa estándar + dropshipping)
  const shipping = calculateShipping(''); // 15000 + dropshipping
  const total = calculateTotal(subtotal, shipping);
  
  return {
    customer_email: shippingForm.email,
    sender_username: senderUsername,
    receiver_username: shippingForm.username.replace('@', ''),
    items: items, // ⭐ Incluye dropshipping como item
    gift_message: shippingForm.note || '',
    total: total
  };
};
```

## 📊 Flujo de Datos para Regalos

### 1. Cliente ve:
```
Subtotal:        $12,900  (productos)
Envío estimado:  $18,000  ($15,000 base + $3,000 dropshipping)
IVA (incluido):  $2,060
───────────────────────────
Total:           $30,900
```

### 2. Frontend envía al backend:
```javascript
{
  customer_email: "sender@email.com",
  sender_username: "sender_user",
  receiver_username: "receiver_user",
  items: [
    { product_id: 48497, name: "Jabón", price: 12900, qty: 1 },
    { product_id: 48500, name: "DROPSHIPPING", price: 3000, qty: 1 }  // ⭐ Recargo
  ],
  gift_message: "¡Feliz cumpleaños!",
  total: 30900  // ⭐ Total con shipping estimado
}
```

### 3. Backend debe:
1. **Recibir los items** (incluye dropshipping)
2. **Calcular shipping real** según ubicación del destinatario
3. **Crear orden** con todos los items
4. **Validar total** (puede variar si shipping real es diferente)

## 🔄 Diferencias: Regular vs Regalo

### Compra Regular:
```javascript
// Shipping conocido (según ciudad seleccionada)
shipping: 10500  // Medellín
items: [producto, dropshipping]
```

### Regalo:
```javascript
// Shipping estimado (se calcula en backend)
// NO se envía campo "shipping" explícito
items: [producto, dropshipping]  // ⭐ Dropshipping incluido en items
total: subtotal + shipping_estimado
```

## 💡 Ventajas

1. **Consistencia**: Misma lógica para regular y regalo
2. **Transparencia**: Cliente ve costo estimado de envío
3. **Flexibilidad**: Backend calcula shipping real según destinatario
4. **Trazabilidad**: Dropshipping aparece en la orden
5. **Validación**: Total enviado para verificación

## 🎨 UI/UX

### Sección de Shipping (Regalo)
- **Diseño**: Card con gradiente rosa
- **Icono**: 📦 Emoji de paquete
- **Información**: 
  - Label: "Costo de envío al destinatario"
  - Monto: Formato COP con tamaño grande
  - Nota: "El envío será calculado según la ubicación del destinatario"

### Estilos:
```css
.gift-shipping-info {
  background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
  border-radius: 0.75rem;
  border: 1px solid #f9a8d4;
  padding: 1rem;
}

.shipping-cost {
  font-size: 1.5rem;
  font-weight: 700;
  color: #be185d;
}
```

## 🧪 Testing

### Caso de Prueba: Regalo con Dropshipping

1. **Agregar producto** al carrito ($12,900)
2. **Ir a checkout** y seleccionar "For Gift"
3. **Ingresar email** del remitente
4. **Buscar usuario** destinatario
5. **Verificar en consola:**
   ```
   🎁 [GIFT] [DROPSHIPPING] Producto agregado a items: {
     id: 48500,
     name: "DROPSHIPPING",
     price: "3000"
   }
   
   💰 [GIFT] Desglose: {
     subtotal: 12900,
     estimatedShipping: 15000,
     dropshipping: 3000,
     total: 30900
   }
   ```

6. **Verificar UI:**
   - Muestra "Costo de envío: $18,000"
   - Total: $30,900

7. **Completar pago** y verificar en backend:
   - Items incluyen producto + dropshipping
   - Total es correcto

## ⚠️ Notas Importantes

1. **Shipping estimado**: Para regalos se usa tarifa estándar ($15,000) + dropshipping
2. **Shipping real**: El backend debe calcular según ubicación del destinatario
3. **Diferencia de total**: Si shipping real difiere del estimado, el backend debe ajustar
4. **Validación**: Backend debe verificar que items incluyan el dropshipping
5. **Logs**: Todos los pasos están logueados con prefijo 🎁 [GIFT]

## 📝 Checklist Backend

- [ ] Recibir items con dropshipping incluido
- [ ] Obtener ubicación del destinatario
- [ ] Calcular shipping real según ubicación
- [ ] Crear orden con todos los items
- [ ] Ajustar total si shipping real difiere del estimado
- [ ] Notificar al destinatario
- [ ] Retornar confirmación al remitente

## 🔗 Archivos Relacionados

- `/src/components/checkout/CheckoutGift.vue` - Componente de formulario de regalo
- `/src/composables/useCheckout.js` - Lógica compartida de checkout
- `/src/views/cart/CheckoutView.vue` - Vista principal de checkout
- `DROPSHIPPING_IMPLEMENTATION.md` - Documentación de dropshipping regular
