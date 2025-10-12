# 📊 Manejo de Precios en CrushMe

## 🎯 Problema Resuelto

Los productos de WooCommerce vienen con dos campos de precio:
- **`price`**: Precio mayorista (NO usar en frontend)
- **`short_description`**: Contiene el precio sugerido en HTML (usar este)

## 💡 Solución Implementada

Se creó un sistema de utilidades en `/src/utils/priceHelper.js` que:

1. **Extrae automáticamente** el precio del HTML en `short_description`
2. **Formatea el precio** en pesos colombianos (COP) con separadores de miles
3. **Maneja ambos tipos** de productos:
   - `type: "simple"` → Sin variaciones de precio
   - `type: "variable"` → Con variaciones (color, tamaño, etc.)

## 🛠️ Funciones Disponibles

### 1. `extractPriceFromShortDescription(shortDescription)`
Extrae el precio numérico del HTML.

```javascript
const html = '<h5><strong>Precio sugerido <span>$21,900</span></strong></h5>'
const price = extractPriceFromShortDescription(html)
// Resultado: 21900
```

### 2. `getProductPrice(product)`
Obtiene el precio de un producto (simple o variable).

```javascript
const product = { short_description: '...' }
const price = getProductPrice(product)
// Resultado: 21900 (número)
```

### 3. `formatCOP(price, includeSymbol = true)`
Formatea un precio en COP.

```javascript
formatCOP(21900, true)   // "$21,900"
formatCOP(21900, false)  // "21,900"
```

### 4. `getFormattedProductPrice(product)`
Obtiene el precio formateado de un producto (función all-in-one).

```javascript
const product = { short_description: '...' }
const formatted = getFormattedProductPrice(product)
// Resultado: "$21,900"
```

### 5. `isVariableProduct(product)` / `isSimpleProduct(product)`
Verifica el tipo de producto.

```javascript
isVariableProduct(product)  // true/false
isSimpleProduct(product)    // true/false
```

## 📦 Componentes Actualizados

### ProductCard.vue
- ✅ Usa `getFormattedProductPrice()` para mostrar precios
- ✅ Usa `getProductPrice()` para cálculos de carrito
- ✅ Maneja automáticamente productos simples y variables

### ProductsView.vue
- ✅ Usa `getProductPrice()` al agregar productos al carrito

## 🎨 Formato de Precios

Los precios se muestran con el formato colombiano:
- **Con símbolo**: `$21,900`
- **Sin decimales**: Los precios en COP no usan decimales
- **Separador de miles**: Coma (`,`)

## 🔮 Próximos Pasos (Productos Variables)

Para productos con `type: "variable"`, necesitarás:
1. Extraer las variaciones del producto
2. Mostrar selector de opciones (color, talla, etc.)
3. Actualizar el precio según la variación seleccionada
4. Validar disponibilidad de stock por variación

## 📝 Ejemplos de Uso

### En un componente Vue
```vue
<script setup>
import { getFormattedProductPrice } from '@/utils/priceHelper.js'

const product = { 
  short_description: '<h5>Precio <span>$21,900</span></h5>' 
}

// Mostrar precio formateado
const displayPrice = getFormattedProductPrice(product) // "$21,900"
</script>

<template>
  <div class="price">{{ displayPrice }}</div>
</template>
```

### En el carrito
```javascript
import { getProductPrice } from '@/utils/priceHelper.js'

const product = { short_description: '...' }
const numericPrice = getProductPrice(product) // 21900

cartStore.addToCart(product.id, {
  price: numericPrice // Usar número sin formato
})
```

## ⚠️ Importante

- **NO usar** `product.price` directamente (precio mayorista)
- **SIEMPRE usar** las funciones de `priceHelper.js`
- Los precios en el carrito deben ser **numéricos** (sin formato)
- Los precios en la UI deben ser **formateados** (con símbolo y comas)

## 🐛 Debugging

Si un precio no se muestra correctamente:
1. Verifica que `product.short_description` existe
2. Revisa el console.log en `priceHelper.js`
3. Asegúrate que el HTML tenga el formato esperado: `$XX,XXX`

## 🔍 Formato HTML Esperado

```html
<h5>
  <span style="color: #333333;">
    <strong>Precio sugerido </strong>
  </span>
  <strong>
    <span style="color: #18badb;">$21,900</span>
  </strong>
</h5>
```

El regex busca cualquier patrón `$XX,XXX` en el HTML.

