# API Endpoints: Gestión de Órdenes

## Información General

Sistema completo de gestión de órdenes para la plataforma de e-commerce CrushMe. Permite a los usuarios crear órdenes desde su carrito, ver su historial de órdenes, hacer seguimiento, cancelar órdenes y más. Incluye endpoints administrativos para gestión completa de órdenes.

---

## Endpoints Disponibles

### 1. Gestión de Órdenes (Usuario)
```
GET    /api/orders/                          - Listar mis órdenes
GET    /api/orders/<order_id>/               - Ver detalles de una orden
POST   /api/orders/create/                   - Crear nueva orden desde carrito
POST   /api/orders/<order_id>/cancel/        - Cancelar una orden
```

### 2. Seguimiento de Órdenes
```
GET    /api/orders/track/<order_number>/     - Rastrear orden por número
GET    /api/orders/recent/                   - Obtener últimas 5 órdenes
```

### 3. Endpoints Administrativos
```
GET    /api/orders/admin/all/                - Listar todas las órdenes (Admin)
PATCH  /api/orders/admin/<order_id>/status/  - Actualizar estado de orden (Admin)
GET    /api/orders/admin/statistics/         - Obtener estadísticas (Admin)
```

---

## Autenticación

✅ **Requerida** - Token JWT Bearer

```
Authorization: Bearer <token>
```

Todos los endpoints de órdenes requieren autenticación. Los endpoints administrativos requieren permisos de administrador.

---

## 1. Crear Nueva Orden

### Endpoint
```
POST /api/orders/create/
```

### Descripción
Crea una nueva orden a partir del carrito actual del usuario. El carrito debe tener al menos un producto y todos los productos deben estar disponibles y tener stock suficiente. Una vez creada la orden, el carrito se vacía automáticamente.

### Autenticación
✅ Requerida (Usuario autenticado)

### Request Body

```json
{
  "shipping_address": "Calle 123 #45-67",
  "shipping_city": "Bogotá",
  "shipping_state": "Cundinamarca",
  "shipping_postal_code": "110111",
  "shipping_country": "Colombia",
  "phone_number": "+57 300 1234567",
  "notes": "Por favor llamar antes de entregar"
}
```

### Campos del Request

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `shipping_address` | string | ✅ Sí | Dirección de envío (mínimo 10 caracteres) |
| `shipping_city` | string | ✅ Sí | Ciudad de envío |
| `shipping_state` | string | ✅ Sí | Estado/Departamento |
| `shipping_postal_code` | string | ✅ Sí | Código postal |
| `shipping_country` | string | ✅ Sí | País de envío |
| `phone_number` | string | ✅ Sí | Número de teléfono (mínimo 10 caracteres) |
| `notes` | string | ❌ No | Notas adicionales o instrucciones de entrega |

### Validaciones

- ✅ El carrito debe existir y no estar vacío
- ✅ Todos los productos en el carrito deben estar activos
- ✅ Debe haber stock suficiente para cada producto
- ✅ La dirección debe tener al menos 10 caracteres
- ✅ El número de teléfono debe tener al menos 10 caracteres

### Respuesta Exitosa

**Código:** `201 Created`

