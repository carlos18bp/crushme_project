# Endpoint de Productos en Tendencia

## 📌 Descripción General

Este endpoint retorna los **8 productos más populares** (tops o en tendencia) desde WooCommerce, ordenados por un algoritmo de popularidad que combina ventas, calificaciones y número de reseñas.

---

## 🔗 Información del Endpoint

| Campo | Valor |
|-------|-------|
| **URL** | `/api/products/woocommerce/products/trending/` |
| **Método** | `GET` |
| **Autenticación** | No requiere (Público) |
| **Cache** | Sí (1 hora, heredado de WooCommerce) |

---

## 📊 Características

✅ **Retorna 8 productos tops**  
✅ **Ordenados por popularidad** (ventas + rating + reseñas)  
✅ **Solo productos con stock disponible**  
✅ **Misma estructura que productos por categoría** (incluye atributos, variaciones, imágenes, etc.)  
✅ **Cache automático de 1 hora**  
✅ **Endpoint público** (no requiere autenticación)

---

## 🎯 Algoritmo de Popularidad

El endpoint ordena los productos usando la siguiente fórmula:

```
Popularidad = (total_sales × 10) + (average_rating × 5) + rating_count
```

**Donde:**
- `total_sales`: Número total de ventas del producto
- `average_rating`: Calificación promedio (0-5 estrellas)
- `rating_count`: Número de reseñas/opiniones

**Filtros aplicados:**
- ✅ Solo productos con `stock_status: "instock"`
- ✅ Solo productos con `stock_quantity > 0`

---

## 📥 Petición

### Ejemplo usando cURL

```bash
curl -X GET http://localhost:8000/api/products/woocommerce/products/trending/
```

### Ejemplo usando JavaScript (Fetch API)

```javascript
async function getTrendingProducts() {
  try {
    const response = await fetch('/api/products/woocommerce/products/trending/');
    const data = await response.json();
    
    if (data.success) {
      console.log('Productos en tendencia:', data.data);
      return data.data;
    } else {
      console.error('Error:', data.error);
    }
  } catch (error) {
    console.error('Error en la petición:', error);
  }
}
```

### Ejemplo usando Axios

```javascript
import axios from 'axios';

const getTrendingProducts = async () => {
  try {
    const { data } = await axios.get('/api/products/woocommerce/products/trending/');
    
    if (data.success) {
      return data.data;
    }
  } catch (error) {
    console.error('Error:', error);
  }
};
```

---

## 📤 Respuesta Exitosa (200 OK)

### Estructura de Respuesta

```json
{
  "success": true,
  "message": "8 productos en tendencia obtenidos exitosamente",
  "data": [...],  // Array de 8 productos (ver estructura abajo)
  "total_products": 8,
  "api_info": {
    "status_code": 200,
    "source": "woocommerce",
    "cached": false
  }
}
```

### Ejemplo Completo de Respuesta

```json
{
  "success": true,
  "message": "8 productos en tendencia obtenidos exitosamente",
  "total_products": 8,
  "data": [
    {
      "id": 19300,
      "name": "Lubricante Íntimo Caliente Licor Lush",
      "slug": "lubricante-intimo-caliente-licor-lush",
      "permalink": "https://desarrollo.distrisex.com/producto/lubricante-intimo-caliente-licor-lush/",
      "type": "variable",
      "status": "publish",
      "featured": false,
      "sku": "LUB-LICOR-LUSH",
      
      "price": "15000",
      "regular_price": "15000",
      "sale_price": "",
      "on_sale": false,
      
      "total_sales": 145,
      "average_rating": "4.8",
      "rating_count": 23,
      
      "stock_status": "instock",
      "stock_quantity": 100,
      "manage_stock": true,
      "backorders": "no",
      
      "description": "<p>Descripción completa del producto...</p>",
      "short_description": "<p>Descripción corta...</p>",
      
      "attributes": [
        {
          "id": 0,
          "name": "Tamaño",
          "slug": "Tamaño",
          "visible": false,
          "variation": true,
          "options": ["Sachet", "39 ML"]
        },
        {
          "id": 0,
          "name": "Sabor",
          "slug": "Sabor",
          "visible": false,
          "variation": true,
          "options": ["Anís", "Baileys", "Mojito", "Ron", "Tequila"]
        },
        {
          "id": 0,
          "name": "Marca",
          "slug": "Marca",
          "visible": true,
          "variation": false,
          "options": ["Erotic"]
        }
      ],
      
      "variations": [19301, 19303, 19304, 19305, 19306, 19307, 19308, 19309, 19310, 19311],
      "has_options": true,
      
      "images": [
        {
          "id": 15234,
          "src": "https://desarrollo.distrisex.com/wp-content/uploads/2023/08/lubricante-licor.jpg",
          "name": "lubricante-licor",
          "alt": "Lubricante Íntimo Caliente Licor",
          "position": 0
        }
      ],
      
      "categories": [
        {
          "id": 45,
          "name": "Lubricantes",
          "slug": "lubricantes"
        }
      ],
      
      "tags": [
        {
          "id": 123,
          "name": "Lubricante",
          "slug": "lubricante"
        }
      ],
      
      "weight": "50",
      "dimensions": {
        "length": "10",
        "width": "5",
        "height": "12"
      }
    },
    {
      "id": 19301,
      "name": "Preservativos Ultra Sensibles Premium Pack",
      "type": "simple",
      "price": "8000",
      "total_sales": 230,
      "average_rating": "4.7",
      "rating_count": 45,
      "stock_status": "instock",
      "stock_quantity": 200,
      "attributes": [],
      "variations": [],
      "has_options": false,
      "images": [...]
    }
    // ... 6 productos más
  ],
  "api_info": {
    "status_code": 200,
    "source": "woocommerce",
    "cached": false
  }
}
```

