# API Endpoints: Sistema de Productos Favoritos

## Información General

Sistema completo de Productos Favoritos para usuarios autenticados. Permite a los usuarios guardar productos individuales de WooCommerce como favoritos para acceder rápidamente a ellos después.

**🚀 Características Principales:**
- ✅ Agregar productos de WooCommerce a favoritos por ID
- ✅ Eliminar productos de favoritos
- ✅ Listar todos los productos favoritos con información actualizada
- ✅ **Carga automática de datos**: Al consultar favoritos, automáticamente obtiene y actualiza la información de productos desde WooCommerce
- ✅ Caché inteligente de información de productos (actualización automática cada 24 horas)
- ✅ Verificar si un producto está en favoritos
- ✅ Obtener solo los IDs de productos favoritos (útil para el frontend)

---

## 🎯 Carga Automática de Productos

### Cómo Funciona

Cuando consultas tus productos favoritos:

```
1. Frontend hace request: GET /api/favorites/products/
2. Backend:
   - Busca favoritos del usuario en BD
   - Encuentra productos: [123, 456, 789]
   - Verifica si el caché está desactualizado (>24h)
   - Consulta WooCommerce por productos con caché viejo
   - Actualiza caché con info fresca
   - Devuelve todos los favoritos con datos completos
3. Frontend recibe TODO en una respuesta:
   - Lista completa de favoritos
   - Info completa de CADA producto
   - Precios actualizados
   - Stock disponible
   - Imágenes
```

### Ventajas

- 🚀 **Un solo request** - No necesitas hacer múltiples llamadas
- 💰 **Precios actualizados** - Siempre muestra precio actual de WooCommerce
- 📦 **Stock real** - Sabe si hay disponibilidad
- 🖼️ **Imágenes actualizadas** - Si cambia imagen en WooCommerce, se refleja
- ⚡ **Caché inteligente** - Solo actualiza cuando es necesario (cada 24h)
- 🎯 **Simple** - Frontend no necesita lógica compleja

---

## Endpoints Disponibles

### 1. Gestión de Favoritos

```
POST   /api/favorites/products/add/              - Agregar producto a favoritos
DELETE /api/favorites/products/{product_id}/     - Eliminar producto de favoritos
GET    /api/favorites/products/                  - Listar mis productos favoritos (🚀 con datos completos)
```

### 2. Consultas y Verificación

```
GET /api/favorites/products/ids/                           - Obtener solo los IDs de productos favoritos
GET /api/favorites/products/{product_id}/status/           - Verificar si un producto está en favoritos
```

### 3. Operaciones Masivas

```
POST   /api/favorites/products/refresh/         - Forzar actualización de todos los productos
DELETE /api/favorites/products/clear/           - Eliminar todos los favoritos
```

---

## Autenticación

✅ **Requerida** - Token JWT Bearer para todos los endpoints

```
Authorization: Bearer <token>
```

---

## Ejemplos de Uso

### 1. Agregar Producto a Favoritos

**Request:**
```http
POST /api/favorites/products/add/
Authorization: Bearer <token>
Content-Type: application/json

{
  "woocommerce_product_id": 123
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Producto agregado a favoritos exitosamente",
  "data": {
    "id": 1,
    "user_email": "usuario@ejemplo.com",
    "user_username": "usuario123",
    "woocommerce_product_id": 123,
    "product_data": {
      "id": 123,
      "name": "Producto Ejemplo",
      "price": "29.99",
      "regular_price": "39.99",
      "sale_price": "29.99",
      "stock_status": "instock",
      "images": [
        {
          "src": "https://ejemplo.com/imagen.jpg",
          "alt": "Producto Ejemplo"
        }
      ],
      "slug": "producto-ejemplo",
      "permalink": "https://ejemplo.com/producto-ejemplo"
    },
    "cache_updated_at": "2025-10-03T14:30:00Z",
    "created_at": "2025-10-03T14:30:00Z",
    "updated_at": "2025-10-03T14:30:00Z"
  }
}
```

**Posibles Errores:**
- `400 Bad Request` - Producto ya está en favoritos
- `502 Bad Gateway` - No se pudo obtener info de WooCommerce
- `400 Bad Request` - ID de producto inválido

---

### 2. Listar Productos Favoritos

**Request:**
```http
GET /api/favorites/products/
Authorization: Bearer <token>
```

