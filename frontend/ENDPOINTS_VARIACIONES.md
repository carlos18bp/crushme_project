# 🎯 Endpoints de Variaciones - productStore.js

## ✅ Implementación Completada

Se han agregado **4 nuevos métodos** al `productStore.js` para manejar variaciones de productos WooCommerce.

---

## 📦 Nuevo State Agregado

### Variables de Estado
```javascript
// Variaciones del producto actual
wooProductVariations = []  // Array de variaciones

// Variación específica seleccionada
wooCurrentVariation = null  // Objeto de variación

// Loading states
isLoadingWooVariations = false  // Cargando lista de variaciones
isLoadingWooVariation = false   // Cargando variación específica
```

---

## 🔧 Métodos Disponibles

### 1. `fetchWooProductVariations(productId, perPage, page)` ⭐ NUEVO

Obtiene todas las variaciones de un producto variable.

**Parámetros:**
- `productId` (number) - ID del producto variable
- `perPage` (number, opcional) - Variaciones por página (default: 100, máximo: 100)
- `page` (number, opcional) - Número de página (default: 1)

**Endpoint Backend:**
```
GET /api/products/woocommerce/products/{productId}/variations/?per_page={perPage}&page={page}
```

**Uso:**
```javascript
const productStore = useProductStore()

// Obtener todas las variaciones (default: 100 por página)
const result = await productStore.fetchWooProductVariations(19425)

// Con paginación personalizada
const result = await productStore.fetchWooProductVariations(19425, 50, 1)

if (result.success) {
  console.log('Variaciones:', result.data)
  console.log('Total:', result.total_variations)
}
```

**Respuesta:**
```javascript
{
  success: true,
  data: [
    {
      id: 19427,
      type: "variation",
      sku: "EK-CLV-005-TRIO-FRR-SAC",
      price: "3190",
      regular_price: "3190",
      stock_status: "outofstock",
      attributes: [
        {
          name: "Tamaño",
          option: "Sachet"
        }
      ],
      image: { ... }
    },
    // ... más variaciones
  ],
  total_variations: 2,
  pagination_info: { ... }
}
```

---

### 2. `fetchWooProductVariation(productId, variationId)` ⭐ NUEVO

Obtiene una variación específica de un producto.

**Parámetros:**
- `productId` (number) - ID del producto variable
- `variationId` (number) - ID de la variación específica

**Endpoint Backend:**
```
GET /api/products/woocommerce/products/{productId}/variations/{variationId}/
```

**Uso:**
```javascript
const productStore = useProductStore()

// Obtener variación específica
const result = await productStore.fetchWooProductVariation(19425, 19427)

if (result.success) {
  console.log('Variación:', result.data)
  // La variación también se guarda en productStore.wooCurrentVariation
}
```

**Respuesta:**
```javascript
{
  success: true,
  data: {
    id: 19427,
    type: "variation",
    date_created: "2023-09-04T17:42:10",
    sku: "EK-CLV-005-TRIO-FRR-SAC",
    price: "3190",
    regular_price: "3190",
    sale_price: "",
    on_sale: false,
    stock_quantity: 0,
    stock_status: "outofstock",
    attributes: [ ... ],
    image: { ... },
    dimensions: { ... }
  }
}
```

---

### 3. `getWooVariationById(variationId)` ⭐ NUEVO

Busca una variación por ID en las variaciones ya cargadas (sin hacer request).

**Parámetros:**
- `variationId` (number) - ID de la variación

**Uso:**
```javascript
const productStore = useProductStore()

// Primero cargar variaciones
await productStore.fetchWooProductVariations(19425)

// Luego buscar localmente (sin request al backend)
const variation = productStore.getWooVariationById(19427)

if (variation) {
  console.log('Variación encontrada:', variation.price)
}
```

**Retorna:** `object | null`

---

### 4. `clearWooVariations()` ⭐ NUEVO

Limpia las variaciones del producto actual.

**Uso:**
```javascript
const productStore = useProductStore()

// Limpiar variaciones al cambiar de producto
productStore.clearWooVariations()

// Ahora:
// productStore.wooProductVariations = []
// productStore.wooCurrentVariation = null
```

---

## 📊 Getters Disponibles

### `hasWooVariations` ⭐ NUEVO

Verifica si hay variaciones cargadas.

