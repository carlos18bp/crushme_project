# 📦 Documentación de Endpoints de Productos

## Tabla de Contenidos
1. [Detalle de Producto](#1-detalle-de-producto)
2. [Stock de Producto](#2-stock-de-producto-nuevo)
3. [Lista de Productos](#3-lista-de-productos)
4. [Variaciones de Producto](#4-variaciones-de-producto)
   - 4.1. [Detalle de Variación Específica](#41-detalle-de-variación-específica)
5. [Productos en Tendencia](#5-productos-en-tendencia)
6. [Flujo Completo: Productos Variables](#flujo-completo-productos-variables)

---

## 1. Detalle de Producto

### Endpoint
```
GET /api/products/woocommerce/products/{product_id}/
```

### Descripción
Obtiene el detalle completo de un producto con información traducida, precios con margen aplicado y stock en tiempo real desde WooCommerce.

### Parámetros de URL
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `product_id` | integer | Sí | ID del producto en WooCommerce |

### Query Parameters
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `lang` | string | `es` | Idioma de la respuesta (`es` o `en`) |
| `real_time_stock` | boolean | `true` | Si debe consultar stock real de WooCommerce |

### Headers
```
Accept-Language: en  # Alternativa al query param lang
```

### Ejemplo de Request
```bash
# Español con stock real (por defecto)
GET /api/products/woocommerce/products/82257/

# Inglés con stock real
GET /api/products/woocommerce/products/82257/?lang=en

# Español con stock local (más rápido)
GET /api/products/woocommerce/products/82257/?real_time_stock=false

# Con header de idioma
curl -H "Accept-Language: en" \
  http://localhost:8000/api/products/woocommerce/products/82257/
```

### Respuesta Exitosa (200 OK)

```json
{
  "success": true,
  "data": {
    "id": 82257,
    "name": "Massage oil Coco Tropical Erotic",
    "slug": "aceite-para-masajes-coco-tropical-erotic",
    "permalink": "https://distrisexcolombia.com/producto/aceite-para-masajes-coco-tropical-erotic/",
    "type": "variable",
    "is_variable": true,
    "variations_count": 2,
    "variations_endpoint": "/api/products/woocommerce/products/82257/variations/",
    "attributes": [
      {
        "name": "Tamaño",
        "slug": "attribute_pa_tamano",
        "options": ["250ML", "30ML"]
      }
    ],
    "available_variations": [
      {
        "id": 82295,
        "attributes": {
          "Tamaño": "250ML"
        },
        "in_stock": true,
        "stock_quantity": 10,
        "price": 8490.0
      },
      {
        "id": 82296,
        "attributes": {
          "Tamaño": "30ML"
        },
        "in_stock": true,
        "stock_quantity": 5,
        "price": 4990.0
      }
    ],
    "short_description": "",
    "description": "The Glass Anal Plug is a sex toy designed for anal stimulation...",
    "price": 8490.0,
    "regular_price": null,
    "sale_price": null,
    "on_sale": false,
    "categories": [
      {
        "id": 251,
        "name": "Massage Oils",
        "slug": "aceites-para-masajes"
      }
    ],
    "images": [
      {
        "id": 82280,
        "src": "https://distrisexcolombia.com/wp-content/uploads/2025/10/Lubricante-sensual-intimo-00.jpg",
        "name": "Lubricante sensual intimo 00",
        "alt": "",
        "thumbnail": "https://distrisexcolombia.com/wp-content/uploads/2025/10/Lubricante-sensual-intimo-00-300x300.jpg"
      },
      {
        "id": 82279,
        "src": "https://distrisexcolombia.com/wp-content/uploads/2025/10/Lubricante-sensual-intimo-01.jpg",
        "name": "Lubricante sensual intimo 01",
        "alt": "",
        "thumbnail": "https://distrisexcolombia.com/wp-content/uploads/2025/10/Lubricante-sensual-intimo-01-300x300.jpg"
      }
    ],
    "average_rating": 0.0,
    "rating_count": 0,
    "featured": false,
    "status": "publish",
    "stock_status": "instock",
    "stock_quantity": 15,
    "manage_stock": true,
    "in_stock": true,
    "real_time_stock": true
  },
  "language": "en",
  "source": "local_db_with_realtime_stock"
}
```

### Campos de la Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `success` | boolean | Indica si la operación fue exitosa |
| `data` | object | Objeto con los datos del producto |
| `data.id` | integer | ID del producto en WooCommerce |
| `data.name` | string | Nombre del producto (traducido según idioma) |
| `data.slug` | string | Slug del producto para URLs |
| `data.permalink` | string | URL completa del producto en WooCommerce |
| `data.type` | string | Tipo de producto (`simple`, `variable`, `grouped`) |
| `data.is_variable` | boolean | Si el producto tiene variaciones |
| `data.variations_count` | integer | Cantidad de variaciones (solo si `is_variable=true`) |
| `data.variations_endpoint` | string | Endpoint para consultar variaciones (solo si `is_variable=true`) |
| `data.attributes` | array | Atributos disponibles del producto (solo si `is_variable=true`) |
| `data.attributes[].name` | string | Nombre del atributo (ej: "Color", "Tamaño") |
| `data.attributes[].slug` | string | Slug del atributo para matching |
| `data.attributes[].options` | array | Opciones disponibles para este atributo |
| `data.available_variations` | array | Resumen de todas las variaciones (solo si `is_variable=true`) |
| `data.available_variations[].id` | integer | ID de la variación |
| `data.available_variations[].attributes` | object | Atributos de esta variación |
| `data.available_variations[].in_stock` | boolean | Si está en stock |
| `data.available_variations[].stock_quantity` | integer | Cantidad disponible |
| `data.available_variations[].price` | float | Precio de esta variación |
| `data.short_description` | string | Descripción corta (traducida, sin HTML) |
| `data.description` | string | Descripción completa (traducida, sin HTML) |
| `data.price` | float | Precio con margen aplicado (COP) |
| `data.regular_price` | float\|null | Precio regular con margen |
| `data.sale_price` | float\|null | Precio de oferta con margen |
| `data.on_sale` | boolean | Si el producto está en oferta |
| `data.categories` | array | Array de categorías del producto |
| `data.categories[].id` | integer | ID de la categoría |
| `data.categories[].name` | string | Nombre de la categoría (traducido) |
| `data.categories[].slug` | string | Slug de la categoría |
| `data.images` | array | Array de imágenes del producto |
| `data.images[].id` | integer | ID de la imagen |
| `data.images[].src` | string | URL de la imagen completa |
| `data.images[].name` | string | Nombre de la imagen |
| `data.images[].alt` | string | Texto alternativo |
| `data.images[].thumbnail` | string | URL de la miniatura |
| `data.average_rating` | float | Rating promedio (0-5) |
| `data.rating_count` | integer | Cantidad de reviews |
| `data.featured` | boolean | Si es producto destacado |
| `data.status` | string | Estado del producto (`publish`, `draft`) |
| `data.stock_status` | string | Estado del stock (`instock`, `outofstock`) |
| `data.stock_quantity` | integer\|null | Cantidad disponible |
| `data.manage_stock` | boolean | Si maneja inventario |
| `data.in_stock` | boolean | Si está disponible |
| `data.real_time_stock` | boolean | Si el stock es en tiempo real |
| `language` | string | Idioma de la respuesta |
| `source` | string | Origen de los datos |

### Errores Posibles

#### Producto no encontrado (404)
```json
{
  "error": "Producto no encontrado",
  "product_id": 99999
}
```

#### Error interno (500)
```json
{
  "error": "Error interno del servidor",
  "details": "Error message..."
}
```

---

## 2. Stock de Producto (NUEVO) ⭐

### Endpoint
```
GET /api/products/woocommerce/products/{product_id}/stock/
```

### Descripción
Consulta **SOLO el stock** de un producto en tiempo real desde WooCommerce. Endpoint ligero y rápido diseñado para verificar disponibilidad antes de agregar al carrito.

⚠️ **IMPORTANTE**: Si el producto es de tipo `variable` (tiene variaciones), este endpoint retorna información indicando que debe consultar el stock de cada variación individual.

### Parámetros de URL
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `product_id` | integer | Sí | ID del producto en WooCommerce |

### Query Parameters
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `real_time` | boolean | `true` | Si debe consultar WooCommerce o usar datos locales |

### Ejemplo de Request
```bash
# Stock en tiempo real (por defecto)
GET /api/products/woocommerce/products/82257/stock/

# Stock desde DB local (más rápido)
GET /api/products/woocommerce/products/82257/stock/?real_time=false

# Con curl
curl http://localhost:8000/api/products/woocommerce/products/82257/stock/
```

### Respuesta Exitosa (200 OK)

#### Producto Simple - Stock en tiempo real
```json
{
  "success": true,
  "product_id": 82257,
  "stock": {
    "status": "instock",
    "quantity": 15,
    "manage_stock": true,
    "in_stock": true,
    "backorders_allowed": false,
    "available": true
  },
  "source": "woocommerce_realtime",
  "timestamp": "2025-10-20T21:30:00Z"
}
```

#### Producto Variable - Requiere consultar variaciones
```json
{
  "success": true,
  "product_id": 20090,
  "product_type": "variable",
  "message": "Este producto tiene variaciones. Consulta el stock de cada variación.",
  "variations_count": 4,
  "variations_endpoint": "/api/products/woocommerce/products/20090/variations/",
  "stock": {
    "status": "variable",
    "requires_variation_selection": true,
    "manage_stock": false,
    "available": true
  }
}
```

#### Stock desde DB local
```json
{
  "success": true,
  "product_id": 82257,
  "stock": {
    "status": "instock",
    "quantity": 15,
    "manage_stock": true,
    "in_stock": true,
    "backorders_allowed": false,
    "available": true
  },
  "source": "local_db"
}
```

#### Stock con fallback (si falla WooCommerce)
```json
{
  "success": true,
  "product_id": 82257,
  "stock": {
    "status": "instock",
    "quantity": 15,
    "manage_stock": true,
    "in_stock": true,
    "backorders_allowed": false,
    "available": true
  },
  "source": "local_db_fallback",
  "warning": "Could not fetch real-time stock, using cached data"
}
```

### Campos de la Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `success` | boolean | Indica si la operación fue exitosa |
| `product_id` | integer | ID del producto consultado |
| `stock` | object | Objeto con información de stock |
| `stock.status` | string | Estado del stock (`instock`, `outofstock`, `onbackorder`) |
| `stock.quantity` | integer\|null | Cantidad disponible (null si no maneja stock) |
| `stock.manage_stock` | boolean | Si el producto maneja inventario |
| `stock.in_stock` | boolean | Si hay stock disponible |
| `stock.backorders_allowed` | boolean | Si acepta pedidos pendientes |
| `stock.available` | boolean | Si está disponible para compra |
| `source` | string | Origen de los datos (`woocommerce_realtime`, `local_db`, `local_db_fallback`) |
| `timestamp` | string | Fecha/hora de la consulta (solo en tiempo real) |
| `warning` | string | Mensaje de advertencia (solo en fallback) |

### Interpretación del Stock

#### Casos comunes:
```javascript
// ✅ Producto disponible con stock gestionado
{
  "status": "instock",
  "quantity": 15,
  "manage_stock": true,
  "available": true
}

// ✅ Producto disponible sin gestión de stock
{
  "status": "instock",
  "quantity": null,
  "manage_stock": false,
  "available": true
}

// ❌ Producto sin stock
{
  "status": "outofstock",
  "quantity": 0,
  "manage_stock": true,
  "available": false
}

// ⚠️ Producto en pedidos pendientes
{
  "status": "onbackorder",
  "quantity": 0,
  "manage_stock": true,
  "backorders_allowed": true,
  "available": true
}
```

### Errores Posibles

#### Producto no encontrado (404)
```json
{
  "error": "Producto no encontrado",
  "product_id": 99999
}
```

#### Error interno (500)
```json
{
  "error": "Error interno del servidor",
  "details": "Error message..."
}
```

---

## 3. Lista de Productos

### Endpoint
```
GET /api/products/woocommerce/products/
```

### Descripción
Obtiene una lista paginada de productos con traducciones, precios con margen y stock desde base de datos local.

### Query Parameters
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `category_id` | integer | null | Filtrar por categoría WooCommerce |
| `per_page` | integer | 20 | Productos por página (máx 100) |
| `page` | integer | 1 | Número de página |
| `lang` | string | `es` | Idioma (`es` o `en`) |

### Ejemplo de Request
```bash
# Primera página de 20 productos
GET /api/products/woocommerce/products/

# Productos de una categoría específica
GET /api/products/woocommerce/products/?category_id=134&per_page=10

# Página 2 en inglés
GET /api/products/woocommerce/products/?page=2&lang=en
```

### Respuesta Exitosa (200 OK)

```json
{
  "success": true,
  "message": "Productos obtenidos desde base de datos local",
  "data": [
    {
      "id": 82257,
      "name": "Massage oil Coco Tropical Erotic",
      "slug": "aceite-para-masajes-coco-tropical-erotic",
      "type": "variable",
      "is_variable": true,
      "variations_count": 2,
      "short_description": "",
      "price": 8490.0,
      "regular_price": null,
      "sale_price": null,
      "on_sale": false,
      "image": "https://distrisexcolombia.com/wp-content/uploads/2025/10/Lubricante-sensual-intimo-03.jpg",
      "images": [
        {
          "id": 82280,
          "src": "https://distrisexcolombia.com/wp-content/uploads/2025/10/Lubricante-sensual-intimo-00.jpg",
          "name": "Lubricante sensual intimo 00",
          "alt": "",
          "thumbnail": "https://distrisexcolombia.com/wp-content/uploads/2025/10/Lubricante-sensual-intimo-00-300x300.jpg"
        }
      ],
      "category": "Massage Oils",
      "featured": false,
      "average_rating": 0.0,
      "rating_count": 0
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_products": 1523,
    "total_pages": 77,
    "has_next": true,
    "has_previous": false
  },
  "filters": {
    "category_id": null,
    "language": "en"
  },
  "source": "local_db"
}
```

---

## 4. Variaciones de Producto

### Endpoint
```
GET /api/products/woocommerce/products/{product_id}/variations/
```

### Descripción
Obtiene las variaciones de un producto variable (ej: diferentes colores, tamaños, sabores). **Cada variación tiene su propio stock.**

### Parámetros de URL
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `product_id` | integer | Sí | ID del producto padre en WooCommerce |

### Query Parameters
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `per_page` | integer | 20 | Variaciones por página (máx 100) |
| `page` | integer | 1 | Número de página |

### Ejemplo de Request
```bash
# Obtener todas las variaciones de un producto
GET /api/products/woocommerce/products/20090/variations/

# Paginación
GET /api/products/woocommerce/products/20090/variations/?per_page=10&page=1
```

### Respuesta Exitosa (200 OK)

```json
{
  "success": true,
  "data": [
    {
      "id": 20091,
      "product_id": 20090,
      "permalink": "https://distrisexcolombia.com/producto/...",
      "price": 25000.0,
      "regular_price": 25000.0,
      "sale_price": null,
      "on_sale": false,
      "stock_status": "instock",
      "stock_quantity": 10,
      "manage_stock": true,
      "attributes": {
        "attribute_pa_color": "Rojo",
        "attribute_pa_size": "M"
      },
      "image": "https://distrisexcolombia.com/wp-content/uploads/...",
      "weight": "0.5",
      "dimensions": {
        "length": "10",
        "width": "5",
        "height": "2"
      }
    },
    {
      "id": 20092,
      "product_id": 20090,
      "permalink": "https://distrisexcolombia.com/producto/...",
      "price": 25000.0,
      "regular_price": 25000.0,
      "sale_price": null,
      "on_sale": false,
      "stock_status": "outofstock",
      "stock_quantity": 0,
      "manage_stock": true,
      "attributes": {
        "attribute_pa_color": "Azul",
        "attribute_pa_size": "M"
      },
      "image": "https://distrisexcolombia.com/wp-content/uploads/...",
      "weight": "0.5",
      "dimensions": {
        "length": "10",
        "width": "5",
        "height": "2"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_variations": 4,
    "total_pages": 1
  },
  "source": "local_db"
}
```

### Campos de Variación

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID de la variación |
| `product_id` | integer | ID del producto padre |
| `price` | float | Precio de esta variación |
| `stock_status` | string | Estado del stock (`instock`, `outofstock`) |
| `stock_quantity` | integer | Cantidad disponible de esta variación |
| `manage_stock` | boolean | Si maneja inventario |
| `attributes` | object | Atributos de la variación (color, tamaño, etc) |
| `image` | string | Imagen específica de esta variación |

---

## 4.1. Detalle de Variación Específica

### Endpoint
```
GET /api/products/woocommerce/products/{product_id}/variations/{variation_id}/
```

### Descripción
Obtiene el detalle de UNA variación específica con stock en tiempo real desde WooCommerce.

### Parámetros de URL
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `product_id` | integer | Sí | ID del producto padre en WooCommerce |
| `variation_id` | integer | Sí | ID de la variación específica |

### Query Parameters
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `lang` | string | `es` | Idioma de la respuesta |
| `real_time_stock` | boolean | `true` | Si debe consultar stock real de WooCommerce |

### Ejemplo de Request
```bash
# Obtener variación específica con stock real
GET /api/products/woocommerce/products/82257/variations/82295/

# En inglés
GET /api/products/woocommerce/products/82257/variations/82295/?lang=en

# Con stock local (más rápido)
GET /api/products/woocommerce/products/82257/variations/82295/?real_time_stock=false
```

### Respuesta Exitosa (200 OK)

```json
{
  "success": true,
  "data": {
    "id": 82295,
    "product_id": 82257,
    "permalink": "https://distrisexcolombia.com/producto/...",
    "price": 25000.0,
    "regular_price": 25000.0,
    "sale_price": null,
    "on_sale": false,
    "stock_status": "instock",
    "stock_quantity": 10,
    "manage_stock": true,
    "in_stock": true,
    "attributes": {
      "attribute_pa_color": "Rojo",
      "attribute_pa_size": "M"
    },
    "image": "https://distrisexcolombia.com/wp-content/uploads/...",
    "weight": "0.5",
    "dimensions": {
      "length": "10",
      "width": "5",
      "height": "2"
    },
    "real_time_stock": true
  },
  "language": "en",
  "source": "local_db_with_realtime_stock"
}
```

### Errores Posibles

#### Producto no encontrado (404)
```json
{
  "error": "Producto no encontrado",
  "product_id": 82257
}
```

#### Variación no encontrada (404)
```json
{
  "error": "Variación no encontrada",
  "product_id": 82257,
  "variation_id": 99999
}
```

---

## 5. Productos en Tendencia

### Endpoint
```
GET /api/products/woocommerce/products/trending/
```

### Descripción
Obtiene los 8 productos más populares con mejor rating y más reviews.

### Query Parameters
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `lang` | string | `es` | Idioma (`es` o `en`) |

### Ejemplo de Request
```bash
GET /api/products/woocommerce/products/trending/
GET /api/products/woocommerce/products/trending/?lang=en
```

### Respuesta Exitosa (200 OK)

```json
{
  "success": true,
  "data": [
    {
      "id": 82257,
      "name": "Massage oil Coco Tropical Erotic",
      "slug": "aceite-para-masajes-coco-tropical-erotic",
      "short_description": "",
      "price": 8490.0,
      "regular_price": null,
      "sale_price": null,
      "on_sale": false,
      "image": "https://...",
      "images": [...],
      "category": "Massage Oils",
      "featured": false,
      "average_rating": 4.5,
      "rating_count": 120
    }
  ],
  "count": 8,
  "source": "local_db"
}
```

---

  }
  ```

  ---
### 2. Ver detalle de producto
```javascript
// GET /api/products/woocommerce/products/82257/?lang=en
// Usa stock real automáticamente
```

### 3. Verificar stock antes de agregar al carrito

#### Para productos simples:
```javascript
// GET /api/products/woocommerce/products/82257/stock/
const response = await fetch(`/api/products/woocommerce/products/${productId}/stock/`);
const data = await response.json();

if (data.stock.available && data.stock.quantity >= quantity) {
  // Agregar al carrito
} else {
  // Mostrar error de stock
}
```

#### Para productos variables:
```javascript
// 1. Verificar si es producto variable
const stockResponse = await fetch(`/api/products/woocommerce/products/${productId}/stock/`);
const stockData = await stockResponse.json();

if (stockData.product_type === 'variable') {
  // 2. Obtener variaciones
  const variationsResponse = await fetch(`/api/products/woocommerce/products/${productId}/variations/`);
  const variations = await variationsResponse.json();
  
  // 3. Usuario debe seleccionar una variación
  // Mostrar selector de variaciones
  
  // 4. Verificar stock de la variación seleccionada
  const selectedVariation = variations.data.find(v => v.id === selectedVariationId);
  
  if (selectedVariation.stock_status === 'instock' && selectedVariation.stock_quantity >= quantity) {
    // Agregar al carrito (con variation_id)
  } else {
    // Mostrar error de stock
  }
}
```

### 4. Actualizar stock en tiempo real en la página de detalle
```javascript
// Consultar cada 30 segundos
setInterval(async () => {
  const stock = await fetch(`/api/products/woocommerce/products/${productId}/stock/`);
  updateStockUI(stock.data);
}, 30000);
```

---

## Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | Éxito |
| 400 | Parámetros inválidos |
| 404 | Producto no encontrado |
| 500 | Error interno del servidor |
| 502 | Error conectando con WooCommerce |

---

## Notas Importantes

1. **Productos Variables**: Los productos con variaciones (ej: diferentes colores/tamaños) NO tienen stock directo. Debes consultar el stock de cada variación individual.
2. **Stock en tiempo real**: El endpoint de detalle y stock consultan WooCommerce por defecto para máxima precisión
3. **Traducciones**: Los textos se traducen automáticamente según el idioma solicitado
4. **Precios**: Todos los precios incluyen el margen configurado por categoría
5. **Imágenes**: Se retornan URLs directas a las imágenes de WooCommerce
6. **Fallback**: Si falla la consulta a WooCommerce, se usan datos locales automáticamente
7. **HTML**: Las traducciones NO incluyen etiquetas HTML, solo texto plano

---

## Flujo Completo: Productos Variables

### Paso 1: Obte### En el detalle del producto
```javascript
const response = await fetch(`/api/products/woocommerce/products/${productId}/`);
const product = response.data;

if (product.is_variable) {
  // Construir selectores de atributos
  product.attributes.forEach(attribute => {
    console.log(`Atributo: ${attribute.name}`);
    console.log(`Opciones: ${attribute.options.join(', ')}`);
    
    // Crear selector HTML
    const select = document.createElement('select');
    select.name = attribute.slug;
    
    attribute.options.forEach(option => {
      const optionElement = document.createElement('option');
      optionElement.value = option;
      optionElement.textContent = option;
      select.appendChild(optionElement);
    });
    
    // Agregar al DOM
    document.getElementById('variation-selectors').appendChild(select);
  });
  
  // Cuando el usuario selecciona opciones, buscar la variación correspondiente
  function findMatchingVariation(selectedAttributes) {
    return product.available_variations.find(variation => {
      return Object.keys(selectedAttributes).every(key => 
        variation.attributes[key] === selectedAttributes[key]
      );
    });
  }
  
  // Ejemplo: Usuario seleccionó "Tamaño: 250ML"
  const selected = findMatchingVariation({ "Tamaño": "250ML" });
  console.log(`Variación ID: ${selected.id}`);
  console.log(`Precio: ${selected.price}`);
  console.log(`Stock: ${selected.stock_quantity}`);
  
} else {
  // Producto simple, mostrar "Agregar al carrito" directo
  showAddToCartButton(product);
}
```

### Paso 2: Consultar stock (detecta que es variable)
```javascript
const stock = await fetch(`/api/products/woocommerce/products/${productId}/stock/`);
// stock.product_type === 'variable'
// stock.message === 'Este producto tiene variaciones...'
// stock.variations_endpoint === '/api/products/.../variations/'
```

### Paso 3: Obtener variaciones con stock
```javascript
const variations = await fetch(`/api/products/woocommerce/products/${productId}/variations/`);
const variations = await fetch(`/api/products/woocommerce/products/20090/variations/`);
// variations.data[0].stock_status === 'instock'
// variations.data[0].stock_quantity === 10
// variations.data[0].attributes === { color: 'Rojo', size: 'M' }
```

### Paso 4: Usuario selecciona variación
```javascript
// El frontend muestra selector de atributos (color, tamaño, etc)
const selectedVariation = variations.data.find(v => 
  v.attributes.attribute_pa_color === 'Rojo' &&
  v.attributes.attribute_pa_size === 'M'
);

// Validar stock de la variación
if (selectedVariation.stock_quantity >= requestedQuantity) {
  addToCart(productId, selectedVariation.id, requestedQuantity);
}
```

---

## Ejemplos de Integración Frontend

### React/Next.js
```javascript
// Obtener detalle del producto
const getProductDetail = async (productId, lang = 'es') => {
  const response = await fetch(
    `/api/products/woocommerce/products/${productId}/?lang=${lang}`
  );
  return await response.json();
};

// Verificar stock
const checkStock = async (productId) => {
  const response = await fetch(
    `/api/products/woocommerce/products/${productId}/stock/`
  );
  const data = await response.json();
  return data.stock;
};

// Uso
const product = await getProductDetail(82257, 'en');
const stock = await checkStock(82257);

if (stock.available) {
  console.log(`${stock.quantity} unidades disponibles`);
}
```

### TypeScript Interfaces
```typescript
interface ProductDetail {
  success: boolean;
  data: {
    id: number;
    name: string;
    slug: string;
    type: 'simple' | 'variable' | 'grouped';
    price: number;
    stock_status: 'instock' | 'outofstock' | 'onbackorder';
    stock_quantity: number | null;
    in_stock: boolean;
    images: Array<{
      id: number;
      src: string;
      thumbnail: string;
    }>;
    // ... otros campos
  };
  language: string;
  source: string;
}

interface ProductStock {
  success: boolean;
  product_id: number;
  product_type?: 'variable';  // Solo presente si es producto variable
  message?: string;
  variations_count?: number;
  variations_endpoint?: string;
  stock: {
    status: 'instock' | 'outofstock' | 'onbackorder' | 'variable';
    quantity: number | null;
    manage_stock: boolean;
    in_stock: boolean;
    backorders_allowed: boolean;
    available: boolean;
    requires_variation_selection?: boolean;
  };
  source: string;
}

interface ProductVariation {
  id: number;
  product_id: number;
  permalink: string;
  price: number;
  regular_price: number | null;
  sale_price: number | null;
  on_sale: boolean;
  stock_status: 'instock' | 'outofstock' | 'onbackorder';
  stock_quantity: number;
  manage_stock: boolean;
  attributes: Record<string, string>;
  image: string | null;
  weight: string;
  dimensions: {
    length: string;
    width: string;
    height: string;
  };
}

interface VariationsResponse {
  success: boolean;
  data: ProductVariation[];
  pagination: {
    page: number;
    per_page: number;
    total_variations: number;
    total_pages: number;
  };
  source: string;
}
```

---

¡Listo! 🚀 Ahora tienes toda la documentación para integrar los endpoints en el frontend.
