# API Endpoints: Sistema de Wishlists

## Información General

Sistema completo de Wishlists (Listas de Deseos) para usuarios autenticados. Permite crear, gestionar y compartir listas de productos de WooCommerce. Las wishlists pueden ser públicas o privadas y se comparten mediante URLs amigables del formato `/@username/{id}`.

**🚀 Actualización Importante:** Todos los endpoints de consulta de wishlists ahora **cargan automáticamente** la información actualizada de productos desde WooCommerce. No necesitas hacer requests adicionales para obtener los datos de productos.

---

## Características Principales

- ✅ Crear wishlists vacías o con productos
- ✅ Agregar/eliminar productos de WooCommerce por ID
- ✅ **Carga automática de productos**: Al consultar una wishlist, automáticamente obtiene y actualiza la información de productos desde WooCommerce
- ✅ Compartir wishlists públicas con URL personalizada: `/@username/{id}`
- ✅ Sistema de favoritos (seguir wishlists de otros usuarios)
- ✅ Caché inteligente de información de productos con actualización automática
- ✅ Información de envío opcional
- ✅ Prioridades y notas por producto
- ✅ URLs dinámicas según entorno (desarrollo/producción)
- ✅ **Un solo request**: No necesitas consultar productos por separado, todo viene incluido

---

## 🎯 Carga Automática de Productos

### Cómo Funciona

Cuando consultas una wishlist:

```
1. Frontend hace request: GET /api/wishlists/@username/5/
2. Backend:
   - Busca la wishlist en BD
   - Encuentra productos: [123, 456, 789]
   - Consulta WooCommerce por cada producto
   - Actualiza caché con info fresca
   - Devuelve wishlist completa
3. Frontend recibe TODO en una respuesta:
   - Info de wishlist
   - Info completa de CADA producto
   - Precios actualizados
   - Stock disponible
   - Imágenes
```

### Ventajas

- 🚀 **1 request en vez de 2+** - Más rápido y simple
- 💰 **Precios actualizados** - Siempre muestra precio actual de WooCommerce
- 📦 **Stock real** - Sabe si hay disponibilidad
- 🖼️ **Imágenes actualizadas** - Si cambia imagen en WooCommerce, se refleja
- 🎯 **Transparente** - Frontend no necesita lógica compleja

---

## Configuración de Entorno

```python
# settings.py
PRODUCTION = False  # Cambiar a True en producción

# URLs se ajustan automáticamente:
# Desarrollo: http://localhost:5173/@username/5
# Producción: https://crushme.com.co/@username/5
```

---

## Endpoints Disponibles

### 1. Gestión de Wishlists
```
GET    /api/wishlists/                      - Listar mis wishlists
POST   /api/wishlists/create/               - Crear nueva wishlist
GET    /api/wishlists/{id}/                 - Ver wishlist (🚀 con productos)
PUT    /api/wishlists/{id}/update/          - Actualizar wishlist
DELETE /api/wishlists/{id}/delete/          - Eliminar wishlist
```

### 2. Productos WooCommerce
```
POST   /api/wishlists/{id}/add-woocommerce-product/     - Agregar producto
DELETE /api/wishlists/{id}/remove-woocommerce-product/{product_id}/  - Remover producto
POST   /api/wishlists/{id}/refresh-products/            - Forzar refresco (opcional)
```

### 3. Compartir y Ver Públicas
```
GET /api/wishlists/user/{username}/         - Listar wishlists públicas de un usuario
GET /api/wishlists/@{username}/{id}/        - Ver wishlist pública (🚀 con productos)
GET /api/wishlists/public/{uuid}/           - Ver wishlist por UUID (🚀 con productos)
GET /api/wishlists/public/                  - Listar todas las wishlists públicas
```

### 4. Sistema de Favoritos
```
POST   /api/wishlists/{id}/favorite/        - Marcar como favorita
DELETE /api/wishlists/{id}/unfavorite/      - Quitar de favoritas
GET    /api/wishlists/favorites/            - Listar mis favoritas
```

