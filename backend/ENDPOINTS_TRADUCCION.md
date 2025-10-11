# 🌐 Endpoints con Traducción Automática

Todos estos endpoints soportan traducción automática español ↔ inglés mediante el parámetro `lang` o header `Accept-Language`.

## 📝 Uso

```javascript
// Query parameter (GET)
GET /api/endpoint/?lang=en

// Header (cualquier método)
headers: {
  'Accept-Language': 'en'
}

// Desactivar traducción temporalmente
GET /api/endpoint/?lang=en&translate=false
```

---

## ✅ Endpoints Implementados

### 🛍️ **Productos WooCommerce**

| Endpoint | Método | Campos Traducidos |
|----------|--------|-------------------|
| `/api/products/woocommerce/products/` | GET | name, short_description, categories[0].name |
| `/api/products/woocommerce/products/{id}/` | GET | name, short_description, description, categories[0].name |
| `/api/products/woocommerce/products/trending/` | GET | name, short_description, categories[0].name |
| `/api/products/woocommerce/products/batch/` | POST | name, short_description, categories[0].name |
| `/api/products/woocommerce/test/` | GET | N/A (solo prueba de conexión) |

**Campos traducidos:**
- ✅ `name` - Nombre del producto
- ✅ `short_description` - Descripción corta
- ✅ `description` - Descripción completa (solo en detalle)
- ✅ `categories[0].name` - Primera categoría

---

### 📁 **Categorías WooCommerce**

| Endpoint | Método | Campos Traducidos |
|----------|--------|-------------------|
| `/api/products/woocommerce/categories/` | GET | name, description |
| `/api/products/woocommerce/categories/organized/` | GET | name (recursivo) |
| `/api/products/woocommerce/categories/tree/` | GET | name (recursivo) |
| `/api/products/woocommerce/stats/` | GET | name |

**Campos traducidos:**
- ✅ `name` - Nombre de categoría
- ✅ `description` - Descripción de categoría
- ✅ Traducción recursiva en subcategorías

---

### ⭐ **Reviews/Reseñas**

| Endpoint | Método | Campos Traducidos |
|----------|--------|-------------------|
| `/api/products/{productId}/reviews/` | GET | title, comment |
| `/api/products/{productId}/reviews/{reviewId}/` | GET | title, comment |
| `/api/products/{productId}/reviews/stats/` | GET | N/A (solo estadísticas) |
| `/api/products/woocommerce/products/{productId}/reviews/` | GET | title, comment |
| `/api/products/woocommerce/products/{productId}/reviews/{reviewId}/` | GET | title, comment |

**Campos traducidos:**
- ✅ `title` - Título de la reseña
- ✅ `comment` - Comentario de la reseña

---

### 👤 **Perfiles Públicos (Crush)**

| Endpoint | Método | Campos Traducidos |
|----------|--------|-------------------|
| `/api/auth/public/@{username}/` | GET | about, note, gallery captions, wishlist names/descriptions |
| `/api/auth/crush/random/` | GET | about, note, gallery captions, wishlist names/descriptions |
| `/api/auth/crush/random-7/` | GET | note |
| `/api/auth/crush/list/` | GET | N/A (solo username, foto) |
| `/api/auth/search/` | GET | N/A (solo username, foto) |

**Campos traducidos:**
- ✅ `about` - Biografía del usuario
- ✅ `note` - Mensaje personal
- ✅ `gallery_photos[].caption` - Descripciones de fotos
- ✅ `public_wishlists[].name` - Nombre de wishlist
- ✅ `public_wishlists[].description` - Descripción de wishlist
- ✅ `public_wishlists[].items[].notes` - Notas sobre productos

---

### 📋 **Wishlists Públicas**