```json
{
  "message": "Order created successfully",
  "order": {
    "id": 45,
    "order_number": "ORD123456ABCD1234",
    "user": "Juan Pérez",
    "status": "pending",
    "status_display": "Pending",
    "total": "450000.00",
    "total_items": 3,
    "items": [
      {
        "id": 1,
        "product": {
          "id": 101,
          "woocommerce_product_id": 2045,
          "name": "Camiseta Básica",
          "price": "50000.00",
          "image_url": "https://example.com/image.jpg"
        },
        "quantity": 2,
        "unit_price": "50000.00",
        "subtotal": "100000.00",
        "product_name": "Camiseta Básica",
        "product_description": "Camiseta de algodón 100%",
        "created_at": "2025-10-03T10:30:00Z"
      },
      {
        "id": 2,
        "product": {
          "id": 102,
          "woocommerce_product_id": 2046,
          "name": "Pantalón Jean",
          "price": "175000.00",
          "image_url": "https://example.com/image2.jpg"
        },
        "quantity": 2,
        "unit_price": "175000.00",
        "subtotal": "350000.00",
        "product_name": "Pantalón Jean",
        "product_description": "Jean clásico azul",
        "created_at": "2025-10-03T10:30:00Z"
      }
    ],
    "shipping_address": "Calle 123 #45-67",
    "shipping_city": "Bogotá",
    "shipping_state": "Cundinamarca",
    "shipping_postal_code": "110111",
    "shipping_country": "Colombia",
    "phone_number": "+57 300 1234567",
    "full_shipping_address": "Calle 123 #45-67, Bogotá, Cundinamarca, 110111, Colombia",
    "notes": "Por favor llamar antes de entregar",
    "created_at": "2025-10-03T10:30:00Z",
    "updated_at": "2025-10-03T10:30:00Z",
    "shipped_at": null,
    "delivered_at": null
  }
}
```

### Respuestas de Error

**Código:** `400 Bad Request` - Carrito vacío
```json
{
  "error": "Invalid data",
  "details": {
    "non_field_errors": ["Cart is empty."]
  }
}
```

**Código:** `400 Bad Request` - Stock insuficiente
```json
{
  "error": "Invalid data",
  "details": {
    "non_field_errors": [
      "Insufficient stock for 'Camiseta Básica'. Available: 1, Required: 2"
    ]
  }
}
```

**Código:** `400 Bad Request` - Producto no disponible
```json
{
  "error": "Invalid data",
  "details": {
    "non_field_errors": ["Product 'Camiseta Básica' is no longer available."]
  }
}
```

**Código:** `500 Internal Server Error`
```json
{
  "error": "Failed to create order",
  "details": "Error message"
}
```

### Notas Importantes

- 🛒 La orden se crea a partir del carrito actual del usuario
- 📦 El stock de los productos se reduce automáticamente
- 🧹 El carrito se vacía después de crear la orden exitosamente
- 💾 Se guarda información histórica del producto al momento de la compra
- 🔢 El número de orden se genera automáticamente (formato: ORD + timestamp + random)
- ✅ La operación es atómica (todo o nada)

---

## 2. Listar Mis Órdenes

### Endpoint
```
GET /api/orders/
```

### Descripción
Obtiene el historial completo de órdenes del usuario autenticado, ordenadas por fecha de creación (más recientes primero).

### Autenticación
✅ Requerida (Usuario autenticado)

### Respuesta Exitosa

**Código:** `200 OK`

```json
{
  "orders": [
    {
      "id": 45,
      "order_number": "ORD123456ABCD1234",
      "status": "delivered",
      "status_display": "Delivered",
      "total": "450000.00",
      "total_items": 3,
      "created_at": "2025-10-01T10:30:00Z",
      "updated_at": "2025-10-03T14:00:00Z"
    },
    {
      "id": 44,
      "order_number": "ORD123456WXYZ5678",
      "status": "processing",
      "status_display": "Processing",
      "total": "125000.00",
      "total_items": 1,
      "created_at": "2025-09-28T15:45:00Z",
      "updated_at": "2025-09-28T16:00:00Z"
    }
  ]
}
```

### Campos de la Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID único de la orden |
| `order_number` | string | Número de orden único |
| `status` | string | Estado actual (pending, processing, shipped, delivered, cancelled, refunded) |
| `status_display` | string | Nombre legible del estado |
| `total` | decimal | Monto total de la orden |
| `total_items` | integer | Cantidad total de productos |
| `created_at` | datetime | Fecha de creación |
| `updated_at` | datetime | Última actualización |

---

## 3. Ver Detalles de una Orden

