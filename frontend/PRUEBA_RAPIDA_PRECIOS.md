# 🚀 Prueba Rápida - Sistema de Precios

## ✅ Lista de Verificación (5 minutos)

### Paso 1: Iniciar el servidor
```bash
npm run dev
```

### Paso 2: Navegar a productos
```
http://localhost:5173/es/products
```

### Paso 3: Abrir DevTools
1. Presiona `F12` o `Ctrl+Shift+I`
2. Ve a la pestaña **Console**

### Paso 4: Verificar logs
Deberías ver en la consola:
```
✅ Catálogo inicializado
✅ Productos de juguetes cargados: 9
[priceHelper] ✅ Precio extraído: $21,900
[priceHelper] ✅ Precio extraído: $18,500
[priceHelper] ✅ Precio extraído: $32,900
...
```

---

## 🔍 Inspección Visual

### 1. Ver Precios en Cards
Los precios en las tarjetas de productos deben mostrar el formato:
```
$21,900
$18,500
$32,900
```

✅ **Correcto:** Precio con separador de miles y símbolo `$`  
❌ **Incorrecto:** `15000` sin formato o precio muy bajo

---

### 2. Verificar en Consola (Manual)

Pega este código en la consola del navegador:

```javascript
// Obtener el primer producto
const { useProductStore } = await import('@/stores/modules/productStore.js')
const { getProductPrice, getFormattedProductPrice } = await import('@/utils/priceHelper.js')

const productStore = useProductStore()
const producto = productStore.wooProducts[0]

console.log('========== PRODUCTO TEST ==========')
console.log('ID:', producto.id)
console.log('Nombre:', producto.name)
console.log('Tipo:', producto.type)
console.log('')
console.log('Short Description (HTML):')
console.log(producto.short_description)
console.log('')
console.log('❌ Precio Mayorista (NO USAR):', producto.price)
console.log('✅ Precio Extraído (CORRECTO):', getProductPrice(producto))
console.log('✅ Precio Formateado:', getFormattedProductPrice(producto))
console.log('===================================')
```

**Resultado esperado:**
```
========== PRODUCTO TEST ==========
ID: 123
Nombre: Vibrador Premium
Tipo: simple

Short Description (HTML):
<h5><span style="color: #333333;"><strong>Precio sugerido </strong></span><strong><span style="color: #18badb;">$21,900</span></strong></h5>

❌ Precio Mayorista (NO USAR): 15000
✅ Precio Extraído (CORRECTO): 21900
✅ Precio Formateado: $21,900
===================================
```

---

## 🛒 Prueba de Carrito

### 1. Agregar producto al carrito
1. Haz clic en **"Buy now"** o **"Add to cart"** en cualquier producto
2. Ve a la consola

**Logs esperados:**
```
🔵 [ProductCard] handleBuyNow clicked for product: 123
🔵 [ProductCard] handleBuyNow result: { success: true }
```

### 2. Verificar precio en carrito

Pega en la consola:
```javascript
const { useCartStore } = await import('@/stores/modules/cartStore.js')
const cartStore = useCartStore()

console.log('========== ITEMS EN CARRITO ==========')
cartStore.items.forEach((item, index) => {
  console.log(`${index + 1}. ${item.name}`)
  console.log(`   - Precio: $${item.price.toLocaleString('es-CO')}`)
  console.log(`   - Cantidad: ${item.quantity}`)
  console.log(`   - Subtotal: $${(item.price * item.quantity).toLocaleString('es-CO')}`)
  console.log('')
})
console.log(`TOTAL: $${cartStore.totalPrice.toLocaleString('es-CO')}`)
console.log('======================================')
```

**Resultado esperado:**
```
========== ITEMS EN CARRITO ==========
1. Vibrador Premium
   - Precio: $21,900  ← ✅ Precio correcto
   - Cantidad: 1
   - Subtotal: $21,900

TOTAL: $21,900
======================================
```

---

## 🐛 Problemas Comunes

### Problema 1: Precio aparece como `$0`
**Causa:** El `short_description` está vacío o no tiene el formato esperado

**Solución:**
```javascript
// Ver el HTML completo
const producto = productStore.wooProducts[0]
console.log(producto.short_description)

// Verificar si hay precio
if (!producto.short_description || !producto.short_description.includes('$')) {
  console.error('❌ Este producto NO tiene precio en short_description')
  console.log('Revisa el producto en WooCommerce admin')
}
```

---

### Problema 2: Warning en consola
```
[priceHelper] ⚠️ Usando precio mayorista (price) como fallback
```

**Causa:** El producto no tiene `short_description` con precio

**Solución:** 
1. Ve al admin de WooCommerce
2. Edita el producto
3. Agrega el precio en "Short description" con formato:
   ```html
   <h5>Precio sugerido <span>$21,900</span></h5>
   ```

---

### Problema 3: Precio muy bajo (parece mayorista)
**Ejemplo:** Se muestra `$15,000` cuando debería ser `$21,900`

**Diagnóstico:**
```javascript
const producto = productStore.wooProducts[0]
const extractedPrice = getProductPrice(producto)

if (extractedPrice === parseFloat(producto.price)) {
  console.error('❌ PROBLEMA: Está usando el precio mayorista')
  console.log('Short description:', producto.short_description)
}
```

---

## ✅ Checklist Final

Marca cada item cuando lo verifiques:

- [ ] Los precios tienen formato `$XX,XXX` (con comas)
- [ ] Los precios son diferentes al campo `product.price` mayorista
- [ ] Al agregar al carrito, el precio es correcto
- [ ] No hay warnings en consola sobre precios mayoristas
- [ ] Logs de `[priceHelper] ✅` aparecen correctamente
- [ ] Los precios coinciden con WooCommerce admin

---

## 🎯 Resultado Esperado

Si todo funciona correctamente:

✅ **Precios correctos** en todas las tarjetas de productos  
✅ **Formato COP** con separadores de miles (`$21,900`)  
✅ **Logs positivos** en consola (`✅ Precio extraído`)  
✅ **Carrito correcto** con precios reales  
✅ **Sin warnings** de precio mayorista  

---

## 📞 Si Algo Falla

1. **Copia el resultado** del test de consola (código arriba)
2. **Toma captura** de los precios en pantalla
3. **Guarda los logs** de la consola
4. **Anota el ID** del producto problemático

---

## 🎉 ¡Listo!

Si todo está ✅, los precios en la lista de productos ahora funcionan correctamente.

**Próximo paso:** Actualizar `ProductDetailView.vue` (página de detalle del producto)