| Endpoint | Método | Campos Traducidos |
|----------|--------|-------------------|
| `/api/wishlists/public/{uuid}/` | GET | name, description, product names, notes |
| `/api/wishlists/@{username}/{wishlistId}/` | GET | name, description, product names, notes |
| `/api/wishlists/user/{username}/` | GET | name, description |
| `/api/wishlists/public/` | GET | name, description |

**Campos traducidos:**
- ✅ `name` - Nombre de la wishlist
- ✅ `description` - Descripción de la wishlist
- ✅ `items[].product_name` - Nombres de productos (WooCommerce)
- ✅ `items[].product_info.name` - Nombre en product_info
- ✅ `items[].notes` - Notas del usuario sobre items

---

## 📊 Resumen por Tipo de Contenido

### Contenido de WooCommerce (español)
- **Comportamiento**: Solo traduce si `lang=en`
- **Optimización**: Traducción ligera en listados, completa en detalles
- **Campos**: name, description, categories, attributes

### Contenido de Usuarios (idioma variable)
- **Comportamiento**: Auto-detecta idioma → Traduce al solicitado
- **Optimización**: Traducción completa siempre
- **Campos**: about, note, captions, reviews, wishlist names/descriptions

---

## ⚡ Rendimiento

| Tipo de Endpoint | Tiempo Aprox. | Campos Traducidos |
|------------------|---------------|-------------------|
| Producto individual | ~2-3s | 3-5 campos |
| Lista de 8 productos | ~5s | 24 campos |
| Perfil con wishlists | ~3-4s | 10-15 campos |
| Reviews (10) | ~2-3s | 20 campos |
| Categorías organizadas | ~2-3s | 30-50 categorías |

**Nota**: Primera traducción ~2s (carga modelo), siguientes ~0.24s cada una.

---

## 🔧 Configuración

### Archivos Modificados

**Servicios:**
- `services/translation_service.py` - Servicio de traducción con argostranslate

**Serializers:**
- `serializers/user_serializers.py` - UserGallerySerializer, CrushPublicProfileSerializer, CrushCardSerializer
- `serializers/wishlist_serializers.py` - WishListItemSerializer, WishListDetailSerializer
- `serializers/review_serializers.py` - ReviewListSerializer, ReviewDetailSerializer

**Views:**
- `views/product_views.py` - Endpoints de productos WooCommerce
- `views/category_views.py` - Endpoints de categorías organizadas
- `views/auth_views.py` - Ya implementados (perfiles públicos)

---

## 🧪 Testing

### Probar traducciones

```bash
# Productos en inglés
curl "http://localhost:8000/api/products/woocommerce/products/trending/?lang=en"

# Perfil de usuario en inglés
curl "http://localhost:8000/api/auth/public/@cerrotico/?lang=en"

# Reviews en inglés
curl "http://localhost:8000/api/products/woocommerce/products/12345/reviews/?lang=en"

# Categorías en inglés
curl "http://localhost:8000/api/products/woocommerce/categories/organized/?lang=en"

# Sin traducción (más rápido)
curl "http://localhost:8000/api/products/woocommerce/products/trending/?lang=en&translate=false"
```

---

## 📝 Notas Importantes

1. **Endpoints privados/autenticados NO se traducen** (información que el usuario mismo puso)
2. **WooCommerce** solo traduce si `lang != es` (sabemos que está en español)
3. **Contenido de usuarios** auto-detecta idioma y traduce siempre
4. **Traducción es offline** (argostranslate) - Sin llamadas HTTP externas
5. **Caché de modelos** - Primera carga ~2s, luego ~0.24s por texto

---

## 🚫 Endpoints SIN Traducción

Estos endpoints NO tienen traducción (y no la necesitan):

- `/api/products/woocommerce/test/` - Solo prueba de conexión
- `/api/auth/crush/list/` - Solo username y foto
- `/api/auth/search/` - Solo username y foto
- Cualquier endpoint de estadísticas que solo devuelva números
- Endpoints privados/autenticados (perfil del usuario logueado)

---

**Última actualización**: 11 de Octubre, 2025