**Request con Actualización Forzada:**
```http
GET /api/favorites/products/?refresh=true
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Favoritos obtenidos exitosamente",
  "data": [
    {
      "id": 1,
      "woocommerce_product_id": 123,
      "product_name": "Producto Ejemplo 1",
      "product_price": "29.99",
      "product_image": "https://ejemplo.com/imagen1.jpg",
      "product_slug": "producto-ejemplo-1",
      "is_in_stock": true,
      "created_at": "2025-10-03T14:30:00Z"
    },
    {
      "id": 2,
      "woocommerce_product_id": 456,
      "product_name": "Producto Ejemplo 2",
      "product_price": "49.99",
      "product_image": "https://ejemplo.com/imagen2.jpg",
      "product_slug": "producto-ejemplo-2",
      "is_in_stock": false,
      "created_at": "2025-10-02T10:15:00Z"
    }
  ],
  "meta": {
    "total_favorites": 2,
    "products_refreshed": 0
  }
}
```

**Notas:**
- Por defecto solo actualiza productos con caché >24h
- Usa `?refresh=true` para forzar actualización de todos
- `products_refreshed` indica cuántos se actualizaron desde WooCommerce

---

### 3. Eliminar Producto de Favoritos

**Request:**
```http
DELETE /api/favorites/products/123/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Producto eliminado de favoritos exitosamente"
}
```

**Error (404 Not Found):**
```json
{
  "success": false,
  "error": "El producto no está en tus favoritos"
}
```

---

### 4. Verificar si Producto está en Favoritos

**Request:**
```http
GET /api/favorites/products/123/status/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "is_favorited": true,
  "woocommerce_product_id": 123
}
```

**Uso típico:**
```javascript
// En el frontend, al mostrar un producto
const checkFavoriteStatus = async (productId) => {
  const response = await fetch(`/api/favorites/products/${productId}/status/`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  const data = await response.json();
  return data.is_favorited; // true o false
};
```

---

### 5. Obtener Solo IDs de Productos Favoritos

**Request:**
```http
GET /api/favorites/products/ids/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "product_ids": [123, 456, 789, 1011],
  "count": 4
}
```

**Uso típico:**
```javascript
// Útil para marcar múltiples productos como favoritos en una lista
const favoriteIds = await getFavoriteIds();
// [123, 456, 789, 1011]

products.forEach(product => {
  product.isFavorite = favoriteIds.includes(product.id);
});
```

---

### 6. Actualizar Todos los Favoritos

**Request:**
```http
POST /api/favorites/products/refresh/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Productos actualizados",
  "stats": {
    "total": 10,
    "updated": 10,
    "errors": 0
  },
  "errors": null
}
```

**Con Errores:**
```json
{
  "success": true,
  "message": "Productos actualizados",
  "stats": {
    "total": 10,
    "updated": 8,
    "errors": 2
  },
  "errors": [
    {
      "product_id": 999,
      "error": "Product not found"
    },
    {
      "product_id": 888,
      "error": "Connection timeout"
    }
  ]
}
```

---

### 7. Eliminar Todos los Favoritos

**Request:**
```http
DELETE /api/favorites/products/clear/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "10 productos eliminados de favoritos"
}
```

---

## Flujo de Trabajo Típico del Frontend

### Escenario 1: Agregar a Favoritos desde Página de Producto

```javascript
// Usuario hace clic en botón de favorito
const addToFavorites = async (productId) => {
  try {
    const response = await fetch('/api/favorites/products/add/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        woocommerce_product_id: productId
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Actualizar UI: mostrar corazón lleno
      updateFavoriteButton(true);
      showToast('Producto agregado a favoritos ✓');
    } else {
      // Ya está en favoritos o error
      showToast(data.error);
    }
  } catch (error) {
    console.error('Error adding to favorites:', error);
    showToast('Error al agregar a favoritos');
  }
};
```

### Escenario 2: Mostrar Lista de Favoritos

```javascript
// Página de favoritos del usuario
const loadFavorites = async () => {
  try {
    const response = await fetch('/api/favorites/products/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Renderizar productos con toda su información
      renderFavoriteProducts(data.data);
      
      // Mostrar mensaje si hay productos sin stock
      const outOfStock = data.data.filter(p => !p.is_in_stock);
      if (outOfStock.length > 0) {
        showNotification(`${outOfStock.length} productos sin stock`);
      }
    }
  } catch (error) {
    console.error('Error loading favorites:', error);
  }
};
```

### Escenario 3: Marcar Favoritos en Catálogo

```javascript
// Al cargar catálogo de productos
const loadProductCatalog = async () => {
  // 1. Cargar productos de WooCommerce
  const products = await fetchWooCommerceProducts();
  
  // 2. Obtener IDs de favoritos (rápido, solo IDs)
  const favResponse = await fetch('/api/favorites/products/ids/', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const favData = await favResponse.json();
  const favoriteIds = favData.product_ids;
  
  // 3. Marcar productos como favoritos
  products.forEach(product => {
    product.isFavorited = favoriteIds.includes(product.id);
  });
  
  // 4. Renderizar catálogo con indicadores de favoritos
  renderProductGrid(products);
};
```

---

## Modelo de Datos

