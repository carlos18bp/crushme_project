# 🔍 Prueba - Detalle de Producto (Simple vs Variable)

## 🎯 Objetivo
Verificar que el precio se muestra correctamente en el detalle del producto:
- ✅ **Productos Simples**: Extrae precio de `short_description`
- 🔄 **Productos Variables**: Usa precio base (`product.price`) hasta implementar selector

---

## 🧪 Prueba 1: Producto Simple

### Paso 1: Navegar a un producto simple
```
http://localhost:5173/es/product/[ID-PRODUCTO-SIMPLE]
```

### Paso 2: Abrir DevTools (F12)
Ve a la pestaña **Console**

### Paso 3: Verificar logs
Deberías ver:
```
💰 [ProductDetail] Producto simple - Precio extraído: $21,900
[priceHelper] ✅ Precio extraído: $21,900
```

### Paso 4: Inspeccionar en consola
```javascript
// Pega esto en la consola:
const { useProductStore } = await import('@/stores/modules/productStore.js')
const productStore = useProductStore()
const producto = productStore.wooCurrentProduct

console.log('========== PRODUCTO SIMPLE ==========')
console.log('ID:', producto.id)
console.log('Nombre:', producto.name)
console.log('Tipo:', producto.type)
console.log('')
console.log('❌ Precio Mayorista:', producto.price)
console.log('✅ Precio Mostrado en UI:', document.querySelector('.current-price')?.textContent)
console.log('Short Description:', producto.short_description?.substring(0, 100))
console.log('====================================')
```

**Resultado esperado:**
```
========== PRODUCTO SIMPLE ==========
ID: 123
Nombre: Vibrador Premium
Tipo: simple

❌ Precio Mayorista: 15000
✅ Precio Mostrado en UI: $21,900
Short Description: <h5>Precio sugerido <span>$21,900</span></h5>
====================================
```

### Paso 5: Agregar al carrito
1. Selecciona cantidad
2. Haz clic en "Agregar al carrito"
3. Verifica en la consola:

```javascript
const { useCartStore } = await import('@/stores/modules/cartStore.js')
const cartStore = useCartStore()
const ultimoItem = cartStore.items[cartStore.items.length - 1]

console.log('Producto agregado al carrito:')
console.log('- Nombre:', ultimoItem.name)
console.log('- Precio:', ultimoItem.price)
console.log('- Esperado: 21900')
console.log('- ✅ Correcto:', ultimoItem.price === 21900)
```

---

## 🧪 Prueba 2: Producto Variable

### Paso 1: Navegar a un producto variable
```
http://localhost:5173/es/product/[ID-PRODUCTO-VARIABLE]
```

### Paso 2: Verificar logs
Deberías ver:
```
💰 [ProductDetail] Producto variable - Usando precio base: $20000
```

### Paso 3: Inspeccionar en consola
```javascript
const { useProductStore } = await import('@/stores/modules/productStore.js')
const productStore = useProductStore()
const producto = productStore.wooCurrentProduct

console.log('========== PRODUCTO VARIABLE ==========')
console.log('ID:', producto.id)
console.log('Nombre:', producto.name)
console.log('Tipo:', producto.type)
console.log('')
console.log('Precio Base (mayorista):', producto.price)
console.log('Precio Mostrado en UI:', document.querySelector('.current-price')?.textContent)
console.log('')
console.log('⚠️ NOTA: Para productos variables, se usa el precio base')
console.log('🔮 TODO: Implementar selector de variaciones con precio dinámico')
console.log('======================================')
```

**Resultado esperado:**
```
========== PRODUCTO VARIABLE ==========
ID: 456
Nombre: Lubricante Sabor Fresa
Tipo: variable

Precio Base (mayorista): 20000
Precio Mostrado en UI: $20000

⚠️ NOTA: Para productos variables, se usa el precio base
🔮 TODO: Implementar selector de variaciones con precio dinámico
======================================
```

---

## 📊 Comparación Visual

### Producto Simple ✅
```
╔═══════════════════════════════════════════╗
║  [Imagen del producto]                    ║
║                                           ║
║  Vibrador Premium                         ║
║  ⭐⭐⭐⭐⭐ 4.5/5 (12 reviews)             ║
║                                           ║
║  $21,900  ← ✅ Precio de short_description║
║                                           ║
║  Color: ● ● ●                            ║
║  Cantidad: [1] [+]                        ║
║  [Agregar al Carrito]                     ║
╚═══════════════════════════════════════════╝
```

### Producto Variable 🔄
```
╔═══════════════════════════════════════════╗
║  [Imagen del producto]                    ║
║                                           ║
║  Lubricante Sabor Fresa                   ║
║  ⭐⭐⭐⭐☆ 4.2/5 (8 reviews)              ║
║                                           ║
║  $20,000  ← 🔄 Precio base (temporal)     ║
║                                           ║
║  Color: ● ● ●                            ║
║  Tamaño: [50ml] [100ml] [200ml]          ║
║  Cantidad: [1] [+]                        ║
║  [Agregar al Carrito]                     ║
╚═══════════════════════════════════════════╝

🔮 Próxima mejora: Cambiar precio al seleccionar tamaño
```