---

## 📋 Campos de Cada Producto

Cada producto en el array `data` contiene **todos los campos de WooCommerce**, incluyendo:

### Campos Básicos
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | int | ID del producto en WooCommerce |
| `name` | string | Nombre del producto |
| `slug` | string | Slug para URL |
| `permalink` | string | URL completa del producto |
| `type` | string | Tipo: "simple", "variable", "grouped", "external" |
| `status` | string | Estado: "publish", "draft", etc. |
| `sku` | string | Código SKU |

### Precios
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `price` | string | Precio actual |
| `regular_price` | string | Precio regular |
| `sale_price` | string | Precio de oferta |
| `on_sale` | boolean | Si está en oferta |

### Popularidad (usados para ordenar)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `total_sales` | int | Total de ventas |
| `average_rating` | string | Calificación promedio (0-5) |
| `rating_count` | int | Número de reseñas |

### Stock
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `stock_status` | string | "instock", "outofstock", "onbackorder" |
| `stock_quantity` | int | Cantidad disponible |
| `manage_stock` | boolean | Si gestiona stock |

### Atributos y Variaciones
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `attributes` | array | Atributos del producto (ver [guía de atributos](woocommerce_product_attributes.md)) |
| `variations` | array | IDs de variaciones disponibles |
| `has_options` | boolean | Si tiene opciones seleccionables |

### Multimedia
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `images` | array | Imágenes del producto |
| `description` | string | Descripción larga (HTML) |
| `short_description` | string | Descripción corta (HTML) |

### Taxonomía
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `categories` | array | Categorías del producto |
| `tags` | array | Etiquetas del producto |

---

## ❌ Respuestas de Error

### Error 502 - Bad Gateway (Fallo en WooCommerce)

```json
{
  "success": false,
  "error": "API returned status 401",
  "status_code": 401,
  "details": "{...}"
}
```

**Causas comunes:**
- Credenciales de WooCommerce incorrectas
- API de WooCommerce no disponible
- Timeout de conexión

### Error 500 - Error Interno del Servidor

```json
{
  "error": "Error interno del servidor",
  "details": "Error message here"
}
```

**Causas comunes:**
- Error en el procesamiento de datos
- Problema con el formato de respuesta de WooCommerce

---

## 🔍 Comparación con Otros Endpoints

### vs. Productos por Categoría

| Característica | Trending Products | Productos por Categoría |
|----------------|:-----------------:|:-----------------------:|
| **Número de productos** | Fijo: 8 | Configurable (max 100) |
| **Ordenamiento** | Por popularidad | Por fecha de creación |
| **Filtrado** | Solo con stock | Todos los publicados |
| **Categoría** | Todas | Una específica |
| **Estructura** | ✅ Idéntica | ✅ Idéntica |
| **Atributos** | ✅ Incluidos | ✅ Incluidos |
| **Variaciones** | ✅ Incluidas | ✅ Incluidas |

### vs. Featured Products (Django Local)

| Característica | Trending (WooCommerce) | Featured (Django Local) |
|----------------|:----------------------:|:-----------------------:|
| **Fuente de datos** | WooCommerce API | Base de datos local |
| **Atributos** | ✅ Sí | ❌ No |
| **Variaciones** | ✅ Sí | ❌ No |
| **Número de productos** | 8 | 12 |
| **Criterio** | Ventas + Rating | Más recientes |

---

## 💡 Casos de Uso

### 1. Página de Inicio - Sección de Productos Populares

```javascript
import React, { useEffect, useState } from 'react';

function TrendingProductsSection() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/products/woocommerce/products/trending/')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setProducts(data.data);
        }
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Cargando productos populares...</div>;

  return (
    <section className="trending-products">
      <h2>🔥 Productos en Tendencia</h2>
      <div className="products-grid">
        {products.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  );
}
```

### 2. Carrusel de Productos Tops