### 5. Información de Envío
```
PATCH /api/wishlists/{id}/shipping/         - Actualizar info de envío
```

---

## Autenticación

✅ **Requerida** para la mayoría de endpoints - Token JWT Bearer

```
Authorization: Bearer <token>
```

❌ **No requerida** para ver wishlists públicas

---

## Ejemplos de Respuesta con Productos

### Wishlist Completa (con productos actualizados)

```json
{
  "wishlist": {
    "id": 5,
    "name": "Regalos de Navidad 2025",
    "description": "Lista de regalos que quiero recibir",
    "user_username": "juanperez",
    "public_url": "http://localhost:5173/@juanperez/5",
    "shareable_path": "/@juanperez/5",
    "items": [
      {
        "id": 10,
        "woocommerce_product_id": 123,
        "product_name": "Secret Egg Vibrator",
        "product_price": 39.99,
        "product_image": "https://ejemplo.com/imagen.jpg",
        "product_info": {
          "id": 123,
          "name": "Secret Egg Vibrator",
          "price": "39.99",
          "regular_price": "49.99",
          "sale_price": "39.99",
          "stock_status": "instock",
          "stock_quantity": 50,
          "images": [
            {"src": "https://ejemplo.com/imagen.jpg"}
          ],
          "categories": [...],
          "average_rating": "4.5"
        },
        "notes": "My naughty little secret... hidden but oh so irresistible 💕",
        "priority": "high",
        "is_available": true,
        "created_at": "2025-10-02T20:35:00Z"
      }
    ],
    "total_items": 1,
    "total_value": 39.99,
    "is_favorited": false,
    "favorites_count": 0
  }
}
```

**Nota:** El campo `product_info` contiene información **actualizada en tiempo real** desde WooCommerce cada vez que consultas la wishlist.

---

## Ejemplos de Código

### React Component - Mostrar Wishlist Pública

```tsx
import { useState, useEffect } from 'react';

function WishlistPage({ username, id }) {
  const [wishlist, setWishlist] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function loadWishlist() {
      // ✅ UN SOLO REQUEST - Ya viene con toda la info de productos
      const res = await fetch(`/api/wishlists/@${username}/${id}/`);
      const data = await res.json();
      
      setWishlist(data.wishlist);
      setLoading(false);
    }
    
    loadWishlist();
  }, [username, id]);
  
  if (loading) return <div>Cargando...</div>;
  
  return (
    <div className="wishlist">
      <h1>{wishlist.name}</h1>
      <p>{wishlist.description}</p>
      
      {/* Mostrar productos - toda la info ya está aquí */}
      <div className="products-grid">
        {wishlist.items.map(item => (
          <div key={item.id} className="product-card">
            <img src={item.product_image} alt={item.product_name} />
            <h3>{item.product_name}</h3>
            <p className="price">${item.product_price}</p>
            <p className="stock">
              {item.is_available ? '✅ En stock' : '❌ Agotado'}
            </p>
            {item.notes && <p className="notes">{item.notes}</p>}
            <button>Comprar ahora</button>
          </div>
        ))}
      </div>
      
      <button onClick={() => navigator.clipboard.writeText(wishlist.public_url)}>
        📋 Copiar Link
      </button>
    </div>
  );
}
```

### JavaScript - Ver Wishlist Pública (Simple)

```javascript
// ✅ UN SOLO REQUEST - Todo incluido
async function viewWishlist(username, wishlistId) {
  const response = await fetch(`/api/wishlists/@${username}/${wishlistId}/`);
  const { wishlist } = await response.json();
  
  console.log(`📋 ${wishlist.name}`);
  console.log(`💰 Total: $${wishlist.total_value}`);
  console.log(`🔗 ${wishlist.public_url}`);
  
  // Ya tiene toda la info de productos
  wishlist.items.forEach(item => {
    console.log(`
      🎁 ${item.product_name}
      💵 $${item.product_price}
      📦 ${item.is_available ? 'En stock' : 'Agotado'}
      🖼️ ${item.product_image}
      📝 ${item.notes || 'Sin notas'}
    `);
  });
}

// Uso
viewWishlist('juanperez', 5);
```

