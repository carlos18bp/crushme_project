# Endpoints que Retornan Precios

Este documento lista todos los endpoints del backend que retornan información de precios, ya convertidos según el header `X-Currency` (COP/USD).

---

## 📦 PRODUCTOS (WooCommerce)

### 1. Lista de productos
```
GET /api/products/woocommerce/products/
```
**Parámetros de query:**
- `per_page` - Productos por página (default: 10, max: 100)
- `page` - Número de página
- `category_id` - Filtrar por categoría

**Campos de precio retornados:**
- `price` - Precio convertido
- `converted_price` - Precio convertido explícito
- `regular_price` - Precio regular convertido
- `converted_regular_price` - Precio regular explícito
- `currency` - Moneda actual (COP/USD)

---

### 2. Detalle de producto
```
GET /api/products/woocommerce/products/{id}/
```
**Campos de precio retornados:**
- `price`, `converted_price`
- `regular_price`, `converted_regular_price`
- `on_sale` - Boolean si está en oferta
- `available_variations[].price` - Precios de variaciones (si es producto variable)
- `currency` - Moneda actual

---

### 3. Variaciones de producto
```
GET /api/products/woocommerce/products/{id}/variations/
```
**Parámetros de query:**
- `per_page` - Variaciones por página (default: 100)
- `page` - Número de página

**Campos de precio retornados:**
- `price`, `converted_price`
- `regular_price`, `converted_regular_price`
- `on_sale` - Boolean si está en oferta
- `currency` - Moneda actual

---

### 4. Detalle de variación específica
```
GET /api/products/woocommerce/products/{id}/variations/{var_id}/
```
**Campos de precio retornados:**
- `price`, `converted_price`
- `regular_price`, `converted_regular_price`
- `on_sale` - Boolean si está en oferta
- `currency` - Moneda actual

---

### 5. Productos en tendencia
```
GET /api/products/woocommerce/products/trending/
```
**Retorna:** 8 productos más populares con stock disponible

**Campos de precio retornados:**
- `price`, `converted_price`
- `regular_price`, `converted_regular_price`
- `currency` - Moneda actual

---

## 🛒 CARRITO

### 6. Obtener carrito
```
GET /api/cart/
```
**Campos de precio retornados:**
- `items[].product_price` - Precio de cada item
- `items[].subtotal` - Subtotal por item (precio × cantidad)
- `total_price` - Total del carrito
- `currency` - Moneda actual

---

### 7. Resumen del carrito
```
GET /api/cart/summary/
```
**Campos de precio retornados:**
- `total_price` - Total del carrito
- `total_items` - Cantidad de items
- `items[].product_price` - Precio de cada item
- `currency` - Moneda actual

---

### 8. Agregar al carrito
```
POST /api/cart/add/
```
**Request body:**
```json
{
  "product_id": 123,
  "quantity": 1,
  "variation_id": 456 // Opcional
}
```

**Campos de precio retornados:**
- `product_price` - Precio del producto agregado
- `total_price` - Total actualizado del carrito
- `currency` - Moneda actual

---

### 9. Validar carrito
```
POST /api/cart/validate/
```
**Campos de precio retornados:**
- `items[].product_price` - Precio actualizado de cada item
- `items[].price_changed` - Boolean si el precio cambió
- `total_price` - Total del carrito
- `currency` - Moneda actual

---

## 📝 WISHLISTS

### 10. Agregar producto a wishlist
```
POST /api/wishlists/{id}/products/
```
**Request body:**
```json
{
  "woocommerce_product_id": 123,
  "notes": "Opcional",
  "priority": "medium"
}
```

**Campos de precio retornados:**
- `product_price` - Precio del producto
- `total_value` - Total actualizado de la wishlist
- `currency` - Moneda actual

---

### 11. Eliminar producto de wishlist
```
DELETE /api/wishlists/{id}/products/{product_id}/
```
**Campos de precio retornados:**
- `total_value` - Total actualizado de la wishlist
- `currency` - Moneda actual

---

### 12. Refrescar productos de wishlist
```
POST /api/wishlists/{id}/refresh/
```
**Campos de precio retornados:**
- `items[].product_price` - Precios actualizados
- `total_value` - Total actualizado
- `updated_count` - Cantidad de productos actualizados
- `currency` - Moneda actual

---

### 13. Wishlist pública por username
```
GET /api/wishlists/@{username}/{wishlist_id}/
```
**Ejemplo:** `/api/wishlists/@cerrotico/1/`