```javascript
function TrendingCarousel() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch('/api/products/woocommerce/products/trending/')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setProducts(data.data);
        }
      });
  }, []);

  return (
    <div className="carousel">
      {products.map((product, index) => (
        <div key={product.id} className="carousel-item">
          <img src={product.images[0]?.src} alt={product.name} />
          <h3>{product.name}</h3>
          <p className="price">${product.price}</p>
          <div className="rating">
            ⭐ {product.average_rating} ({product.rating_count} reseñas)
          </div>
          <span className="badge">🔥 {product.total_sales} vendidos</span>
        </div>
      ))}
    </div>
  );
}
```

### 3. Widget de "Más Vendidos"

```javascript
function BestSellersWidget() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch('/api/products/woocommerce/products/trending/')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          // Tomar solo los 4 primeros
          setProducts(data.data.slice(0, 4));
        }
      });
  }, []);

  return (
    <aside className="widget">
      <h3>🏆 Los Más Vendidos</h3>
      <ul>
        {products.map((product, index) => (
          <li key={product.id}>
            <span className="rank">#{index + 1}</span>
            <img src={product.images[0]?.src} alt="" />
            <div>
              <h4>{product.name}</h4>
              <p>${product.price}</p>
            </div>
          </li>
        ))}
      </ul>
    </aside>
  );
}
```

---

## ⚙️ Configuración Técnica

### Cache

El endpoint hereda el sistema de caché de WooCommerce:
- **Duración:** 1 hora (3600 segundos)
- **Clave de caché:** `woocommerce_products_all_50_1`
- **Limpiar caché:** `POST /api/products/woocommerce/cache/clear/`

### Performance

- **Productos consultados:** 50 (para tener suficiente pool de donde elegir)
- **Productos retornados:** 8 (los más populares)
- **Tiempo de respuesta:** ~200ms (con caché) / ~1.5s (sin caché)

### Límites

- **Productos mínimos:** Puede retornar menos de 8 si hay pocos productos con stock
- **Productos máximos:** Siempre máximo 8
- **Stock:** Solo productos con stock disponible

---

## 🎨 Ejemplo de Implementación Completa

```javascript
// hooks/useTrendingProducts.js
import { useState, useEffect } from 'react';

export function useTrendingProducts() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTrending = async () => {
      try {
        const response = await fetch('/api/products/woocommerce/products/trending/');
        const data = await response.json();
        
        if (data.success) {
          setProducts(data.data);
        } else {
          setError(data.error);
        }
      } catch (err) {
        setError('Error al cargar productos');
      } finally {
        setLoading(false);
      }
    };

    fetchTrending();
  }, []);

  return { products, loading, error };
}

// components/TrendingProducts.jsx
import { useTrendingProducts } from '../hooks/useTrendingProducts';

function TrendingProducts() {
  const { products, loading, error } = useTrendingProducts();

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <section className="trending-products">
      <div className="section-header">
        <h2>🔥 Productos en Tendencia</h2>
        <p>Los más populares de nuestra tienda</p>
      </div>
      
      <div className="products-grid">
        {products.map(product => (
          <ProductCard 
            key={product.id}
            product={product}
            showBadge={true}
            badge={`${product.total_sales} vendidos`}
          />
        ))}
      </div>
    </section>
  );
}
```

---

## 📚 Documentación Relacionada

- [Atributos de Productos WooCommerce](woocommerce_product_attributes.md) - Guía sobre cómo usar el campo `attributes`
- [Productos por Categoría](product_detail_endpoints.md#2-productos-por-categoría-woocommerce) - Endpoint similar
- [Sistema de Reviews](review_endpoints.md) - Para mostrar reseñas de estos productos

---

## 🔄 Actualizaciones y Versiones

| Fecha | Versión | Cambios |
|-------|---------|---------|
| Oct 2025 | 1.0.0 | Versión inicial del endpoint |

---

## ❓ FAQ (Preguntas Frecuentes)

### ¿Cada cuánto se actualiza la lista de trending?

El endpoint usa caché de 1 hora, así que los productos en tendencia se actualizan cada hora. Puedes limpiar el caché manualmente si necesitas una actualización inmediata.

### ¿Por qué a veces retorna menos de 8 productos?

Si hay menos de 8 productos con stock disponible en el catálogo, retornará todos los disponibles. Es raro en producción pero puede pasar en desarrollo.

### ¿Puedo cambiar el número de productos retornados?

Actualmente está fijo en 8. Si necesitas un número diferente, puedes usar el endpoint de productos por categoría con paginación.

### ¿Los productos incluyen variaciones?

Sí, cada producto incluye el array `variations` con los IDs de sus variaciones (si las tiene). Necesitarás hacer peticiones adicionales para obtener detalles de cada variación.

### ¿Funciona sin autenticación?

Sí, es un endpoint público. No requiere autenticación ni tokens.

### ¿Qué pasa si WooCommerce está caído?

Retornará un error 502 (Bad Gateway) con detalles del error. El frontend debe manejar este caso mostrando un mensaje al usuario.

---

**Última actualización:** Octubre 2025  
**Mantenido por:** Equipo Backend CrushMe