### FavoriteProduct

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | ID único del favorito |
| `user` | ForeignKey | Usuario dueño del favorito |
| `woocommerce_product_id` | Integer | ID del producto en WooCommerce |
| `product_data` | JSONField | Caché de datos del producto desde WooCommerce |
| `cache_updated_at` | DateTime | Última actualización del caché |
| `created_at` | DateTime | Fecha de creación del favorito |
| `updated_at` | DateTime | Última actualización del registro |

**Restricciones:**
- `unique_together`: Un usuario no puede tener el mismo producto duplicado en favoritos
- Índices en: `user`, `woocommerce_product_id`, `created_at`

---

## Caché de Productos

### Estrategia de Caché

1. **Primera vez**: Al agregar a favoritos, se obtiene y guarda info de WooCommerce
2. **Consultas**: Si el caché tiene <24h, usa datos guardados (rápido)
3. **Actualización automática**: Si caché >24h, refresca automáticamente
4. **Forzar actualización**: Usar `?refresh=true` o endpoint `/refresh/`

### Datos Cacheados

```json
{
  "id": 123,
  "name": "Nombre del Producto",
  "slug": "nombre-del-producto",
  "permalink": "https://tienda.com/producto",
  "price": "29.99",
  "regular_price": "39.99",
  "sale_price": "29.99",
  "stock_status": "instock",
  "stock_quantity": 50,
  "images": [
    {
      "id": 456,
      "src": "https://tienda.com/imagen.jpg",
      "alt": "Producto"
    }
  ],
  "categories": [...],
  "attributes": [...],
  "description": "...",
  "short_description": "..."
}
```

---

## Mejores Prácticas

### 1. Verificación de Favoritos en Listados

✅ **Recomendado:**
```javascript
// Una sola petición para todos los IDs
const favoriteIds = await getFavoriteIds();
products.forEach(p => p.isFavorited = favoriteIds.includes(p.id));
```

❌ **No recomendado:**
```javascript
// Múltiples peticiones (lento)
for (const product of products) {
  product.isFavorited = await checkIfFavorited(product.id);
}
```

### 2. Actualización del UI

```javascript
// Actualizar UI inmediatamente después de agregar/eliminar
const toggleFavorite = async (productId, isFavorited) => {
  if (isFavorited) {
    await removeFavorite(productId);
    updateUI(productId, false);
  } else {
    await addFavorite(productId);
    updateUI(productId, true);
  }
};
```

### 3. Manejo de Errores

```javascript
try {
  await addToFavorites(productId);
} catch (error) {
  if (error.status === 401) {
    // Usuario no autenticado, redirigir a login
    redirectToLogin();
  } else if (error.status === 502) {
    // Error de WooCommerce, mostrar mensaje amigable
    showError('Producto temporalmente no disponible');
  }
}
```

---

## Diferencias con Wishlists

| Característica | Favoritos | Wishlists |
|----------------|-----------|-----------|
| **Propósito** | Lista personal simple de productos favoritos | Listas organizadas con nombre, descripción, compartibles |
| **Visibilidad** | Siempre privados | Pueden ser públicas o privadas |
| **Organización** | Una sola lista plana | Múltiples listas con categorización |
| **Compartir** | No | Sí, con URL personalizada |
| **Metadatos** | Solo producto | Notas, prioridades, info de envío |
| **Uso** | Quick access, marcadores | Gift registries, planificación de compras |

---

## Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| `200 OK` | Operación exitosa |
| `201 Created` | Favorito creado exitosamente |
| `400 Bad Request` | Datos inválidos o producto ya favorito |
| `401 Unauthorized` | No autenticado |
| `404 Not Found` | Producto no está en favoritos |
| `500 Internal Server Error` | Error del servidor |
| `502 Bad Gateway` | Error al conectar con WooCommerce |

---

## Preguntas Frecuentes

**Q: ¿Cuál es el límite de productos favoritos?**  
A: No hay límite definido, pero se recomienda mantener una cantidad razonable (<1000) para mejor rendimiento.

**Q: ¿Qué pasa si un producto es eliminado de WooCommerce?**  
A: El favorito se mantiene pero la actualización del caché fallará. El producto se mostrará con la última información cacheada.

**Q: ¿Puedo agregar productos sin autenticarme?**  
A: No, todos los endpoints requieren autenticación. Los favoritos son personales de cada usuario.

**Q: ¿Cómo optimizar para muchos favoritos?**  
A: Usa el endpoint `/ids/` para verificaciones masivas y carga la página de favoritos con paginación si es necesario.

**Q: ¿Los favoritos se sincronizan entre dispositivos?**  
A: Sí, los favoritos están asociados al usuario, no al dispositivo. Se sincronizan automáticamente.

---

## Soporte y Contacto

Para reportar bugs o solicitar features, contacta al equipo de desarrollo.