### Endpoint
```
GET /api/orders/<order_id>/
```

### Descripción
Obtiene información detallada de una orden específica del usuario, incluyendo todos los items, dirección de envío y fechas importantes.

### Autenticación
✅ Requerida (Usuario autenticado)

### Parámetros URL

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `order_id` | integer | ID de la orden |

### Respuesta Exitosa

**Código:** `200 OK`

```json
{
  "order": {
    "id": 45,
    "order_number": "ORD123456ABCD1234",
    "user": "Juan Pérez",
    "status": "shipped",
    "status_display": "Shipped",
    "total": "450000.00",
    "total_items": 3,
    "items": [
      {
        "id": 1,
        "product": {
          "id": 101,
          "woocommerce_product_id": 2045,
          "name": "Camiseta Básica",
          "price": "50000.00",
          "image_url": "https://example.com/image.jpg"
        },
        "quantity": 2,
        "unit_price": "50000.00",
        "subtotal": "100000.00",
        "product_name": "Camiseta Básica",
        "product_description": "Camiseta de algodón 100%",
        "created_at": "2025-10-01T10:30:00Z"
      }
    ],
    "shipping_address": "Calle 123 #45-67",
    "shipping_city": "Bogotá",
    "shipping_state": "Cundinamarca",
    "shipping_postal_code": "110111",
    "shipping_country": "Colombia",
    "phone_number": "+57 300 1234567",
    "full_shipping_address": "Calle 123 #45-67, Bogotá, Cundinamarca, 110111, Colombia",
    "notes": "Por favor llamar antes de entregar",
    "created_at": "2025-10-01T10:30:00Z",
    "updated_at": "2025-10-02T14:00:00Z",
    "shipped_at": "2025-10-02T14:00:00Z",
    "delivered_at": null
  }
}
```

### Respuesta de Error

**Código:** `404 Not Found`
```json
{
  "error": "Order not found"
}
```

---

## 4. Cancelar una Orden

### Endpoint
```
POST /api/orders/<order_id>/cancel/
```

### Descripción
Cancela una orden existente. Solo se pueden cancelar órdenes con estado `pending` o `processing`.

### Autenticación
✅ Requerida (Usuario autenticado)

### Parámetros URL

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `order_id` | integer | ID de la orden a cancelar |

### Request Body

```json
{
  "reason": "Ya no necesito el producto"
}
```

### Campos del Request

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `reason` | string | ❌ No | Motivo de cancelación (máximo 500 caracteres) |

### Respuesta Exitosa

**Código:** `200 OK`

```json
{
  "message": "Order cancelled successfully",
  "order": {
    "id": 45,
    "order_number": "ORD123456ABCD1234",
    "user": "Juan Pérez",
    "status": "cancelled",
    "status_display": "Cancelled",
    "total": "450000.00",
    "total_items": 3,
    "items": [...],
    "shipping_address": "Calle 123 #45-67",
    "notes": "Por favor llamar antes de entregar\n\nCancellation reason: Ya no necesito el producto",
    "created_at": "2025-10-01T10:30:00Z",
    "updated_at": "2025-10-03T10:00:00Z"
  }
}
```

### Respuestas de Error

**Código:** `404 Not Found`
```json
{
  "error": "Order not found"
}
```

**Código:** `400 Bad Request` - No se puede cancelar
```json
{
  "error": "Order cannot be cancelled"
}
```

**Código:** `400 Bad Request` - Estado no permite cancelación
```json
{
  "error": "Invalid data",
  "details": {
    "non_field_errors": ["Order with status 'shipped' cannot be cancelled."]
  }
}
```

### Reglas de Cancelación

- ✅ Se puede cancelar: `pending`, `processing`
- ❌ NO se puede cancelar: `shipped`, `delivered`, `cancelled`, `refunded`
- 📝 El motivo de cancelación se guarda en las notas de la orden

---

## 5. Rastrear Orden