**Campos de precio retornados:**
- `items[].product_price` - Precio de cada producto
- `items[].product_info.price` - Precio en info del producto
- `total_value` - Total de la wishlist
- `currency` - Moneda actual

---

### 14. Wishlist pública por UUID
```
GET /api/wishlists/public/{uuid}/
```
**Campos de precio retornados:**
- `items[].product_price` - Precio de cada producto
- `total_value` - Total de la wishlist
- `currency` - Moneda actual

---

### 15. Lista de wishlists del usuario
```
GET /api/wishlists/
```
**Campos de precio retornados:**
- `wishlists[].total_value` - Total de cada wishlist
- `wishlists[].items[].product_price` - Precio de cada producto
- `currency` - Moneda actual

---

## ❤️ FAVORITOS

### 16. Lista de favoritos
```
GET /api/favorites/products/
```
**Campos de precio retornados:**
- `data[].price` - Precio convertido
- `data[].converted_price` - Precio convertido explícito
- `data[].regular_price` - Precio regular
- `currency` - Moneda actual

---

### 17. Agregar a favoritos
```
POST /api/favorites/products/
```
**Request body:**
```json
{
  "woocommerce_product_id": 123
}
```

**Campos de precio retornados:**
- `product.price` - Precio convertido
- `product.converted_price` - Precio convertido explícito
- `currency` - Moneda actual

---

## 📦 ÓRDENES Y COMPRAS

### 18. Historial de compras
```
GET /api/orders/purchases/
```
**Campos de precio retornados:**
- `orders[].total_amount` - Total de cada orden
- `orders[].items[].price` - Precio de cada item
- `total_spent` - Total gastado (convertido)
- `currency` - Moneda actual

---

### 19. Historial de regalos enviados
```
GET /api/orders/gifts/
```
**Campos de precio retornados:**
- `gifts[].total_amount` - Total de cada regalo
- `gifts[].items[].price` - Precio de cada item
- `currency` - Moneda actual

---

## 💳 CHECKOUT

### 20. Crear orden PayPal
```
POST /api/orders/paypal/create/
```
**Request body:**
```json
{
  "items": [
    {
      "product_id": 123,
      "quantity": 1,
      "variation_id": 456
    }
  ],
  "shipping_info": {...}
}
```

**Campos de precio retornados:**
- `order_id` - ID de la orden PayPal
- `total_amount` - Total de la orden
- `currency` - Moneda actual

---

### 21. Enviar regalo
```
POST /api/gifts/send/
```
**Request body:**
```json
{
  "receiver_username": "username",
  "items": [...],
  "message": "Mensaje opcional",
  "is_from_wishlist": false,
  "wishlist_id": null
}
```

**Campos de precio retornados:**
- `total_amount` - Total del regalo
- `wishlist_info.remaining_items` - Items restantes (si es de wishlist)
- `currency` - Moneda actual

---

## 📊 Resumen

**Total de endpoints:** 21

**Header requerido en TODOS:**
```
X-Currency: COP | USD
```

**Campos comunes retornados:**
- `price` / `converted_price` - Precio actual convertido
- `regular_price` / `converted_regular_price` - Precio regular convertido
- `total_value` / `total_amount` - Totales convertidos
- `currency` - Moneda actual (COP o USD)

---

## ⚙️ Funcionamiento

1. **Frontend envía header:**
   ```javascript
   headers: {
     'X-Currency': 'USD' // o 'COP'
   }
   ```

2. **Backend convierte precios:**
   - Lee el header `X-Currency`
   - Aplica conversión usando `CurrencyConverter`
   - Retorna todos los precios en la moneda solicitada

3. **Frontend muestra precios:**
   - Lee `converted_price || price`
   - Formatea con `currencyStore.formatPrice()`
   - **NO hace cálculos de conversión**

---

## 🔧 Componentes Backend

- **CurrencyConverter** (`crushme_app/utils/currency_converter.py`)
- **CurrencyMiddleware** (`crushme_app/middleware/currency_middleware.py`)
- **Price Helpers** (`crushme_app/utils/price_helpers.py`)

---

## 📝 Notas

- **COP:** Precios en enteros sin decimales (ej: `11037`)
- **USD:** Precios con 2 decimales (ej: `2.85`)
- **Tasa de cambio:** 1 USD = 4,000 COP (aproximada)
- **Todos los precios ya vienen convertidos** del backend
- **Frontend solo formatea** para display, no convierte
