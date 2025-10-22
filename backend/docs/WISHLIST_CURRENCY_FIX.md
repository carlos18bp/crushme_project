# 🔧 Fix: Conversión de Moneda en Wishlist Pública

## ❌ Problema

El endpoint `GET /api/wishlists/@{username}/{wishlist_id}/` NO estaba convirtiendo los precios según el header `X-Currency`.

**Antes del fix:**
```bash
# Request con X-Currency: USD
curl -H "X-Currency: USD" "/api/wishlists/@cerrotico/1/"

# Response (precios en COP, no convertidos)
{
  "wishlist": {
    "total_value": 6890.0,  // ❌ Debería ser 1.78 USD
    "items": [{
      "product_price": 6890.0,  // ❌ Debería ser 1.78 USD
      "currency": "COP"  // ❌ Debería ser USD
    }]
  }
}
```

---

## ✅ Solución

Agregué conversión de precios en el endpoint `get_public_wishlist_by_username()`:

1. Lee el header `X-Currency` del request (via `CurrencyMiddleware`)
2. Convierte todos los precios usando `convert_price_fields()`
3. Retorna `currency` en la respuesta

**Cambios en `wishlist_woocommerce_views.py`:**

```python
# Get currency from request (set by CurrencyMiddleware)
currency = getattr(request, 'currency', 'COP')

# Enriquecer con datos frescos de WooCommerce
wishlist = enrich_wishlist_with_woocommerce_data(wishlist)

detail_serializer = WishListDetailSerializer(wishlist, context={'request': request})
wishlist_data = detail_serializer.data

# Convert prices in wishlist data
from ..utils.price_helpers import convert_price_fields
wishlist_data = convert_price_fields(wishlist_data, currency)

return Response({
    'wishlist': wishlist_data,
    'currency': currency.upper()
}, status=status.HTTP_200_OK)
```

---

## ✅ Verificación

### Test en USD

**Request:**
```bash
curl -H "X-Currency: USD" \
  "http://localhost:8000/api/wishlists/@cerrotico/1/"
```

**Response:**
```json
{
  "currency": "USD",
  "wishlist": {
    "id": 1,
    "name": "M7 list",
    "total_value": 1.78,
    "currency": "USD",
    "items": [
      {
        "product_name": "Lubricante Íntimo Saborizado Action Lube",
        "product_price": 1.78,
        "currency": "USD",
        "product_info": {
          "price": 1.78,
          "currency": "USD"
        }
      }
    ]
  }
}
```

### Test en COP

**Request:**
```bash
curl -H "X-Currency: COP" \
  "http://localhost:8000/api/wishlists/@cerrotico/1/"
```

**Response:**
```json
{
  "currency": "COP",
  "wishlist": {
    "total_value": 6890.0,
    "currency": "COP",
    "items": [
      {
        "product_price": 6890.0,
        "currency": "COP",
        "product_info": {
          "price": 6890.0,
          "currency": "COP"
        }
      }
    ]
  }
}
```

---

## 📊 Campos Convertidos

El endpoint ahora convierte correctamente:

| Campo | Ubicación | Descripción |
|-------|-----------|-------------|
| `total_value` | `wishlist.total_value` | Valor total de la wishlist |
| `product_price` | `wishlist.items[].product_price` | Precio de cada producto |
| `product_info.price` | `wishlist.items[].product_info.price` | Precio en product_info |
| `currency` | `wishlist.currency` | Indicador de moneda |
| `currency` | `wishlist.items[].currency` | Moneda de cada item |
| `currency` | Response root | Moneda de la respuesta |

---

## 🔄 Flujo de Conversión

```
1. Request: GET /api/wishlists/@cerrotico/1/
   Headers: X-Currency: USD
   ↓
2. CurrencyMiddleware lee X-Currency
   request.currency = 'USD'
   ↓
3. get_public_wishlist_by_username()
   currency = getattr(request, 'currency', 'COP')
   ↓
4. enrich_wishlist_with_woocommerce_data()
   Carga datos frescos de WooCommerce (en COP)
   ↓
5. WishListDetailSerializer
   Serializa wishlist con items
   ↓
6. convert_price_fields(wishlist_data, 'USD')
   Convierte todos los precios recursivamente
   ↓
7. Response con precios en USD
```

---

## 🎯 Casos de Uso

### 1. Frontend con Currency Store
```javascript
// currencyStore.currentCurrency = 'USD'
const response = await api.get('/api/wishlists/@cerrotico/1/')
// response.wishlist.items[0].product_price = 1.78 USD
```

### 2. Compra desde Wishlist
```javascript
// Usuario ve wishlist en USD
const wishlist = await api.get('/api/wishlists/@cerrotico/1/', {
  headers: { 'X-Currency': 'USD' }
})

// Agrega items al carrito con precios en USD
wishlist.items.forEach(item => {
  cart.add({
    product_id: item.woocommerce_product_id,
    price: item.product_price,  // Ya en USD
    currency: 'USD'
  })
})
```

### 3. Compartir Wishlist
```javascript
// Link compartido: /@cerrotico/1
// Usuario en Colombia → Ve precios en COP
// Usuario en USA → Ve precios en USD
```

---

## 🔗 Endpoints Relacionados

| Endpoint | Conversión | Estado |
|----------|------------|--------|
| `GET /api/wishlists/@{username}/{id}` | ✅ Sí | **CORREGIDO** |
| `GET /api/auth/public/@{username}/` | ✅ Sí | Ya funcionaba |
| `GET /api/auth/crush/random/` | ✅ Sí | Ya funcionaba |
| `POST /api/wishlists/{id}/products/` | ✅ Sí | Ya funcionaba |
| `POST /api/gifts/send/` | ✅ Sí | Ya funcionaba |

---

## ⚠️ Importante

**Este endpoint es crítico** porque se usa en:

1. **WishlistCheckoutRedirect.vue** - Carga wishlist para compra
2. **PublicProfile.vue** - Muestra wishlists públicas
3. **Compartir links** - Usuarios externos ven la wishlist

Sin la conversión de moneda, los usuarios veían precios incorrectos al comprar desde una wishlist.

---

## ✅ Resumen

**Problema:** Endpoint no convertía precios según X-Currency header

**Solución:** 
- Agregada lectura de `request.currency`
- Agregada conversión con `convert_price_fields()`
- Agregado campo `currency` en response

**Resultado:**
- ✅ Precios convertidos correctamente (COP/USD)
- ✅ Compatible con frontend currency store
- ✅ Funciona con flujo de compra de wishlist

**Archivo:** `crushme_app/views/wishlist_woocommerce_views.py`  
**Función:** `get_public_wishlist_by_username()`  
**Líneas:** 291-306

**Fecha:** 2025-10-22