### Endpoint
```
GET /api/orders/track/<order_number>/
```

### Descripción
Permite hacer seguimiento de una orden usando su número de orden. Muestra el estado actual, fechas importantes y estimación de entrega.

### Autenticación
✅ Requerida (Usuario autenticado)

### Parámetros URL

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `order_number` | string | Número de orden (ej: ORD123456ABCD1234) |

### Respuesta Exitosa

**Código:** `200 OK`

```json
{
  "tracking": {
    "id": 45,
    "order_number": "ORD123456ABCD1234",
    "status": "shipped",
    "status_display": "Shipped",
    "created_at": "2025-10-01T10:30:00Z",
    "shipped_at": "2025-10-02T14:00:00Z",
    "delivered_at": null,
    "can_be_cancelled": false,
    "estimated_delivery": "2025-10-07"
  }
}
```

### Campos de la Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID de la orden |
| `order_number` | string | Número de orden |
| `status` | string | Estado actual |
| `status_display` | string | Nombre legible del estado |
| `created_at` | datetime | Fecha de creación |
| `shipped_at` | datetime | Fecha de envío (null si no se ha enviado) |
| `delivered_at` | datetime | Fecha de entrega (null si no se ha entregado) |
| `can_be_cancelled` | boolean | Indica si la orden puede ser cancelada |
| `estimated_delivery` | date | Fecha estimada de entrega (solo si está enviada) |

### Respuesta de Error

**Código:** `404 Not Found`
```json
{
  "error": "Order not found"
}
```

### Notas

- 📅 La fecha estimada de entrega se calcula como 5 días después del envío
- ⏱️ Solo aparece `estimated_delivery` si la orden tiene estado `shipped`

---

## 6. Órdenes Recientes

### Endpoint
```
GET /api/orders/recent/
```

### Descripción
Obtiene las últimas 5 órdenes del usuario autenticado.

### Autenticación
✅ Requerida (Usuario autenticado)

### Respuesta Exitosa

**Código:** `200 OK`

```json
{
  "recent_orders": [
    {
      "id": 45,
      "order_number": "ORD123456ABCD1234",
      "status": "delivered",
      "status_display": "Delivered",
      "total": "450000.00",
      "total_items": 3,
      "created_at": "2025-10-01T10:30:00Z",
      "updated_at": "2025-10-03T14:00:00Z"
    },
    {
      "id": 44,
      "order_number": "ORD123456WXYZ5678",
      "status": "processing",
      "status_display": "Processing",
      "total": "125000.00",
      "total_items": 1,
      "created_at": "2025-09-28T15:45:00Z",
      "updated_at": "2025-09-28T16:00:00Z"
    }
  ]
}
```

---

## 7. Listar Todas las Órdenes (Admin)

### Endpoint
```
GET /api/orders/admin/all/
```

### Descripción
Obtiene todas las órdenes del sistema con filtros avanzados, búsqueda y paginación. Solo accesible para administradores.

### Autenticación
✅ Requerida (Administrador)

### Parámetros Query Opcionales

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `status` | string | Filtrar por estado (pending, processing, shipped, delivered, cancelled, refunded) |
| `date_from` | date | Fecha de inicio (formato: YYYY-MM-DD) |
| `date_to` | date | Fecha de fin (formato: YYYY-MM-DD) |
| `min_total` | decimal | Monto mínimo |
| `max_total` | decimal | Monto máximo |
| `search` | string | Buscar por email, nombre o número de orden |
| `ordering` | string | Ordenamiento (-created_at, created_at, -total, total, status) |
| `page` | integer | Número de página (default: 1) |
| `page_size` | integer | Items por página (default: 50, max: 100) |

### Ejemplo de Request

```
GET /api/orders/admin/all/?status=processing&date_from=2025-10-01&ordering=-total&page=1&page_size=20
```

### Respuesta Exitosa

**Código:** `200 OK`