### JavaScript - Listar Wishlists de un Usuario

```javascript
// 🎯 Obtener todas las wishlists públicas de un usuario
async function getUserWishlists(username) {
  const response = await fetch(`/api/wishlists/user/${username}/`);
  const data = await response.json();
  
  if (data.success) {
    console.log(`📋 ${data.message}`);
    console.log(`👤 ${data.user_full_name} (@${data.username})`);
    console.log(`🎁 ${data.total_wishlists} wishlists encontradas\n`);
    
    data.wishlists.forEach(wishlist => {
      console.log(`
        ══════════════════════════════
        📝 ${wishlist.title}
        📄 ${wishlist.description}
        🔗 ${wishlist.public_url}
        📦 ${wishlist.items_count} productos
        💰 Total: $${wishlist.total_value}
        📅 Creada: ${new Date(wishlist.created_at).toLocaleDateString()}
        ══════════════════════════════
      `);
    });
  } else {
    console.log(`⚠️ ${data.message}`);
  }
}

// Uso
getUserWishlists('juanperez');
```

### Python - Crear y Consultar Wishlist

```python
import requests

API_URL = "http://localhost:8000/api/wishlists"
token = "tu_token_aqui"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 1. Crear wishlist
response = requests.post(
    f"{API_URL}/create/",
    headers=headers,
    json={
        "name": "Mi Wishlist",
        "is_public": True
    }
)

wishlist = response.json()['wishlist']
wishlist_id = wishlist['id']

# 2. Agregar productos
for product_id in [123, 456, 789]:
    requests.post(
        f"{API_URL}/{wishlist_id}/add-woocommerce-product/",
        headers=headers,
        json={"woocommerce_product_id": product_id}
    )

# 3. Consultar wishlist (ya tiene toda la info de productos)
response = requests.get(f"{API_URL}/{wishlist_id}/", headers=headers)
wishlist = response.json()['wishlist']

print(f"Wishlist: {wishlist['name']}")
print(f"Total items: {wishlist['total_items']}")
print(f"Total value: ${wishlist['total_value']}")

for item in wishlist['items']:
    print(f"- {item['product_name']}: ${item['product_price']}")
```

---

## Notas Importantes

### Carga Automática de Productos

**Todos** los siguientes endpoints cargan automáticamente la información de productos desde WooCommerce:

- ✅ `GET /api/wishlists/{id}/` - Tu wishlist privada
- ✅ `GET /api/wishlists/@{username}/{id}/` - Wishlist pública por username
- ✅ `GET /api/wishlists/public/{uuid}/` - Wishlist pública por UUID

**No necesitas:**
- ❌ Hacer un request adicional para obtener productos
- ❌ Llamar al endpoint batch de productos
- ❌ Implementar lógica de sincronización en el frontend

**El backend se encarga de:**
- ✅ Consultar WooCommerce automáticamente
- ✅ Actualizar el caché
- ✅ Devolver todo en una respuesta

### Rendimiento

- Primera vez: Consulta WooCommerce (puede tardar 1-2 segundos con muchos productos)
- Siguientes veces: Más rápido gracias al caché
- Cada consulta actualiza el caché automáticamente

### Endpoint Batch (Opcional)

Aunque ya no es necesario para wishlists, el endpoint batch sigue disponible:

```bash
POST /api/products/woocommerce/products/batch/
Body: { "product_ids": [123, 456, 789] }
```

Úsalo solo si necesitas consultar productos fuera del contexto de una wishlist.

---

## Documentación Completa de Endpoints

[... El resto del documento con todos los endpoints detallados continúa igual ...]

---

Para ver la documentación completa de cada endpoint individual, consulta las secciones siguientes del documento.

---

**Última actualización**: 3 de Octubre de 2025  
**Changelog**:
- Agregada carga automática de productos desde WooCommerce en endpoints de consulta de wishlists.
- Agregado endpoint `/api/wishlists/user/{username}/` para listar todas las wishlists públicas de un usuario.
