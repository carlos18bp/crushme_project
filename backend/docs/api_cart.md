# API de Carrito de Compras - CrushMe

## Base URL
```
/api/v1/cart/
```

## Autenticación
Todos los endpoints requieren autenticación mediante token JWT:
```
Authorization: Bearer <token>
```

---

## 📋 Índice de Endpoints

### Información del Carrito
1. [GET /api/v1/cart/](#1-obtener-carrito-completo) - Obtener carrito completo
2. [GET /api/v1/cart/summary/](#2-obtener-resumen-del-carrito) - Obtener resumen del carrito

### Operaciones del Carrito
3. [POST /api/v1/cart/add/](#3-agregar-producto-al-carrito) - Agregar producto al carrito
4. [PUT /api/v1/cart/items/{item_id}/update/](#4-actualizar-cantidad-de-item) - Actualizar cantidad de un item
5. [DELETE /api/v1/cart/items/{item_id}/remove/](#5-eliminar-item-del-carrito) - Eliminar item del carrito
6. [DELETE /api/v1/cart/clear/](#6-vaciar-carrito) - Vaciar todo el carrito

### Endpoints de Conveniencia
7. [POST /api/v1/cart/products/{product_id}/add/](#7-agregar-producto-directo) - Agregar producto directo (por ID)
8. [GET /api/v1/cart/products/{product_id}/count/](#8-obtener-cantidad-de-producto) - Obtener cantidad de un producto en el carrito

### Validación
9. [POST /api/v1/cart/validate/](#9-validar-carrito-para-checkout) - Validar carrito para checkout

---

## Endpoints Detallados

### 1. Obtener Carrito Completo

Obtiene el carrito del usuario con todos sus items y detalles completos.

**Endpoint:** `GET /api/v1/cart/`

**Autenticación:** Requerida

**Respuesta Exitosa:** `200 OK`

```json
{
  "cart": {
    "id": 1,
    "user": "usuario@example.com",
    "items": [
      {
        "id": 1,
        "woocommerce_product_id": 123,
        "product_name": "Camiseta Estampada",
        "product_image": "https://example.com/images/camiseta.jpg",
        "quantity": 2,
        "unit_price": "25.99",
        "subtotal": "51.98",
        "created_at": "2025-10-03T10:30:00Z",
        "updated_at": "2025-10-03T10:30:00Z"
      },
      {
        "id": 2,
        "woocommerce_product_id": 456,
        "product_name": "Pantalón Denim",
        "product_image": "https://example.com/images/pantalon.jpg",
        "quantity": 1,
        "unit_price": "45.00",
        "subtotal": "45.00",
        "created_at": "2025-10-03T11:00:00Z",
        "updated_at": "2025-10-03T11:00:00Z"
      }
    ],
    "total_items": 3,
    "total_price": "96.98",
    "is_empty": false,
    "created_at": "2025-10-03T10:30:00Z",
    "updated_at": "2025-10-03T11:00:00Z"
  },
  "is_new_cart": false
}
```

**Campos:**
- `cart.id`: ID del carrito
- `cart.user`: Email del usuario
- `cart.items`: Lista de items en el carrito
  - `id`: ID del item en el carrito
  - `woocommerce_product_id`: ID del producto en WooCommerce
  - `product_name`: Nombre del producto
  - `product_image`: URL de la imagen del producto
  - `quantity`: Cantidad de unidades
  - `unit_price`: Precio unitario
  - `subtotal`: Precio total del item (unit_price × quantity)
- `cart.total_items`: Cantidad total de items (suma de cantidades)
- `cart.total_price`: Precio total del carrito
- `cart.is_empty`: Indica si el carrito está vacío
- `is_new_cart`: Indica si el carrito se creó en esta petición

**Notas:**
- Si el usuario no tiene un carrito, se crea automáticamente
- El carrito siempre se retorna, incluso si está vacío

---

### 2. Obtener Resumen del Carrito

Obtiene un resumen ligero del carrito (ideal para mostrar en el header/navegación).

**Endpoint:** `GET /api/v1/cart/summary/`

**Autenticación:** Requerida

**Respuesta Exitosa:** `200 OK`

```json
{
  "cart_summary": {
    "id": 1,
    "total_items": 3,
    "total_price": "96.98",
    "items_count": 2,
    "updated_at": "2025-10-03T11:00:00Z"
  }
}
```

**Campos:**
- `id`: ID del carrito
- `total_items`: Cantidad total de items (suma de cantidades)
- `total_price`: Precio total del carrito
- `items_count`: Cantidad de productos únicos
- `updated_at`: Última actualización del carrito

**Respuesta si no hay carrito:** `200 OK`

```json
{
  "cart_summary": {
    "id": null,
    "total_items": 0,
    "total_price": "0.00",
    "items_count": 0
  }
}
```

**Uso:**
- Ideal para mostrar el contador de items en el header
- Respuesta más ligera que el endpoint completo

---

### 3. Agregar Producto al Carrito

Agrega un producto de WooCommerce al carrito del usuario.

**Endpoint:** `POST /api/v1/cart/add/`

**Autenticación:** Requerida

**Body:**

```json
{
  "product_id": 123,
  "quantity": 2,
  "product_name": "Camiseta Estampada",
  "product_price": "25.99",
  "product_image": "https://example.com/images/camiseta.jpg"
}
```

**Campos Requeridos:**
- `product_id` (integer): ID del producto en WooCommerce
- `quantity` (integer): Cantidad a agregar (mínimo 1, por defecto 1)

**Campos Opcionales:**
- `product_name` (string): Nombre del producto (para mejor rendimiento)
- `product_price` (decimal): Precio del producto
- `product_image` (string): URL de la imagen del producto

**Respuesta Exitosa:** `200 OK`

```json
{
  "message": "Added 2 x Camiseta Estampada to cart",
  "item": {
    "id": 1,
    "product_id": 123,
    "product_name": "Camiseta Estampada",
    "quantity": 2,
    "unit_price": "25.99",
    "subtotal": "51.98"
  },
  "cart_summary": {
    "total_items": 3,
    "total_price": "96.98"
  }
}
```

**Errores:**

**400 Bad Request** - Datos inválidos:
```json
{
  "error": "Invalid data",
  "details": {
    "product_id": ["This field is required."],
    "quantity": ["Ensure this value is greater than or equal to 1."]
  }
}
```

**500 Internal Server Error** - Error al agregar:
```json
{
  "error": "Failed to add item to cart",
  "details": "Error message"
}
```

**Comportamiento:**
- Si el producto ya existe en el carrito, se incrementa la cantidad
- Si el carrito no existe, se crea automáticamente
- Los datos opcionales del producto mejoran el rendimiento al evitar llamadas a la API

---

### 4. Actualizar Cantidad de Item

Actualiza la cantidad de un item específico en el carrito.

**Endpoint:** `PUT /api/v1/cart/items/{item_id}/update/`

**Parámetros URL:**
- `item_id`: ID del item en el carrito

**Autenticación:** Requerida

**Body:**

```json
{
  "quantity": 5
}
```

**Campos:**
- `quantity` (integer): Nueva cantidad (mínimo 1)

**Respuesta Exitosa:** `200 OK`

```json
{
  "message": "Updated Camiseta Estampada quantity to 5",
  "cart": {
    "id": 1,
    "user": "usuario@example.com",
    "items": [
      {
        "id": 1,
        "woocommerce_product_id": 123,
        "product_name": "Camiseta Estampada",
        "product_image": "https://example.com/images/camiseta.jpg",
        "quantity": 5,
        "unit_price": "25.99",
        "subtotal": "129.95",
        "created_at": "2025-10-03T10:30:00Z",
        "updated_at": "2025-10-03T12:00:00Z"
      }
    ],
    "total_items": 5,
    "total_price": "129.95",
    "is_empty": false,
    "created_at": "2025-10-03T10:30:00Z",
    "updated_at": "2025-10-03T12:00:00Z"
  }
}
```

**Errores:**

**404 Not Found** - Carrito no encontrado:
```json
{
  "error": "Cart not found"
}
```

**404 Not Found** - Item no encontrado:
```json
{
  "error": "Cart item not found"
}
```

**400 Bad Request** - Cantidad inválida:
```json
{
  "error": "Invalid data",
  "details": {
    "quantity": ["Ensure this value is greater than or equal to 1."]
  }
}
```

**400 Bad Request** - Stock insuficiente:
```json
{
  "error": "Invalid data",
  "details": {
    "non_field_errors": ["Only 3 items available in stock."]
  }
}
```

---

### 5. Eliminar Item del Carrito

Elimina un item específico del carrito.

**Endpoint:** `DELETE /api/v1/cart/items/{item_id}/remove/`

**Parámetros URL:**
- `item_id`: ID del item en el carrito

**Autenticación:** Requerida

**Respuesta Exitosa:** `200 OK`

```json
{
  "message": "Removed Camiseta Estampada from cart",
  "cart": {
    "id": 1,
    "user": "usuario@example.com",
    "items": [
      {
        "id": 2,
        "woocommerce_product_id": 456,
        "product_name": "Pantalón Denim",
        "product_image": "https://example.com/images/pantalon.jpg",
        "quantity": 1,
        "unit_price": "45.00",
        "subtotal": "45.00",
        "created_at": "2025-10-03T11:00:00Z",
        "updated_at": "2025-10-03T11:00:00Z"
      }
    ],
    "total_items": 1,
    "total_price": "45.00",
    "is_empty": false,
    "created_at": "2025-10-03T10:30:00Z",
    "updated_at": "2025-10-03T12:05:00Z"
  }
}
```

**Errores:**

**404 Not Found** - Carrito no encontrado:
```json
{
  "error": "Cart not found"
}
```

**404 Not Found** - Item no encontrado:
```json
{
  "error": "Cart item not found"
}
```

---

### 6. Vaciar Carrito

Elimina todos los items del carrito del usuario.

**Endpoint:** `DELETE /api/v1/cart/clear/`

**Autenticación:** Requerida

**Respuesta Exitosa:** `200 OK`

```json
{
  "message": "Cleared 3 items from cart",
  "cart": {
    "id": 1,
    "user": "usuario@example.com",
    "items": [],
    "total_items": 0,
    "total_price": "0.00",
    "is_empty": true,
    "created_at": "2025-10-03T10:30:00Z",
    "updated_at": "2025-10-03T12:10:00Z"
  }
}
```

**Respuesta si no hay carrito:** `200 OK`

```json
{
  "message": "Cart was already empty",
  "cart": {
    "id": null,
    "items": [],
    "total_items": 0,
    "total_price": "0.00",
    "is_empty": true
  }
}
```

---

### 7. Agregar Producto Directo

Agrega un producto específico al carrito usando su ID (endpoint conveniente).

**Endpoint:** `POST /api/v1/cart/products/{product_id}/add/`

**Parámetros URL:**
- `product_id`: ID del producto

**Autenticación:** Requerida

**Body (Opcional):**

```json
{
  "quantity": 2
}
```

**Campos:**
- `quantity` (integer): Cantidad a agregar (por defecto 1)

**Respuesta Exitosa:** `200 OK`

```json
{
  "message": "Added 2 x Camiseta Estampada to cart",
  "cart": {
    "id": 1,
    "user": "usuario@example.com",
    "items": [
      {
        "id": 1,
        "woocommerce_product_id": 123,
        "product_name": "Camiseta Estampada",
        "product_image": "https://example.com/images/camiseta.jpg",
        "quantity": 2,
        "unit_price": "25.99",
        "subtotal": "51.98",
        "created_at": "2025-10-03T10:30:00Z",
        "updated_at": "2025-10-03T10:30:00Z"
      }
    ],
    "total_items": 2,
    "total_price": "51.98",
    "is_empty": false,
    "created_at": "2025-10-03T10:30:00Z",
    "updated_at": "2025-10-03T10:30:00Z"
  }
}
```

**Errores:**

**404 Not Found** - Producto no encontrado:
```json
{
  "error": "Product not found"
}
```

**400 Bad Request** - Cantidad inválida:
```json
{
  "error": "Invalid quantity"
}
```

**400 Bad Request** - Producto no disponible:
```json
{
  "error": "Invalid data",
  "details": {
    "product_id": ["Product is not available."]
  }
}
```

**400 Bad Request** - Sin stock:
```json
{
  "error": "Invalid data",
  "details": {
    "product_id": ["Product is out of stock."]
  }
}
```

**Diferencia con /api/v1/cart/add/:**
- Este endpoint valida que el producto exista en la base de datos local
- `/cart/add/` es más rápido y trabaja directamente con productos de WooCommerce

---

### 8. Obtener Cantidad de Producto

Obtiene la cantidad de un producto específico en el carrito del usuario.

**Endpoint:** `GET /api/v1/cart/products/{product_id}/count/`

**Parámetros URL:**
- `product_id`: ID del producto

**Autenticación:** Requerida

**Respuesta Exitosa:** `200 OK`

```json
{
  "product_id": 123,
  "quantity_in_cart": 2,
  "is_in_cart": true
}
```

**Respuesta si el producto no está en el carrito:** `200 OK`

```json
{
  "product_id": 123,
  "quantity_in_cart": 0,
  "is_in_cart": false
}
```

**Errores:**

**404 Not Found** - Producto no encontrado:
```json
{
  "error": "Product not found"
}
```

**Uso:**
- Útil para mostrar si un producto ya está en el carrito
- Permite mostrar la cantidad actual en la UI del producto

---

### 9. Validar Carrito para Checkout

Valida que el carrito esté listo para proceder al checkout.

**Endpoint:** `POST /api/v1/cart/validate/`

**Autenticación:** Requerida

**Respuesta Exitosa:** `200 OK`

```json
{
  "message": "Cart is valid for checkout",
  "cart_summary": {
    "total_items": 3,
    "total_price": "96.98",
    "items_count": 2
  }
}
```

**Errores:**

**400 Bad Request** - Carrito vacío:
```json
{
  "error": "Cart validation failed",
  "details": {
    "non_field_errors": ["Cart is empty."]
  }
}
```

**400 Bad Request** - Validación fallida:
```json
{
  "error": "Cart validation failed",
  "issues": [
    "Camiseta Estampada is no longer available",
    "Only 1 of Pantalón Denim available"
  ]
}
```

**Validaciones realizadas:**
- Verifica que el carrito no esté vacío
- Verifica que todos los productos estén activos
- Verifica que haya stock suficiente para cada item
- Verifica la disponibilidad de todos los productos

**Uso:**
- Llamar antes de proceder al checkout
- Permite informar al usuario de problemas antes de intentar comprar

---

## Estructura de Datos

### CartItem (Item del Carrito)

```json
{
  "id": 1,
  "woocommerce_product_id": 123,
  "product_name": "Camiseta Estampada",
  "product_image": "https://example.com/images/camiseta.jpg",
  "quantity": 2,
  "unit_price": "25.99",
  "subtotal": "51.98",
  "created_at": "2025-10-03T10:30:00Z",
  "updated_at": "2025-10-03T10:30:00Z"
}
```

### Cart (Carrito)

```json
{
  "id": 1,
  "user": "usuario@example.com",
  "items": [/* lista de CartItem */],
  "total_items": 3,
  "total_price": "96.98",
  "is_empty": false,
  "created_at": "2025-10-03T10:30:00Z",
  "updated_at": "2025-10-03T11:00:00Z"
}
```

### CartSummary (Resumen del Carrito)

```json
{
  "id": 1,
  "total_items": 3,
  "total_price": "96.98",
  "items_count": 2,
  "updated_at": "2025-10-03T11:00:00Z"
}
```

---

## Ejemplos de Uso

### Flujo Básico: Agregar Producto al Carrito

```javascript
// 1. Agregar producto al carrito
const response = await fetch('/api/v1/cart/add/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    product_id: 123,
    quantity: 2,
    product_name: 'Camiseta Estampada',
    product_price: '25.99',
    product_image: 'https://example.com/images/camiseta.jpg'
  })
});

const data = await response.json();
console.log(data.message); // "Added 2 x Camiseta Estampada to cart"
console.log(data.cart_summary); // { total_items: 2, total_price: "51.98" }
```

### Obtener Carrito Completo

```javascript
const response = await fetch('/api/v1/cart/', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer ' + token
  }
});

const data = await response.json();
console.log(data.cart.items); // Lista de items en el carrito
console.log(data.cart.total_price); // Precio total del carrito
```

### Actualizar Cantidad de un Item

```javascript
const itemId = 1;
const response = await fetch(`/api/v1/cart/items/${itemId}/update/`, {
  method: 'PUT',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    quantity: 5
  })
});

const data = await response.json();
console.log(data.message); // "Updated Camiseta Estampada quantity to 5"
```

### Validar Carrito Antes del Checkout

```javascript
const response = await fetch('/api/v1/cart/validate/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token
  }
});

const data = await response.json();
if (response.ok) {
  console.log('Carrito válido, proceder al checkout');
  console.log(data.cart_summary);
} else {
  console.log('Problemas con el carrito:', data.issues);
}
```

### Obtener Resumen del Carrito (para Header)

```javascript
const response = await fetch('/api/v1/cart/summary/', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer ' + token
  }
});

const data = await response.json();
document.querySelector('.cart-badge').textContent = data.cart_summary.total_items;
```

---

## Notas de Implementación

### Integración con WooCommerce

El carrito trabaja principalmente con productos de WooCommerce:

- **Endpoint rápido:** `/cart/add/` - Agrega productos directamente con datos del frontend
- **Endpoint validado:** `/cart/products/{id}/add/` - Valida contra la base de datos local

### Comportamiento de Cantidades

- Si agregas un producto que ya existe, se **incrementa** la cantidad
- `total_items` es la suma de todas las cantidades
- `items_count` es el número de productos únicos

### Persistencia

- El carrito se asocia al usuario autenticado
- El carrito persiste entre sesiones
- Los items se mantienen hasta que se eliminen o se complete el checkout

### Validación de Stock

- Al agregar/actualizar items, se valida el stock disponible
- La validación completa se hace en `/cart/validate/` antes del checkout
- Los productos inactivos o sin stock generan errores

### Performance

- Para mejor rendimiento, usa `/cart/add/` con datos del producto del frontend
- Usa `/cart/summary/` para actualizaciones ligeras del UI
- El endpoint `/cart/` retorna el carrito completo con todos los detalles

---

## Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | Operación exitosa |
| 400 | Datos inválidos o validación fallida |
| 401 | No autenticado |
| 404 | Carrito, item o producto no encontrado |
| 500 | Error interno del servidor |

---

## Preguntas Frecuentes

### ¿Cuál es la diferencia entre `total_items` e `items_count`?

- `total_items`: Suma de todas las cantidades (ej: 2 camisetas + 1 pantalón = 3)
- `items_count`: Número de productos únicos (ej: camisetas + pantalón = 2)

### ¿Cómo se calculan los precios?

- `unit_price`: Precio por unidad del producto
- `subtotal`: `unit_price × quantity` (precio total del item)
- `total_price`: Suma de todos los subtotales

### ¿Qué pasa si agrego un producto que ya está en el carrito?

Se incrementa la cantidad del item existente en lugar de crear un item duplicado.

### ¿El carrito se vacía automáticamente después de una compra?

No, debes llamar explícitamente a `/cart/clear/` después de completar el checkout.

### ¿Puedo agregar productos que no están en la base de datos local?

Sí, usando `/cart/add/` puedes agregar cualquier producto de WooCommerce. El endpoint `/cart/products/{id}/add/` requiere que el producto exista localmente.

### ¿Cómo muestro el contador del carrito en el header?

Usa el endpoint `/cart/summary/` que retorna un resumen ligero con `total_items` perfecto para badges/contadores.