```json
{
  "orders": [
    {
      "id": 45,
      "order_number": "ORD123456ABCD1234",
      "user": "Juan Pérez",
      "status": "processing",
      "status_display": "Processing",
      "total": "450000.00",
      "total_items": 3,
      "items": [...],
      "shipping_address": "Calle 123 #45-67",
      "shipping_city": "Bogotá",
      "shipping_state": "Cundinamarca",
      "shipping_postal_code": "110111",
      "shipping_country": "Colombia",
      "phone_number": "+57 300 1234567",
      "full_shipping_address": "Calle 123 #45-67, Bogotá, Cundinamarca, 110111, Colombia",
      "notes": "",
      "created_at": "2025-10-01T10:30:00Z",
      "updated_at": "2025-10-02T14:00:00Z",
      "shipped_at": null,
      "delivered_at": null
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 98,
    "has_next": true,
    "has_previous": false,
    "page_size": 20
  }
}
```

### Opciones de Ordenamiento

- `-created_at`: Más recientes primero (default)
- `created_at`: Más antiguas primero
- `-total`: Mayor total primero
- `total`: Menor total primero
- `status`: Por estado

---

## 8. Actualizar Estado de Orden (Admin)

### Endpoint
```
PATCH /api/orders/admin/<order_id>/status/
```

### Descripción
Actualiza el estado de una orden. Solo accesible para administradores. Las transiciones de estado están validadas según reglas de negocio.

### Autenticación
✅ Requerida (Administrador)

### Parámetros URL

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `order_id` | integer | ID de la orden |

### Request Body

```json
{
  "status": "shipped"
}
```

### Estados Disponibles

- `pending`: Pendiente
- `processing`: En proceso
- `shipped`: Enviada
- `delivered`: Entregada
- `cancelled`: Cancelada
- `refunded`: Reembolsada

### Transiciones de Estado Válidas

| Estado Actual | Puede cambiar a |
|--------------|-----------------|
| `pending` | `processing`, `cancelled` |
| `processing` | `shipped`, `cancelled` |
| `shipped` | `delivered` |
| `delivered` | `refunded` |
| `cancelled` | ❌ Ninguno |
| `refunded` | ❌ Ninguno |

### Respuesta Exitosa

**Código:** `200 OK`

```json
{
  "message": "Order status updated to Shipped",
  "order": {
    "id": 45,
    "order_number": "ORD123456ABCD1234",
    "user": "Juan Pérez",
    "status": "shipped",
    "status_display": "Shipped",
    "total": "450000.00",
    "total_items": 3,
    "items": [...],
    "shipped_at": "2025-10-03T10:30:00Z",
    "delivered_at": null
  }
}
```

### Respuestas de Error

**Código:** `404 Not Found`
```json
{
  "error": "Order not found"
}
```

**Código:** `400 Bad Request` - Transición inválida
```json
{
  "error": "Invalid data",
  "details": {
    "status": ["Cannot change status from 'shipped' to 'pending'."]
  }
}
```

### Comportamientos Especiales

- 📦 Al cambiar a `shipped`: Se registra automáticamente `shipped_at`
- 🎁 Al cambiar a `delivered`: Se registra automáticamente `delivered_at`
- ❌ Al cambiar a `cancelled`: Se ejecuta el método `cancel_order()`

---

## 9. Estadísticas de Órdenes (Admin)

### Endpoint
```
GET /api/orders/admin/statistics/
```

### Descripción
Obtiene estadísticas generales del sistema de órdenes, incluyendo totales, ingresos, órdenes por estado y métricas de los últimos 30 días.

### Autenticación
✅ Requerida (Administrador)

### Respuesta Exitosa

**Código:** `200 OK`

