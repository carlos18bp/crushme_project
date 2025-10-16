# Implementación de Producto Dropshipping (Recargo Oculto)

## 📋 Resumen

Se ha implementado la lógica para incluir automáticamente un producto de dropshipping (ID: 48500) en todas las órdenes. Este producto actúa como un recargo que:

- ✅ **Se consulta automáticamente** al cargar el checkout
- ✅ **Se suma al costo de envío visualmente** para el cliente
- ✅ **Se envía como un producto más** en la lista de items al backend
- ✅ **NO se muestra** en la lista de productos del carrito
- ✅ **El shipping real** (sin recargo) se envía en el campo `shipping`

## 🔧 Cambios Implementados

### 1. **Imports y Stores** (líneas 350-368)
```javascript
import { useProductStore } from '@/stores/modules/productStore.js';
const productStore = useProductStore();
```

### 2. **State Management** (líneas 404-407)
```javascript
// ⭐ Producto de dropshipping (recargo oculto)
const DROPSHIPPING_PRODUCT_ID = 48500;
const dropshippingProduct = ref(null);
const isLoadingDropshipping = ref(false);
```

### 3. **Función de Carga** (líneas 487-516)
```javascript
const loadDropshippingProduct = async () => {
  isLoadingDropshipping.value = true;
  
  try {
    console.log(`📦 [DROPSHIPPING] Consultando producto ${DROPSHIPPING_PRODUCT_ID}...`);
    
    const result = await productStore.fetchWooProduct(DROPSHIPPING_PRODUCT_ID);
    
    if (result.success && result.data) {
      dropshippingProduct.value = result.data;
      console.log('✅ [DROPSHIPPING] Producto cargado:', {
        id: result.data.id,
        name: result.data.name,
        price: result.data.price
      });
    } else {
      console.error('❌ [DROPSHIPPING] Error al cargar producto:', result.error);
    }
  } catch (error) {
    console.error('❌ [DROPSHIPPING] Error inesperado:', error);
  } finally {
    isLoadingDropshipping.value = false;
  }
};
```

### 4. **Cálculo de Shipping** (líneas 845-885)

#### Base Shipping (valor real enviado al backend)
```javascript
const baseShipping = computed(() => {
  const ciudad = (shippingForm.value.city || '').toLowerCase().trim();
  
  if (!ciudad) return 15000;
  
  switch (ciudad) {
    case 'medellín':
    case 'medellin':
      return 10500;
    case 'san andrés isla':
    case 'san andres isla':
    // ... más casos
      return 45000;
    default:
      return 15000;
  }
});
```

#### Shipping Mostrado (incluye recargo)
```javascript
const shipping = computed(() => {
  let total = baseShipping.value;
  
  // Agregar recargo de dropshipping si está disponible
  if (dropshippingProduct.value && dropshippingProduct.value.price) {
    const dropshippingPrice = parseFloat(dropshippingProduct.value.price);
    total += dropshippingPrice;
    console.log(`📦 [DROPSHIPPING] Shipping mostrado: ${baseShipping.value} + ${dropshippingPrice} = ${total}`);
  }
  
  return total;
});
```

### 5. **Modificaciones en Funciones de Orden**

#### `createRegularOrder()` (líneas 551-578)
- Agrega el producto dropshipping a los items
- Envía `baseShipping.value` en el campo `shipping`

#### `createGiftOrder()` (líneas 626-651)
- Agrega el producto dropshipping a los items de regalo

#### `captureRegularPayment()` (líneas 800-840)
- Agrega el producto dropshipping a los items de captura
- Envía `baseShipping.value` en el campo `shipping`

#### `captureGiftPayment()` (líneas 702-739)
- Agrega el producto dropshipping a los items de captura de regalo
- Envía `baseShipping.value` en el campo `shipping`

### 6. **Inicialización** (líneas 1159-1161)
```javascript
// ⭐ Cargar producto de dropshipping (recargo)
// Este producto siempre se consulta al inicio
await loadDropshippingProduct();
```

### 7. **UI - Mensaje de Envío** (líneas 113-117)
```html
<p class="city-shipping-info" v-if="shippingForm.city">
  <span>
    📦 Costo de envío: {{ formatCOP(shipping) }}
  </span>
</p>
```

## 🎯 Flujo de Datos

### Para el Cliente (Frontend)
```
Subtotal: $50,000
Shipping: $25,500  ← (baseShipping: $15,000 + dropshipping: $10,500)
Tax: $9,500
Total: $85,000
```

### Para el Backend
```javascript
{
  items: [
    { product_id: 123, name: "Producto A", price: 50000, quantity: 1 },
    { product_id: 48500, name: "Dropshipping", price: 10500, quantity: 1 }  ← Recargo
  ],
  shipping: 15000  ← Costo base real
}
```

## ✅ Ventajas de esta Implementación

1. **Transparencia para el cliente**: Ve el costo total de envío sin saber que incluye un recargo
2. **Flexibilidad**: El recargo se puede cambiar en WooCommerce sin modificar código
3. **Trazabilidad**: El producto dropshipping aparece en la orden de WooCommerce
4. **Separación de conceptos**: El shipping real se mantiene separado del recargo
5. **Logs detallados**: Cada paso del proceso está logueado para debugging

## 🔍 Debugging

Los logs incluyen:
- `📦 [DROPSHIPPING] Consultando producto...`
- `✅ [DROPSHIPPING] Producto cargado`
- `📦 [DROPSHIPPING] Producto agregado a items`
- `📦 [DROPSHIPPING] Shipping mostrado: X + Y = Z`

## ⚠️ Consideraciones

1. **Producto debe existir**: El producto con ID 48500 debe existir en WooCommerce
2. **Precio actualizable**: El precio del recargo se obtiene dinámicamente de WooCommerce
3. **Sin mostrar en UI**: El producto NO aparece en la lista de productos del checkout
4. **Siempre incluido**: Se agrega automáticamente a TODAS las órdenes (regulares y regalos)

## 🧪 Testing

Para probar:
1. Ir al checkout con productos en el carrito
2. Verificar en consola que se carga el producto 48500
3. Seleccionar una ciudad y verificar que el shipping incluye el recargo
4. Completar la orden y verificar en backend que:
   - El producto 48500 está en los items
   - El campo `shipping` tiene el valor base (sin recargo)
