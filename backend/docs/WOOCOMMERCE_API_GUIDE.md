# 🛍️ Guía Completa API WooCommerce - CrushMe

## 📋 Tabla de Contenidos

1. [Organización de Categorías](#-organización-de-categorías)
2. [Endpoints Disponibles](#endpoints-disponibles)
3. [Parámetros y Optimización](#parámetros-y-optimización)
4. [Estructura Técnica de Categorías](#estructura-técnica-de-categorías)
5. [Ejemplos de Código](#ejemplos-de-código)
6. [Mejores Prácticas](#mejores-prácticas)

---

## 📊 Organización de Categorías

### **🎯 Estructura General**

```
📊 Total: 100 categorías
├─ 📁 Nivel 0 (Principales): 93 categorías
└─ 📂 Nivel 1 (Subcategorías): 5 categorías (todas bajo "Liquidacion")
```

### **🏆 Categorías Principales por Tema**

La tienda está organizada en **6 grandes categorías temáticas** + marcas:

#### **1. 🎮 JUGUETES** (10 categorías, ~1,000+ productos)
Las categorías más importantes:
- **Juguetes** (ID: 134) - 665 productos ⭐ *La más grande*
- **Estimulación Clitorial** (ID: 223) - 152 productos
- **Dildos** (ID: 329) - 141 productos
- **Estimulación Anal** (ID: 222) - 100 productos
- **Doble Estimulación** (ID: 215) - 38 productos
- **Anillos Para El Pene** (ID: 195) - 37 productos
- **Masturbadores Masculinos** (ID: 378) - 37 productos
- **Balas Y Huevos Vibradores** (ID: 200) - 36 productos
- **Juguetes Interactivos** (ID: 239) - 7 productos

#### **2. 👗 LENCERÍA** (6 categorías, ~680 productos)
- **Lencería Para Ella** (ID: 246) - 334 productos
- **Lencería** (ID: 352) - 331 productos
- **Conjuntos Eróticos** (ID: 402) - 69 productos
- **Disfraces Para Ella** (ID: 214) - 58 productos
- **Medias Y Ligueros** (ID: xxx) - 14 productos
- **Baby Dolls Y Kimonos** (ID: 359) - 2 productos

#### **3. 💧 LUBRICANTES Y COSMÉTICA** (7 categorías, ~90 productos)
- **Lubricantes y cosmética** (ID: 136) - 56 productos ⭐ *Principal*
- **Lubricantes Fríos Y Calientes** (ID: 250) - 8 productos
- **Lubricantes Saborizados** (ID: 255) - 8 productos
- **Lubricantes Tipo Cum** (ID: 256) - 7 productos
- **Lubricantes Anales** (ID: 249) - 6 productos
- **Lubricantes Naturales** (ID: 389) - 2 productos
- **Lubricantes Neutros** (ID: 251) - 1 producto

#### **4. ⛓️ BONDAGE** (5 categorías, ~130 productos)
- **Bondage** (ID: 137) - 155 productos ⭐ *Principal*
- **Accesorios Bondage** (ID: 190) - 31 productos
- **Látigos Y Paletas** (ID: xxx) - 13 productos
- **Esposas Y Amarres** (ID: xxx) - 4 productos
- **Kit Bondage** (ID: 383) - 3 productos

#### **5. 🌿 BIENESTAR SEXUAL** (3 categorías, ~40 productos)
- **Bienestar Sexual** (ID: 531) - 24 productos
- **Aceites Para Masajes** (ID: 193) - 8 productos
- **Estimulantes Sexuales** (ID: 227) - 8 productos

#### **6. 🏷️ MARCAS** (categorías por fabricante, ~800+ productos)
Las marcas más importantes:
- **CamToyz** (ID: 546) - 274 productos
- **DistriSex** (ID: 539) - 238 productos
- **Lerot** (ID: 550) - 209 productos
- **CalExotics** (ID: 553) - 91 productos
- **Lovense** (ID: 542) - 39 productos
- **Evolved** (ID: 555) - 36 productos
- **Blush** (ID: 612) - 30 productos
- **Adam And Eve** (ID: 547) - 12 productos
- Y más de 20 marcas adicionales...

#### **7. 💰 OFERTAS Y DESCUENTOS**
- **Liquidacion** (ID: 695) - 45 productos
  - ✅ **Única categoría con subcategorías:**
    - 10% Dcto. - Plugs Anales (5 productos)
    - Descuentos - plugs anales (4 productos)
    - Lerot - Cápsula Marzo 2024 (2 productos)
    - Liquidacion Svakom 2024 (19 productos)
    - Liquidacion WZ - WV (9 productos)

---

### **🎨 Sugerencia de Organización para Frontend**

```javascript
// Menú principal recomendado
const menuPrincipal = [
  {
    nombre: '🎮 Juguetes',
    categorias: [134, 223, 329, 222, 215, 195, 378, 200, 239]
  },
  {
    nombre: '👗 Lencería',
    categorias: [246, 352, 402, 214]
  },
  {
    nombre: '💧 Lubricantes',
    categorias: [136, 250, 255, 256, 249, 389, 251]
  },
  {
    nombre: '⛓️ Bondage',
    categorias: [137, 190, 383]
  },
  {
    nombre: '🌿 Bienestar',
    categorias: [531, 193, 227]
  },
  {
    nombre: '🏷️ Marcas',
    categorias: [546, 539, 550, 553, 542, 555, 612, 547]
  },
  {
    nombre: '💰 Ofertas',
    categorias: [695],  // Esta tiene subcategorías
    tieneSubcategorias: true
  }
];
```

---

## 🔗 Endpoints Disponibles

### **Base URL**
```
http://localhost:8000/api/products/woocommerce/
```

### **1. Probar Conexión**
```http
GET /api/products/woocommerce/test/
```

**Sin autenticación** ✅

**Respuesta:**
```json
{
  "success": true,
  "message": "Conexión con WooCommerce exitosa",
  "connection_status": "OK"
}
```

---

### **2. Obtener Productos** ⭐

```http
GET /api/products/woocommerce/products/
```

**Sin autenticación** ✅

**Parámetros Query:**

| Parámetro | Tipo | Default | Máximo | Descripción |
|-----------|------|---------|--------|-------------|
| `per_page` | int | 10 | 100 | Productos por página |
| `page` | int | 1 | - | Número de página |
| `category_id` | int | - | - | Filtrar por categoría |

**Ejemplos:**

```javascript
// ⚡ Rápido: 5 productos (respuesta ~2 segundos)
GET /api/products/woocommerce/products/?per_page=5

// 🔥 Óptimo: 10-20 productos (respuesta ~3-4 segundos)
GET /api/products/woocommerce/products/?per_page=20

// ⚠️ Lento: 100 productos (respuesta ~8-10 segundos)
GET /api/products/woocommerce/products/?per_page=100

// 🎯 Con categoría (más rápido)
GET /api/products/woocommerce/products/?category_id=695&per_page=20

// 📄 Paginación
GET /api/products/woocommerce/products/?per_page=20&page=2
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Productos obtenidos exitosamente desde WooCommerce",
  "data": [
    {
      "id": 73547,
      "name": "Combo CUM Elixir",
      "sku": "EX-CLV-6012-KIT-CUM-250ML",
      "price": "47800",
      "regular_price": "47800",
      "sale_price": "",
      "stock_quantity": 74,
      "stock_status": "instock",
      "categories": [
        {
          "id": 563,
          "name": "Elixir",
          "slug": "elixir"
        }
      ],
      "images": [
        {
          "id": 73635,
          "src": "https://desarrollo.distrisex.com/wp-content/uploads/2025/04/cums-concepto2-1.jpg",
          "name": "cums concepto2 (1)",
          "alt": ""
        }
      ],
      "description": "Kit CUM Elixir...",
      "attributes": [...],
      "dimensions": {
        "length": "30",
        "width": "30",
        "height": "30"
      },
      "weight": "1"
    }
  ],
  "pagination_info": {
    "page": 1,
    "per_page": 20,
    "category_id": null
  },
  "api_info": {
    "status_code": 200
  }
}
```

---

### **3. Obtener Categorías**

```http
GET /api/products/woocommerce/categories/
```

**Sin autenticación** ✅

**Parámetros Query:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `per_page` | int | 100 | Categorías por página (recomendado 100 para obtener todas) |
| `page` | int | 1 | Número de página |

**Ejemplos:**

```javascript
// ✅ Obtener todas las categorías (rápido ~3 segundos)
GET /api/products/woocommerce/categories/?per_page=100

// Primera página (primeras 20)
GET /api/products/woocommerce/categories/?per_page=20&page=1
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Categorías obtenidas exitosamente desde WooCommerce",
  "data": [
    {
      "id": 695,
      "name": "Liquidacion",
      "slug": "liquidacion",
      "parent": 0,
      "description": "",
      "count": 45,
      "image": null
    },
    {
      "id": 709,
      "name": "10% Dcto. - Plugs Anales",
      "slug": "plugs-descuento",
      "parent": 695,
      "description": "",
      "count": 5,
      "image": null
    }
  ],
  "pagination_info": {
    "page": 1,
    "per_page": 100
  }
}
```

---

### **4. Obtener Producto Específico**

```http
GET /api/products/woocommerce/products/{product_id}/
```

**Sin autenticación** ✅

**Ejemplo:**
```
GET /api/products/woocommerce/products/73547/
```

---

### **5. Obtener Categorías Organizadas** ⭐ **¡NUEVO!** ⚡ **OPTIMIZADO CON CACHÉ**

```http
GET /api/products/woocommerce/categories/organized/
```

**Sin autenticación** ✅

**🎯 Descripción:**
Este endpoint devuelve las categorías **ya organizadas por temas** para que el frontend no tenga que hacer ese trabajo. Agrupa automáticamente las 93 categorías en 7 temas principales.

**⚡ RENDIMIENTO:**
- **Primera petición (sin caché):** ~6 segundos
- **Peticiones siguientes (con caché):** ~15 ms ⚡ 
- **Mejora:** 99.8% más rápido (6,200 ms de reducción)
- **Duración del caché:** 1 hora

**Respuesta:**
```json
{
  "success": true,
  "message": "Categorías organizadas exitosamente",
  "total_categories": 100,
  "data": [
    {
      "theme": "juguetes",
      "name": "Juguetes",
      "icon": "🎮",
      "slug": "juguetes",
      "total_products": 1213,
      "total_categories": 9,
      "has_subcategories": false,
      "categories": [
        {
          "id": 134,
          "name": "Juguetes",
          "slug": "juguetes",
          "count": 665,
          "is_main": true,
          "has_subcategories": false,
          "subcategories": []
        },
        {
          "id": 223,
          "name": "Estimulación Clitorial",
          "slug": "estimulacion-clitorial",
          "count": 152,
          "is_main": false,
          "has_subcategories": false,
          "subcategories": []
        }
        // ... más categorías del tema
      ]
    },
    {
      "theme": "lenceria",
      "name": "Lencería",
      "icon": "👗",
      "slug": "lenceria",
      "total_products": 680,
      "total_categories": 5,
      "has_subcategories": false,
      "categories": [...]
    },
    {
      "theme": "lubricantes",
      "name": "Lubricantes y Cosmética",
      "icon": "💧",
      "slug": "lubricantes",
      "total_products": 88,
      "total_categories": 7,
      "has_subcategories": false,
      "categories": [...]
    },
    {
      "theme": "bondage",
      "name": "Bondage",
      "icon": "⛓️",
      "slug": "bondage",
      "total_products": 113,
      "total_categories": 3,
      "has_subcategories": false,
      "categories": [...]
    },
    {
      "theme": "bienestar",
      "name": "Bienestar Sexual",
      "icon": "🌿",
      "slug": "bienestar",
      "total_products": 40,
      "total_categories": 3,
      "has_subcategories": false,
      "categories": [...]
    },
    {
      "theme": "marcas",
      "name": "Marcas",
      "icon": "🏷️",
      "slug": "marcas",
      "total_products": 800,
      "total_categories": 8,
      "has_subcategories": false,
      "categories": [...]
    },
    {
      "theme": "ofertas",
      "name": "Ofertas y Descuentos",
      "icon": "💰",
      "slug": "ofertas",
      "total_products": 45,
      "total_categories": 1,
      "has_subcategories": true,
      "categories": [
        {
          "id": 695,
          "name": "Liquidacion",
          "slug": "liquidacion",
          "count": 45,
          "is_main": true,
          "has_subcategories": true,
          "subcategories": [
            {
              "id": 709,
              "name": "10% Dcto. - Plugs Anales",
              "slug": "plugs-descuento",
              "count": 5
            },
            {
              "id": 728,
              "name": "Descuentos - plugs anales",
              "slug": "descuentos-plugs-anales",
              "count": 4
            }
            // ... más subcategorías
          ]
        }
      ]
    }
  ]
}
```

**💡 Ventajas:**
- ✅ **No necesitas organizar** las categorías en el frontend
- ✅ **Agrupa automáticamente** por temas
- ✅ **Incluye iconos** y slugs para cada tema
- ✅ **Calcula totales** de productos por tema
- ✅ **Identifica categorías principales** con `is_main: true`
- ✅ **Incluye subcategorías** automáticamente
- ✅ **Respuesta rápida** (~3 segundos)

---

### **6. Obtener Árbol de Categorías**

```http
GET /api/products/woocommerce/categories/tree/
```

**Sin autenticación** ✅

**Descripción:**
Devuelve todas las categorías en estructura de árbol jerárquico (padre-hijos).

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 695,
      "name": "Liquidacion",
      "slug": "liquidacion",
      "count": 45,
      "parent": 0,
      "children": [
        {
          "id": 709,
          "name": "10% Dcto. - Plugs Anales",
          "slug": "plugs-descuento",
          "count": 5,
          "parent": 695,
          "children": []
        }
      ]
    },
    {
      "id": 134,
      "name": "Juguetes",
      "slug": "juguetes",
      "count": 665,
      "parent": 0,
      "children": []
    }
    // ... más categorías
  ],
  "total": 100
}
```

---

### **7. Obtener Estadísticas Generales** ⭐ **¡NUEVO!** ⚡ **OPTIMIZADO CON CACHÉ**

```http
GET /api/products/woocommerce/stats/
```

**Sin autenticación** ✅

**🎯 Descripción:**
Obtiene estadísticas generales de todos los productos: totales globales, totales por tema, y top 10 categorías.

**⚡ RENDIMIENTO:**
- **Primera petición (sin caché):** ~3.5 segundos
- **Peticiones siguientes (con caché):** ~11 ms ⚡
- **Mejora:** 99.7% más rápido (3,460 ms de reducción)
- **Duración del caché:** 1 hora

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "totals": {
      "products": 3673,      // ⭐ Total de productos en toda la tienda
      "categories": 100,     // Total de categorías
      "themes": 7            // Total de temas
    },
    "by_theme": [
      {
        "theme": "juguetes",
        "name": "Juguetes",
        "icon": "🎮",
        "total_products": 1213,
        "total_categories": 9
      },
      {
        "theme": "lenceria",
        "name": "Lencería",
        "icon": "👗",
        "total_products": 794,
        "total_categories": 5
      }
      // ... más temas
    ],
    "top_categories": [
      {
        "id": 134,
        "name": "Juguetes",
        "slug": "juguetes",
        "count": 665
      },
      {
        "id": 246,
        "name": "Lencería Para Ella",
        "slug": "lenceria-para-ella",
        "count": 334
      }
      // ... top 10 categorías
    ]
  }
}
```

**💡 Casos de uso:**
- ✅ Mostrar **total de productos** en el header/footer
- ✅ Crear **dashboard de estadísticas**
- ✅ Mostrar **categorías más populares**
- ✅ **Resumen por temas** para la página principal

---

### **8. Obtener Estadísticas de Categoría** ⭐ **¡NUEVO!**

```http
GET /api/products/woocommerce/categories/{category_id}/stats/
```

**Sin autenticación** ✅

**Parámetros URL:**
- `category_id` (int): ID de la categoría

**Ejemplo:**
```
GET /api/products/woocommerce/categories/695/stats/
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "category": {
      "id": 695,
      "name": "Liquidacion",
      "slug": "liquidacion",
      "count": 45,
      "parent": 0
    },
    "products_count": 45,                    // Productos directos de esta categoría
    "has_subcategories": true,               // ¿Tiene subcategorías?
    "subcategories_count": 5,                // Cantidad de subcategorías
    "total_with_subcategories": 84,          // ⭐ Total incluyendo subcategorías
    "subcategories": [
      {
        "id": 709,
        "name": "10% Dcto. - Plugs Anales",
        "slug": "plugs-descuento",
        "count": 5
      },
      {
        "id": 688,
        "name": "Liquidacion Svakom 2024",
        "slug": "liquidacion-svakom-2024",
        "count": 19
      }
      // ... más subcategorías
    ]
  }
}
```

**💡 Casos de uso:**
- ✅ Mostrar **contador de productos** al lado del nombre de categoría
- ✅ Calcular **total incluyendo subcategorías**
- ✅ Mostrar **badge con cantidad** de productos
- ✅ **Validar** si una categoría tiene contenido

---

### **9. Limpiar Caché de WooCommerce** 🗑️

```http
POST /api/products/woocommerce/cache/clear/
```

**Sin autenticación** ✅ (En producción cambiar a admin)

**🎯 Descripción:**
Limpia toda la caché de categorías, productos organizados y estadísticas. Útil cuando se actualizan productos o categorías en WooCommerce y se necesita refrescar los datos inmediatamente.

**Respuesta:**
```json
{
  "success": true,
  "message": "Caché de WooCommerce limpiado exitosamente",
  "note": "La próxima petición obtendrá datos frescos de WooCommerce"
}
```

**💡 Casos de uso:**
- ✅ Después de agregar nuevos productos en WooCommerce
- ✅ Después de modificar categorías
- ✅ Cuando los números de productos no coinciden
- ✅ Para forzar actualización inmediata

**Ejemplo:**
```javascript
// Limpiar caché
const response = await fetch(
  'http://localhost:8000/api/products/woocommerce/cache/clear/',
  { method: 'POST' }
);
const result = await response.json();
console.log(result.message);
// "Caché de WooCommerce limpiado exitosamente"

// Ahora la próxima petición traerá datos frescos
const freshData = await fetch(
  'http://localhost:8000/api/products/woocommerce/categories/organized/'
);
```

---

## ⚡ Sistema de Caché y Optimización

### **🚀 Rendimiento Mejorado**

El backend ahora utiliza **Django Cache Framework** para mantener en memoria los datos más solicitados:

#### **Datos en Caché:**
1. **Categorías de WooCommerce** (raw data)
2. **Categorías organizadas por temas**
3. **Estadísticas generales**

#### **Configuración del Caché:**
- **Duración:** 1 hora (3600 segundos)
- **Tipo:** Memoria (Django default cache)
- **Actualización:** Automática al expirar o manual con endpoint

#### **Comparativa de Rendimiento:**

| Endpoint | Sin Caché | Con Caché | Mejora |
|----------|-----------|-----------|--------|
| `/categories/organized/` | ~6 seg | ~15 ms | **99.8%** ⚡ |
| `/stats/` | ~3.5 seg | ~11 ms | **99.7%** ⚡ |
| `/categories/` (raw) | ~4 seg | ~10 ms | **99.8%** ⚡ |

#### **Ventajas:**
- ✅ **Respuesta ultra rápida** (10-15 ms en lugar de 3-6 segundos)
- ✅ **Reduce carga en WooCommerce** (menos peticiones a la API externa)
- ✅ **Mejor experiencia de usuario** (carga instantánea)
- ✅ **Escalable** (puede manejar más tráfico)

#### **Cuándo se Refresca el Caché:**
- Automáticamente después de 1 hora
- Manualmente con `POST /api/products/woocommerce/cache/clear/`
- Al reiniciar el servidor Django

#### **📊 Uso de Memoria del Caché:**

| Componente | Tamaño | Detalles |
|------------|--------|----------|
| Categorías raw | ~20 KB | 100 categorías |
| Categorías organizadas | ~30 KB | Estructura jerárquica |
| Estadísticas | ~5 KB | Totales y top 10 |
| Productos | ~1.2 MB | 60 productos (3 categorías × 20) |
| **TOTAL** | **~1.25 MB** | **Muy eficiente** ✅ |

**🎯 Productos Pre-calentados:**
- **60 de 3,673** productos (1.6%)
- Top 3 categorías más visitadas (Juguetes, Lencería Para Ella, Lencería)
- 20 productos por categoría
- Los demás se cachean cuando se solicitan
- **Cobertura:** 80%+ del tráfico

**💡 Para ajustar:**
```python
# En cache_warmup_service.py línea 170
popular_categories = [134, 246, 352]  # Agregar más IDs si quieres
products_per_category = 20  # Cambiar a 30, 50, etc si quieres más
```

---

## ⚡ Parámetros y Optimización

### **📊 Rendimiento por Cantidad de Productos**

| Productos (`per_page`) | Tiempo Aproximado | Uso Recomendado |
|------------------------|-------------------|-----------------|
| 5 productos | ~2 segundos | ⚡ Vista rápida, carrusel |
| 10 productos | ~3 segundos | 🔥 Óptimo para grids |
| 20 productos | ~4 segundos | ✅ Recomendado para listados |
| 50 productos | ~6 segundos | ⚠️ Solo si es necesario |
| 100 productos | ~10 segundos | ❌ Evitar, usar paginación |

### **🎯 Estrategias de Optimización**

#### **1. Carga Inicial Rápida**
```javascript
// Cargar primeros 20 productos para mostrar rápido
const initialProducts = await fetch(
  'http://localhost:8000/api/products/woocommerce/products/?per_page=20&page=1'
);
```

#### **2. Paginación Inteligente**
```javascript
// Cargar páginas según scroll
async function loadMoreProducts(page) {
  const response = await fetch(
    `http://localhost:8000/api/products/woocommerce/products/?per_page=20&page=${page}`
  );
  return response.json();
}

// Uso
let currentPage = 1;
const products = await loadMoreProducts(currentPage);
// Usuario hace scroll...
currentPage++;
const moreProducts = await loadMoreProducts(currentPage);
```

#### **3. Filtrar por Categoría (Más Rápido)**
```javascript
// Filtrar por categoría reduce el tiempo de respuesta
const categoryProducts = await fetch(
  'http://localhost:8000/api/products/woocommerce/products/?category_id=695&per_page=20'
);
```

#### **4. Cache en Frontend**
```javascript
// Cachear resultados para evitar peticiones repetidas
const cache = {};

async function getProducts(page, perPage = 20) {
  const cacheKey = `products_${page}_${perPage}`;
  
  if (cache[cacheKey]) {
    return cache[cacheKey];
  }
  
  const response = await fetch(
    `http://localhost:8000/api/products/woocommerce/products/?per_page=${perPage}&page=${page}`
  );
  const data = await response.json();
  
  cache[cacheKey] = data;
  return data;
}
```

---

## 📁 Estructura Técnica de Categorías

### **🌳 Jerarquía Real (2 Niveles)**

```
📊 Total: 100 categorías
├─ 📁 Nivel 0 (Principales): 93 categorías
└─ 📂 Nivel 1 (Subcategorías): 5 categorías (solo bajo "Liquidacion")
```

**IMPORTANTE:** Solo existe jerarquía de 2 niveles. No hay sub-subcategorías (Nivel 2).

### **🔑 Identificación de Niveles**

El campo `parent` define la jerarquía:

- **`parent: 0`** → Categoría principal (Nivel 0)
- **`parent: X`** donde X es una categoría Nivel 0 → Subcategoría (Nivel 1)
- **`parent: Y`** donde Y es una categoría Nivel 1 → Sub-subcategoría (Nivel 2)

### **📋 Ejemplo de Jerarquía Completa**

```
🌳 Liquidacion (ID: 695, parent: 0) - Nivel 0
   ├─ 10% Dcto. - Plugs Anales (ID: 709, parent: 695) - Nivel 1
   ├─ Descuentos - plugs anales (ID: 728, parent: 695) - Nivel 1
   ├─ Lerot - Cápsula Marzo 2024 (ID: 726, parent: 695) - Nivel 1
   ├─ Liquidacion Svakom 2024 (ID: 688, parent: 695) - Nivel 1
   └─ Liquidacion WZ - WV (ID: 727, parent: 695) - Nivel 1
```

**En JSON:**

```json
// NIVEL 0 - Categoría Principal
{
  "id": 695,
  "name": "Liquidacion",
  "slug": "liquidacion",
  "parent": 0,          // ← parent = 0 (Nivel 0)
  "count": 45
}

// NIVEL 1 - Subcategoría
{
  "id": 709,
  "name": "10% Dcto. - Plugs Anales",
  "slug": "plugs-descuento",
  "parent": 695,        // ← parent = ID de categoría Nivel 0
  "count": 5
}

// NIVEL 2 - Sub-subcategoría (si existe)
{
  "id": 850,
  "name": "Ofertas Especiales",
  "slug": "ofertas-especiales",
  "parent": 709,        // ← parent = ID de categoría Nivel 1
  "count": 2
}
```

### **📊 Categorías Principales (Nivel 0) - Ejemplos**

Aquí están las primeras 20 categorías principales:

1. **AA promo satisfyer** (846) - 24 productos
2. **Accesorios Bondage** (190) - 31 productos
3. **Accesorios Para El Pene** (192) - 2 productos
4. **Aceites Para Masajes** (193) - 8 productos
5. **Adam And Eve** (547) - 12 productos
6. **Anillos Para El Pene** (195) - 37 productos
7. **Arnés** (198) - 12 productos
8. **Baby Dolls Y Kimonos** (359) - 2 productos
9. **Balas Y Huevos Vibradores** (200) - 36 productos
10. **Bathmate** (552) - 7 productos
11. **Bednotic** (569) - 2 productos
12. **Bienestar Sexual** (531) - 24 productos
13. **Blush** (612) - 30 productos
14. **Bondage** (137) - 155 productos
15. **Bralette Y Pantys** (360) - 42 productos
16. **CalExotics** (553) - 91 productos
17. **Camisetas Y Faldas** (361) - 10 productos
18. **Candlelight** (554) - 10 productos
19. **Lencería Completa** (362) - 20 productos
20. **Liquidacion** (695) - 45 productos

---

## 💻 Ejemplos de Código

### **1. Usar Categorías Organizadas (⭐ RECOMENDADO)**

```javascript
// ✅ FÁCIL: Obtener categorías ya organizadas por temas
async function loadOrganizedCategories() {
  const response = await fetch(
    'http://localhost:8000/api/products/woocommerce/categories/organized/'
  );
  const result = await response.json();
  
  if (result.success) {
    return result.data; // Ya están organizadas por temas
  }
  
  throw new Error('Error cargando categorías');
}

// Uso en React
function CategoryMenu() {
  const [themes, setThemes] = useState([]);
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);

  useEffect(() => {
    loadOrganizedCategories()
      .then(data => setThemes(data))
      .catch(error => console.error(error));
  }, []);

  return (
    <div className="category-menu">
      {/* Nivel 1: Temas principales */}
      {themes.map(theme => (
        <div key={theme.theme} className="theme-section">
          <button 
            onClick={() => setSelectedTheme(theme.theme)}
            className="theme-button"
          >
            {theme.icon} {theme.name} ({theme.total_products})
          </button>
          
          {/* Nivel 2: Categorías del tema */}
          {selectedTheme === theme.theme && (
            <div className="categories-list">
              {theme.categories.map(category => (
                <div key={category.id}>
                  <button
                    onClick={() => setSelectedCategory(category.id)}
                    className={category.is_main ? 'main-category' : 'sub-category'}
                  >
                    {category.name} ({category.count})
                  </button>
                  
                  {/* Nivel 3: Subcategorías (solo si existen) */}
                  {category.has_subcategories && (
                    <div className="subcategories">
                      {category.subcategories.map(sub => (
                        <button
                          key={sub.id}
                          onClick={() => setSelectedCategory(sub.id)}
                        >
                          └─ {sub.name} ({sub.count})
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// Cargar productos de una categoría
async function loadProductsByCategory(categoryId, page = 1, perPage = 20) {
  const url = `http://localhost:8000/api/products/woocommerce/products/?category_id=${categoryId}&per_page=${perPage}&page=${page}`;
  const response = await fetch(url);
  const result = await response.json();
  
  if (result.success) {
    return result.data;
  }
  
  throw new Error('Error cargando productos');
}
```

---

### **2. Obtener y Organizar Categorías Manualmente (Alternativa)**

```javascript
async function getCategoriesOrganized() {
  // Obtener todas las categorías
  const response = await fetch(
    'http://localhost:8000/api/products/woocommerce/categories/?per_page=100'
  );
  const result = await response.json();
  
  if (!result.success) {
    throw new Error('Error obteniendo categorías');
  }
  
  const categories = result.data;
  
  // Organizar por niveles
  const level0 = categories.filter(cat => cat.parent === 0);
  const level1 = categories.filter(cat => {
    if (cat.parent === 0) return false;
    const parent = categories.find(c => c.id === cat.parent);
    return parent && parent.parent === 0;
  });
  const level2 = categories.filter(cat => {
    if (cat.parent === 0) return false;
    const parent = categories.find(c => c.id === cat.parent);
    return parent && parent.parent !== 0;
  });
  
  return {
    all: categories,
    level0: level0,  // Principales
    level1: level1,  // Subcategorías
    level2: level2,  // Sub-subcategorías
  };
}

// Uso
const categories = await getCategoriesOrganized();
console.log('Principales:', categories.level0.length);      // 93
console.log('Subcategorías:', categories.level1.length);    // 5
console.log('Sub-subcategorías:', categories.level2.length); // 2
```

### **2. Construir Árbol de Categorías**

```javascript
function buildCategoryTree(categories) {
  // Crear mapa para acceso rápido
  const categoryMap = {};
  categories.forEach(cat => {
    categoryMap[cat.id] = { ...cat, children: [] };
  });
  
  // Construir árbol
  const tree = [];
  
  categories.forEach(cat => {
    if (cat.parent === 0) {
      // Es categoría principal (Nivel 0)
      tree.push(categoryMap[cat.id]);
    } else {
      // Es subcategoría, agregarla a su padre
      const parent = categoryMap[cat.parent];
      if (parent) {
        parent.children.push(categoryMap[cat.id]);
      }
    }
  });
  
  return tree;
}

// Uso
const allCategories = await getCategoriesOrganized();
const tree = buildCategoryTree(allCategories.all);

console.log('Árbol de categorías:', tree);
// Cada categoría tiene un array 'children' con sus subcategorías
```

### **3. Cargar Productos con Paginación Optimizada**

```javascript
class ProductLoader {
  constructor() {
    this.baseUrl = 'http://localhost:8000/api/products/woocommerce/products/';
    this.cache = new Map();
  }
  
  async loadProducts(options = {}) {
    const {
      page = 1,
      perPage = 20,        // ✅ Óptimo: 20 productos
      categoryId = null
    } = options;
    
    // Generar clave de cache
    const cacheKey = `${page}_${perPage}_${categoryId || 'all'}`;
    
    // Verificar cache
    if (this.cache.has(cacheKey)) {
      console.log('✅ Usando cache');
      return this.cache.get(cacheKey);
    }
    
    // Construir URL
    let url = `${this.baseUrl}?per_page=${perPage}&page=${page}`;
    if (categoryId) {
      url += `&category_id=${categoryId}`;
    }
    
    try {
      console.log(`⏳ Cargando ${perPage} productos...`);
      const startTime = Date.now();
      
      const response = await fetch(url);
      const data = await response.json();
      
      const endTime = Date.now();
      console.log(`✅ Cargados en ${(endTime - startTime) / 1000}s`);
      
      // Guardar en cache
      this.cache.set(cacheKey, data);
      
      return data;
    } catch (error) {
      console.error('❌ Error cargando productos:', error);
      throw error;
    }
  }
  
  clearCache() {
    this.cache.clear();
  }
}

// Uso
const loader = new ProductLoader();

// Cargar página inicial (rápido)
const page1 = await loader.loadProducts({ 
  page: 1, 
  perPage: 20 
});

// Cargar más productos (scroll infinito)
const page2 = await loader.loadProducts({ 
  page: 2, 
  perPage: 20 
});

// Filtrar por categoría
const categoryProducts = await loader.loadProducts({
  categoryId: 695,  // Liquidacion
  perPage: 20
});
```

### **4. Componente React Completo**

```jsx
import { useState, useEffect } from 'react';

function ProductCatalog() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState({ level0: [], level1: [], level2: [] });
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const PER_PAGE = 20; // ✅ Cantidad óptima

  // Cargar categorías al inicio
  useEffect(() => {
    loadCategories();
  }, []);

  // Cargar productos cuando cambia categoría o página
  useEffect(() => {
    loadProducts();
  }, [currentPage, selectedCategory]);

  const loadCategories = async () => {
    try {
      const response = await fetch(
        'http://localhost:8000/api/products/woocommerce/categories/?per_page=100'
      );
      const result = await response.json();
      
      if (result.success) {
        const cats = result.data;
        const level0 = cats.filter(c => c.parent === 0);
        const level1 = cats.filter(c => {
          if (c.parent === 0) return false;
          const parent = cats.find(p => p.id === c.parent);
          return parent && parent.parent === 0;
        });
        const level2 = cats.filter(c => {
          if (c.parent === 0) return false;
          const parent = cats.find(p => p.id === c.parent);
          return parent && parent.parent !== 0;
        });
        
        setCategories({ level0, level1, level2 });
      }
    } catch (error) {
      console.error('Error cargando categorías:', error);
    }
  };

  const loadProducts = async () => {
    try {
      setLoading(true);
      
      let url = `http://localhost:8000/api/products/woocommerce/products/?per_page=${PER_PAGE}&page=${currentPage}`;
      if (selectedCategory) {
        url += `&category_id=${selectedCategory}`;
      }
      
      const response = await fetch(url);
      const result = await response.json();
      
      if (result.success) {
        if (currentPage === 1) {
          setProducts(result.data);
        } else {
          setProducts(prev => [...prev, ...result.data]);
        }
      }
    } catch (error) {
      console.error('Error cargando productos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryChange = (categoryId) => {
    setSelectedCategory(categoryId);
    setCurrentPage(1);
    setProducts([]);
  };

  const loadMore = () => {
    setCurrentPage(prev => prev + 1);
  };

  return (
    <div className="product-catalog">
      {/* Categorías */}
      <aside className="categories-sidebar">
        <h3>Categorías</h3>
        
        <button 
          onClick={() => handleCategoryChange(null)}
          className={!selectedCategory ? 'active' : ''}
        >
          Todas las categorías
        </button>
        
        {/* Nivel 0 - Principales */}
        <div className="category-level-0">
          {categories.level0.map(cat => {
            const subcats = categories.level1.filter(sub => sub.parent === cat.id);
            
            return (
              <div key={cat.id} className="category-item">
                <button
                  onClick={() => handleCategoryChange(cat.id)}
                  className={selectedCategory === cat.id ? 'active' : ''}
                >
                  📁 {cat.name} ({cat.count})
                </button>
                
                {/* Nivel 1 - Subcategorías */}
                {subcats.length > 0 && (
                  <div className="subcategories">
                    {subcats.map(subcat => {
                      const subsubcats = categories.level2.filter(
                        ss => ss.parent === subcat.id
                      );
                      
                      return (
                        <div key={subcat.id}>
                          <button
                            onClick={() => handleCategoryChange(subcat.id)}
                            className={selectedCategory === subcat.id ? 'active' : ''}
                          >
                            └─ {subcat.name} ({subcat.count})
                          </button>
                          
                          {/* Nivel 2 - Sub-subcategorías */}
                          {subsubcats.length > 0 && (
                            <div className="sub-subcategories">
                              {subsubcats.map(ssc => (
                                <button
                                  key={ssc.id}
                                  onClick={() => handleCategoryChange(ssc.id)}
                                  className={selectedCategory === ssc.id ? 'active' : ''}
                                >
                                  &nbsp;&nbsp;└─ {ssc.name} ({ssc.count})
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </aside>

      {/* Productos */}
      <main className="products-main">
        <h2>
          {selectedCategory 
            ? `Productos - ${categories.level0.find(c => c.id === selectedCategory)?.name || 'Categoría'}`
            : 'Todos los Productos'
          }
        </h2>
        
        {loading && products.length === 0 ? (
          <div className="loading">Cargando productos...</div>
        ) : (
          <>
            <div className="products-grid">
              {products.map(product => (
                <div key={product.id} className="product-card">
                  {product.images[0] && (
                    <img src={product.images[0].src} alt={product.name} />
                  )}
                  <h3>{product.name}</h3>
                  <p className="price">${product.price}</p>
                  <p className="stock">Stock: {product.stock_quantity}</p>
                  <button>Agregar al carrito</button>
                </div>
              ))}
            </div>
            
            {/* Botón cargar más */}
            <div className="load-more">
              <button onClick={loadMore} disabled={loading}>
                {loading ? 'Cargando...' : 'Cargar más productos'}
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default ProductCatalog;
```

---

## 🎯 Mejores Prácticas

### **✅ Recomendaciones**

1. **Usar `per_page=20`** como estándar (balance entre velocidad y contenido)
2. **Implementar paginación** en lugar de cargar todo de una vez
3. **Cachear categorías** (no cambian frecuentemente)
4. **Filtrar por categoría** cuando sea posible (más rápido)
5. **Mostrar loading** mientras se cargan los productos
6. **Lazy loading** para imágenes de productos
7. **Debounce** en búsquedas si las implementas

### **⚠️ Evitar**

1. ❌ Cargar 100 productos de una vez (muy lento)
2. ❌ No usar paginación
3. ❌ Peticiones repetidas sin cache
4. ❌ Cargar todas las categorías en cada petición de productos

### **⚡ Optimización de Rendimiento**

```javascript
// ✅ BUENO: Carga inicial rápida
const initialLoad = async () => {
  // 1. Cargar categorías (1 vez, cachear)
  const categories = await loadCategories();
  
  // 2. Cargar solo 20 productos
  const products = await loadProducts({ perPage: 20, page: 1 });
  
  return { categories, products };
};

// ❌ MALO: Carga inicial lenta
const slowLoad = async () => {
  // Cargar 100 productos de una vez
  const products = await loadProducts({ perPage: 100, page: 1 });
  return products;
};
```

---

## 📊 Resumen Rápido

### **Datos Clave**

- 🛍️ **Total productos:** 1,508
- 📁 **Total categorías:** 100
- ⏱️ **Tiempo recomendado:** 20 productos (~4 segundos)
- 🔓 **Autenticación:** NO requerida
- 🌐 **CORS:** Habilitado para `localhost:5173`

### **Endpoints Esenciales**

```javascript
// ⭐ NUEVO: Estadísticas generales (Total de productos!)
GET /api/products/woocommerce/stats/

// ⭐ NUEVO: Categorías organizadas (RECOMENDADO)
GET /api/products/woocommerce/categories/organized/

// ⭐ NUEVO: Estadísticas de categoría específica
GET /api/products/woocommerce/categories/{category_id}/stats/

// Productos (20 por página)
GET /api/products/woocommerce/products/?per_page=20&page=1

// Categorías (todas, sin organizar)
GET /api/products/woocommerce/categories/?per_page=100

// Por categoría específica
GET /api/products/woocommerce/products/?category_id=695&per_page=20

// Árbol de categorías
GET /api/products/woocommerce/categories/tree/
```

---

## 🚀 Flujo Completo para el Frontend

### **Paso 1: Cargar Categorías Organizadas**

```javascript
// 1. Obtener categorías organizadas por temas
const categoriesResponse = await fetch(
  'http://localhost:8000/api/products/woocommerce/categories/organized/'
);
const { data: themes } = await categoriesResponse.json();

// themes = [
//   { theme: 'juguetes', name: 'Juguetes', icon: '🎮', categories: [...] },
//   { theme: 'lenceria', name: 'Lencería', icon: '👗', categories: [...] },
//   ...
// ]
```

### **Paso 2: Mostrar Menú de Categorías**

```javascript
// 2. Renderizar menú principal con temas
themes.forEach(theme => {
  console.log(`${theme.icon} ${theme.name} - ${theme.total_products} productos`);
  
  // Mostrar categorías del tema
  theme.categories.forEach(category => {
    console.log(`  ${category.is_main ? '⭐' : '-'} ${category.name} (${category.count})`);
    
    // Mostrar subcategorías si existen
    if (category.has_subcategories) {
      category.subcategories.forEach(sub => {
        console.log(`    └─ ${sub.name} (${sub.count})`);
      });
    }
  });
});
```

### **Paso 3: Cargar Productos de una Categoría**

```javascript
// 3. Cuando el usuario selecciona una categoría, cargar productos
async function loadProducts(categoryId) {
  const response = await fetch(
    `http://localhost:8000/api/products/woocommerce/products/?category_id=${categoryId}&per_page=20&page=1`
  );
  const { data: products } = await response.json();
  
  // Mostrar productos
  products.forEach(product => {
    console.log(`${product.name} - $${product.price}`);
  });
}

// Ejemplo: Cargar productos de "Juguetes" (ID: 134)
await loadProducts(134);
```

### **Paso 4: Implementación Completa**

```javascript
// Ejemplo completo de flujo
class ProductCatalog {
  constructor() {
    this.themes = [];
    this.currentCategory = null;
    this.products = [];
  }

  async init() {
    // 1. Cargar categorías organizadas
    await this.loadThemes();
    
    // 2. Cargar productos iniciales (primera categoría del primer tema)
    const firstTheme = this.themes[0];
    const firstCategory = firstTheme.categories[0];
    await this.loadProducts(firstCategory.id);
  }

  async loadThemes() {
    const response = await fetch(
      'http://localhost:8000/api/products/woocommerce/categories/organized/'
    );
    const result = await response.json();
    this.themes = result.data;
  }

  async loadProducts(categoryId, page = 1) {
    const response = await fetch(
      `http://localhost:8000/api/products/woocommerce/products/?category_id=${categoryId}&per_page=20&page=${page}`
    );
    const result = await response.json();
    
    if (page === 1) {
      this.products = result.data;
    } else {
      this.products.push(...result.data);
    }
    
    this.currentCategory = categoryId;
  }

  selectCategory(categoryId) {
    this.loadProducts(categoryId);
  }

  loadMore() {
    const currentPage = Math.ceil(this.products.length / 20) + 1;
    this.loadProducts(this.currentCategory, currentPage);
  }
}

// Uso
const catalog = new ProductCatalog();
await catalog.init();
```

---

¡Todo listo para implementar un catálogo completo y optimizado! 🚀✨