```json
{
  "statistics": {
    "total_orders": 542,
    "total_revenue": "45678900.00",
    "orders_by_status": [
      {
        "status": "pending",
        "count": 23
      },
      {
        "status": "processing",
        "count": 45
      },
      {
        "status": "shipped",
        "count": 67
      },
      {
        "status": "delivered",
        "count": 389
      },
      {
        "status": "cancelled",
        "count": 15
      },
      {
        "status": "refunded",
        "count": 3
      }
    ],
    "recent_30_days": {
      "orders": 78,
      "revenue": "6543210.00"
    },
    "requires_attention": {
      "pending_orders": 23,
      "processing_orders": 45
    }
  }
}
```

### Campos de la Respuesta

| Campo | Descripción |
|-------|-------------|
| `total_orders` | Total de órdenes en el sistema |
| `total_revenue` | Ingresos totales (solo órdenes delivered y shipped) |
| `orders_by_status` | Conteo de órdenes por cada estado |
| `recent_30_days.orders` | Órdenes de los últimos 30 días |
| `recent_30_days.revenue` | Ingresos de los últimos 30 días |
| `requires_attention.pending_orders` | Órdenes pendientes que requieren atención |
| `requires_attention.processing_orders` | Órdenes en proceso que requieren atención |

---

## Estados de Orden

### Ciclo de Vida de una Orden

```
pending → processing → shipped → delivered
           ↓                        ↓
        cancelled              refunded
```

### Descripción de Estados

| Estado | Descripción | Acciones Permitidas |
|--------|-------------|---------------------|
| `pending` | Orden recién creada, esperando confirmación | Cancelar, Pasar a processing |
| `processing` | Orden confirmada, siendo preparada | Cancelar, Pasar a shipped |
| `shipped` | Orden enviada al cliente | Pasar a delivered |
| `delivered` | Orden entregada exitosamente | Pasar a refunded |
| `cancelled` | Orden cancelada por el usuario o admin | Ninguna (estado final) |
| `refunded` | Orden reembolsada | Ninguna (estado final) |

---

## Estructura de Datos

### Modelo Order

```python
{
  "id": integer,
  "user": integer (Foreign Key),
  "order_number": string (único),
  "total": decimal,
  "status": string (choices),
  "email": string,
  "name": string,
  "country": string,
  "state": string,
  "city": string,
  "zipcode": string,
  "address_line_1": string,
  "address_line_2": string (opcional),
  "phone": string,
  "notes": text (opcional),
  "created_at": datetime,
  "updated_at": datetime,
  "shipped_at": datetime (nullable),
  "delivered_at": datetime (nullable)
}
```

### Modelo OrderItem

```python
{
  "id": integer,
  "order": integer (Foreign Key),
  "woocommerce_product_id": integer,
  "quantity": integer,
  "unit_price": decimal,
  "product_name": string,
  "product_description": text,
  "created_at": datetime,
  "updated_at": datetime
}
```

---

## Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| `200 OK` | Solicitud exitosa |
| `201 Created` | Orden creada exitosamente |
| `400 Bad Request` | Datos inválidos o reglas de negocio violadas |
| `401 Unauthorized` | No autenticado |
| `403 Forbidden` | No tiene permisos (endpoint admin) |
| `404 Not Found` | Orden no encontrada |
| `500 Internal Server Error` | Error del servidor |

---

## Errores Comunes

### 1. Carrito vacío
```json
{
  "error": "Invalid data",
  "details": {
    "non_field_errors": ["Cart is empty."]
  }
}
```
**Solución:** Agregar productos al carrito antes de crear la orden.

### 2. Stock insuficiente
```json
{
  "error": "Invalid data",
  "details": {
    "non_field_errors": [
      "Insufficient stock for 'Producto X'. Available: 2, Required: 5"
    ]
  }
}
```
**Solución:** Reducir la cantidad en el carrito o esperar reabastecimiento.

### 3. Producto no disponible
```json
{
  "error": "Invalid data",
  "details": {
    "non_field_errors": ["Product 'Producto X' is no longer available."]
  }
}
```
**Solución:** Remover el producto del carrito.