---

## 🎨 Flujo de Datos

### Producto Simple ✅
```
Backend WooCommerce
  ↓
product.type = "simple"
product.short_description = "<h5>Precio $21,900</h5>"
product.price = "15000" (mayorista, ignorado)
  ↓
Frontend (ProductDetailView.vue)
  ↓
isProductSimple.value = true
  ↓
displayPrice = getFormattedProductPrice(product)
  ↓
Extrae de short_description → "$21,900" ✅
  ↓
UI muestra: $21,900
  ↓
Carrito recibe: 21900
```

### Producto Variable 🔄
```
Backend WooCommerce
  ↓
product.type = "variable"
product.price = "20000" (precio base)
product.variations = [
  { size: "50ml", price: "12500" },
  { size: "100ml", price: "18900" },
  { size: "200ml", price: "28500" }
]
  ↓
Frontend (ProductDetailView.vue)
  ↓
isProductSimple.value = false
  ↓
displayPrice = `$${product.price}` (temporal)
  ↓
UI muestra: $20,000 (precio base)
  ↓
🔮 TODO: Actualizar precio al seleccionar variación
```

---

## ✅ Checklist de Prueba

### Producto Simple
- [ ] El precio se extrae de `short_description`
- [ ] Se muestra con formato COP (`$21,900`)
- [ ] Logs muestran "Producto simple - Precio extraído"
- [ ] Al agregar al carrito, usa el precio correcto
- [ ] No hay warnings en consola

### Producto Variable
- [ ] El precio muestra el valor de `product.price`
- [ ] Logs muestran "Producto variable - Usando precio base"
- [ ] Los selectores de variación están visibles
- [ ] Al agregar al carrito, usa el precio base
- [ ] ⚠️ Se muestra nota de "próxima mejora" en logs

---

## 🐛 Problemas Comunes

### Problema 1: Producto simple muestra precio mayorista
**Diagnóstico:**
```javascript
const producto = productStore.wooCurrentProduct
console.log('Tipo:', producto.type)  // ¿Es "simple"?
console.log('Short description:', producto.short_description)  // ¿Tiene precio?
```

**Causas posibles:**
1. El `short_description` está vacío
2. El formato del HTML no coincide con el regex
3. El tipo de producto es incorrecto

**Solución:**
Verificar en WooCommerce admin que:
- El producto sea tipo "simple"
- El campo "Short description" contenga el precio: `<h5>Precio $XX,XXX</h5>`

---

### Problema 2: Producto variable muestra $0
**Diagnóstico:**
```javascript
const producto = productStore.wooCurrentProduct
console.log('Price:', producto.price)  // ¿Tiene valor?
console.log('Type:', producto.type)    // ¿Es "variable"?
```

**Causa:** El campo `price` del producto está vacío

**Solución:** 
En WooCommerce, asegúrate que:
1. El producto tenga al menos una variación creada
2. Las variaciones tengan precios asignados
3. WooCommerce calcule el precio base automáticamente

---

### Problema 3: Log no aparece en consola
**Causa:** El producto no se cargó correctamente

**Diagnóstico:**
```javascript
const productStore = useProductStore()
console.log('Producto cargado:', productStore.wooCurrentProduct)
console.log('Loading:', productStore.isLoadingWooProduct)
console.log('Error:', productStore.wooError)
```

**Solución:**
1. Recargar la página
2. Verificar que el ID del producto sea correcto
3. Revisar errores de red en DevTools → Network

---

## 📝 Resumen de Diferencias

| Aspecto | Producto Simple | Producto Variable |
|---------|----------------|------------------|
| **Tipo** | `type: "simple"` | `type: "variable"` |
| **Fuente Precio** | `short_description` ✅ | `product.price` 🔄 |
| **Log en Consola** | "Producto simple - Precio extraído" | "Producto variable - Usando precio base" |
| **Precio Mostrado** | Correcto (sugerido) | Temporal (base) |
| **En Carrito** | Precio correcto ✅ | Precio base 🔄 |
| **Variaciones** | No aplica | Pendiente implementar |

---

## 🔮 Próximas Mejoras (Productos Variables)

### Fase 1: Selector de Variaciones ⏳
- [ ] Detectar atributos de variación (color, talla, etc.)
- [ ] Mostrar selectores interactivos
- [ ] Cargar datos de variaciones desde WooCommerce

### Fase 2: Precio Dinámico ⏳
- [ ] Obtener precio de cada variación
- [ ] Actualizar precio al seleccionar opciones
- [ ] Mostrar "desde $XX,XXX" si hay múltiples precios

### Fase 3: Stock por Variación ⏳
- [ ] Verificar disponibilidad por variación
- [ ] Deshabilitar opciones sin stock
- [ ] Mostrar mensaje de disponibilidad

---

**✅ Estado Actual:**
- Productos Simples: ✅ **FUNCIONANDO CORRECTAMENTE**
- Productos Variables: 🔄 **USANDO PRECIO BASE (TEMPORAL)**

**🎯 Próximo Paso:** Implementar selector de variaciones con precio dinámico