**Uso:**
```javascript
const productStore = useProductStore()

if (productStore.hasWooVariations) {
  console.log('Hay variaciones cargadas')
}
```

---

## 🎯 Casos de Uso Comunes

### Caso 1: Mostrar Selector de Variaciones

```javascript
// En ProductDetailView.vue

import { useProductStore } from '@/stores/modules/productStore'

const productStore = useProductStore()
const product = computed(() => productStore.wooCurrentProduct)

// Verificar si es producto variable
const isVariable = computed(() => product.value?.type === 'variable')

// Cargar variaciones cuando se monta el componente
onMounted(async () => {
  if (isVariable.value) {
    const result = await productStore.fetchWooProductVariations(product.value.id)
    
    if (result.success) {
      console.log(`${result.total_variations} variaciones cargadas`)
    }
  }
})

// Acceder a las variaciones
const variations = computed(() => productStore.wooProductVariations)
```

---

### Caso 2: Cambiar Precio según Variación Seleccionada

```javascript
const selectedVariationId = ref(null)

// Computed: Precio de la variación seleccionada
const currentPrice = computed(() => {
  if (selectedVariationId.value) {
    const variation = productStore.getWooVariationById(selectedVariationId.value)
    return variation?.price || product.value.price
  }
  return product.value.price
})

// Método: Seleccionar variación
const selectVariation = async (variationId) => {
  selectedVariationId.value = variationId
  
  // Opcional: Cargar detalles completos de la variación
  await productStore.fetchWooProductVariation(product.value.id, variationId)
}
```

---

### Caso 3: Verificar Stock de Variación

```javascript
const checkVariationStock = (variationId) => {
  const variation = productStore.getWooVariationById(variationId)
  
  if (!variation) return false
  
  return variation.stock_status === 'instock' && variation.stock_quantity > 0
}

// Uso en template
<button 
  v-for="variation in productStore.wooProductVariations"
  :key="variation.id"
  :disabled="!checkVariationStock(variation.id)"
  @click="selectVariation(variation.id)"
>
  {{ variation.attributes[0].option }} - ${{ variation.price }}
  <span v-if="!checkVariationStock(variation.id)">(Sin stock)</span>
</button>
```

---

### Caso 4: Agrupar Variaciones por Atributo

```javascript
// Obtener opciones únicas de un atributo (ej: Tamaño)
const availableSizes = computed(() => {
  if (!productStore.hasWooVariations) return []
  
  return productStore.wooProductVariations
    .map(v => v.attributes.find(attr => attr.name === 'Tamaño')?.option)
    .filter((value, index, self) => self.indexOf(value) === index)
})

// Uso en template
<select v-model="selectedSize">
  <option v-for="size in availableSizes" :key="size" :value="size">
    {{ size }}
  </option>
</select>
```

---

## 🔍 Estructura de una Variación

```javascript
{
  id: 19427,                    // ID único de la variación
  type: "variation",            // Siempre "variation"
  
  // Precios
  price: "3190",                // Precio actual
  regular_price: "3190",        // Precio regular
  sale_price: "",               // Precio en oferta (puede estar vacío)
  on_sale: false,               // ¿Está en oferta?
  
  // Stock
  stock_status: "outofstock",   // instock | outofstock | onbackorder
  stock_quantity: 0,            // Cantidad disponible
  manage_stock: true,           // ¿Se gestiona stock?
  
  // SKU
  sku: "EK-CLV-005-TRIO-FRR-SAC",
  
  // Atributos que definen esta variación
  attributes: [
    {
      id: 0,
      name: "Tamaño",
      slug: "tamano",
      option: "Sachet"            // Valor específico de esta variación
    }
  ],
  
  // Imagen específica de la variación
  image: {
    id: 25286,
    src: "https://...",
    name: "...",
    alt: "..."
  },
  
  // Dimensiones
  dimensions: {
    length: "30",
    width: "30",
    height: "30"
  },
  
  // Metadatos adicionales
  permalink: "https://...",
  date_created: "2023-09-04T17:42:10",
  date_modified: "2025-04-08T12:04:51",
  description: "..."
}
```

---

## 📝 Estados del Store