### 4. Transición de estado inválida
```json
{
  "error": "Invalid data",
  "details": {
    "status": ["Cannot change status from 'delivered' to 'processing'."]
  }
}
```
**Solución:** Verificar las transiciones de estado válidas.

### 5. No se puede cancelar
```json
{
  "error": "Order cannot be cancelled"
}
```
**Solución:** Solo se pueden cancelar órdenes en estado `pending` o `processing`.

---

## Características Importantes

### ✅ Validaciones Implementadas

- Validación de stock en tiempo real al crear orden
- Validación de disponibilidad de productos
- Validación de transiciones de estado
- Validación de permisos (usuario/admin)
- Validación de datos de envío

### 💾 Gestión de Datos

- Información histórica de productos preservada
- Generación automática de número de orden único
- Timestamps automáticos (created_at, updated_at, shipped_at, delivered_at)
- Operaciones atómicas con transacciones de base de datos

### 📊 Optimizaciones

- Índices en campos frecuentemente consultados
- Queries optimizados con select_related
- Paginación en listados largos
- Campos calculados en tiempo real (total_items, full_shipping_address)

### 🔒 Seguridad

- Autenticación requerida en todos los endpoints
- Usuarios solo pueden ver sus propias órdenes
- Endpoints administrativos protegidos con IsAdminUser
- Validación de propiedad de recursos

---

## Ejemplos de Uso

### Flujo Completo: Crear y Rastrear Orden

#### Paso 1: Agregar productos al carrito
```bash
POST /api/cart/add-product/
{
  "woocommerce_product_id": 2045,
  "quantity": 2
}
```

#### Paso 2: Crear la orden
```bash
POST /api/orders/create/
{
  "shipping_address": "Calle 123 #45-67",
  "shipping_city": "Bogotá",
  "shipping_state": "Cundinamarca",
  "shipping_postal_code": "110111",
  "shipping_country": "Colombia",
  "phone_number": "+57 300 1234567",
  "notes": "Por favor llamar antes de entregar"
}
```

#### Paso 3: Rastrear la orden
```bash
GET /api/orders/track/ORD123456ABCD1234/
```

#### Paso 4: Cancelar si es necesario
```bash
POST /api/orders/45/cancel/
{
  "reason": "Ya no necesito el producto"
}
```

### Flujo Admin: Gestionar Orden

#### Paso 1: Ver todas las órdenes pendientes
```bash
GET /api/orders/admin/all/?status=pending&page=1
```

#### Paso 2: Actualizar estado a processing
```bash
PATCH /api/orders/admin/45/status/
{
  "status": "processing"
}
```

#### Paso 3: Marcar como enviada
```bash
PATCH /api/orders/admin/45/status/
{
  "status": "shipped"
}
```

#### Paso 4: Verificar estadísticas
```bash
GET /api/orders/admin/statistics/
```

---

## Notas de Implementación

### Base de Datos

- **Modelo:** Order, OrderItem
- **Índices:** user + created_at, status, order_number
- **Relaciones:** Order → User (many-to-one), Order → OrderItem (one-to-many)
- **Constraints:** order_number único, unique_together en OrderItem

### Integración con WooCommerce

- Los productos vienen de WooCommerce
- Se guarda `woocommerce_product_id` para referencia
- Información del producto se preserva históricamente en OrderItem
- Stock se gestiona localmente después de la compra

### Transacciones

- Creación de orden usa `@transaction.atomic`
- Garantiza que si falla cualquier paso, todo se revierte
- Incluye: creación de orden, creación de items, reducción de stock, vaciado de carrito

---

## Soporte

Para más información o reportar problemas:
- Backend: Django + Django REST Framework
- Base de datos: PostgreSQL
- Autenticación: JWT Bearer Token

---

**Fecha de última actualización:** Octubre 3, 2025
**Versión de la API:** 1.0