### Acceso Directo
```javascript
const productStore = useProductStore()

// Array de variaciones cargadas
productStore.wooProductVariations
// Ejemplo: [{ id: 19427, ... }, { id: 19426, ... }]

// Variación actual seleccionada
productStore.wooCurrentVariation
// Ejemplo: { id: 19427, price: "3190", ... }

// Loading states
productStore.isLoadingWooVariations  // true/false
productStore.isLoadingWooVariation   // true/false

// Getter
productStore.hasWooVariations        // true/false
```

---

## ⚠️ Notas Importantes

### 1. Paginación
- Las variaciones están paginadas con **máximo 100 por página**
- Si un producto tiene más de 100 variaciones, necesitarás hacer múltiples requests
- El método maneja automáticamente la paginación:
  - Página 1 → Reemplaza `wooProductVariations`
  - Páginas siguientes → Agrega al array existente

### 2. Limpieza de Memoria
- Recuerda llamar `clearWooVariations()` al cambiar de producto
- Esto evita que se muestren variaciones del producto anterior

### 3. Productos Simples vs Variables
- Solo productos con `type: "variable"` tienen variaciones
- Productos `type: "simple"` no tienen variaciones (el request fallará)
- Siempre verifica el tipo antes de cargar variaciones

### 4. Caché Local
- `getWooVariationById()` busca en las variaciones **ya cargadas**
- No hace request al backend (más rápido)
- Útil para búsquedas frecuentes sin recargar

---

## 🎨 Ejemplo Completo de Implementación

```vue
<template>
  <div v-if="isVariable">
    <!-- Loading -->
    <div v-if="productStore.isLoadingWooVariations">
      Cargando variaciones...
    </div>
    
    <!-- Selector de variaciones -->
    <div v-else-if="productStore.hasWooVariations">
      <h3>Selecciona una opción:</h3>
      
      <!-- Tamaños disponibles -->
      <div class="variations">
        <button 
          v-for="variation in productStore.wooProductVariations"
          :key="variation.id"
          :class="{ active: selectedVariation?.id === variation.id }"
          :disabled="variation.stock_status === 'outofstock'"
          @click="selectVariation(variation.id)"
        >
          {{ getVariationLabel(variation) }}
          <span class="price">${{ variation.price }}</span>
          <span v-if="variation.stock_status === 'outofstock'" class="out-of-stock">
            Sin stock
          </span>
        </button>
      </div>
      
      <!-- Precio seleccionado -->
      <div class="selected-price">
        Precio: ${{ selectedPrice }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useProductStore } from '@/stores/modules/productStore'

const productStore = useProductStore()
const product = computed(() => productStore.wooCurrentProduct)
const selectedVariation = ref(null)

// ¿Es producto variable?
const isVariable = computed(() => product.value?.type === 'variable')

// Precio seleccionado
const selectedPrice = computed(() => {
  return selectedVariation.value?.price || product.value?.price || '0'
})

// Cargar variaciones al montar
onMounted(async () => {
  if (isVariable.value) {
    await productStore.fetchWooProductVariations(product.value.id)
  }
})

// Limpiar variaciones al cambiar de producto
watch(() => product.value?.id, () => {
  productStore.clearWooVariations()
  selectedVariation.value = null
})

// Seleccionar variación
const selectVariation = (variationId) => {
  selectedVariation.value = productStore.getWooVariationById(variationId)
}

// Obtener label de la variación
const getVariationLabel = (variation) => {
  return variation.attributes
    .map(attr => attr.option)
    .join(' - ')
}
</script>
```

---

## ✅ Resumen de Métodos

| Método | Descripción | Hace Request |
|--------|-------------|--------------|
| `fetchWooProductVariations()` | Obtiene todas las variaciones | ✅ Sí |
| `fetchWooProductVariation()` | Obtiene variación específica | ✅ Sí |
| `getWooVariationById()` | Busca en variaciones cargadas | ❌ No (local) |
| `clearWooVariations()` | Limpia variaciones | ❌ No |

---

## 🚀 Siguiente Paso

Ahora que los endpoints están agregados, puedes:
1. Implementar selector de variaciones en `ProductDetailView.vue`
2. Mostrar precios dinámicos según variación seleccionada
3. Validar stock por variación
4. Mostrar imágenes específicas de cada variación

---

**Fecha de implementación:** ${new Date().toLocaleDateString('es-CO', { 
  year: 'numeric', 
  month: 'long', 
  day: 'numeric',
  hour: '2-digit',
  minute: '2-digit'
})}

**Estado:** ✅ Endpoints agregados y listos para usar


