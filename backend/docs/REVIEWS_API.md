# API de Reviews - Documentación para Frontend

Esta documentación describe todos los endpoints relacionados con reseñas de productos de WooCommerce en CrushMe.

## Tabla de Contenidos

- [Información General](#información-general)
- [Consulta de Reviews](#consulta-de-reviews)
  - [Obtener Reviews de un Producto](#1-obtener-reviews-de-un-producto)
  - [Obtener Estadísticas de Reviews](#2-obtener-estadísticas-de-reviews)
  - [Obtener Detalle de una Review](#3-obtener-detalle-de-una-review)
  - [Verificar si Usuario ha Revisado un Producto](#4-verificar-si-usuario-ha-revisado-un-producto)
  - [Obtener Mis Reviews](#5-obtener-mis-reviews)
- [Gestión de Reviews](#gestión-de-reviews)
  - [Crear Review](#6-crear-review)
  - [Actualizar Review](#7-actualizar-review)
  - [Eliminar Review](#8-eliminar-review)

---

## Información General

### Base URL

```
http://your-domain.com/api/reviews/
```

### Notas Importantes

- **Todas las reviews pertenecen a un producto de WooCommerce** mediante su `woocommerce_product_id`
- **Privacidad y Anonimato**: El sistema expone únicamente el **username** de los usuarios registrados, nunca el nombre real ni datos personales, para mantener la privacidad
- **Reviews anónimas**: Los usuarios no autenticados pueden dejar reviews proporcionando `anonymous_name` y `anonymous_email`
- **Reviews autenticadas**: Los usuarios autenticados se identifican automáticamente por su username
- **Una review por usuario por producto**: Un usuario solo puede hacer una review por producto
- **Moderación**: Las reviews tienen un campo `is_active` para moderación por administradores

---

## Consulta de Reviews

### 1. Obtener Reviews de un Producto

Obtiene todas las reviews de un producto específico de WooCommerce.

**Endpoint:** `GET /reviews/product/<woocommerce_product_id>/`

**Autenticación:** No requerida

**Parámetros de URL:**
- `woocommerce_product_id` (integer): ID del producto en WooCommerce

**Query Parameters:**
- `active_only` (boolean, opcional): Solo mostrar reviews activas/aprobadas. Default: `true`
  - Valores aceptados: `"true"`, `"false"` (como string)

**Ejemplo de Request:**
```
GET /reviews/product/123/?active_only=true
```

**Response (200 OK):**
```json
{
  "success": true,
  "woocommerce_product_id": 123,
  "total_reviews": 15,
  "reviews": [
    {
      "id": 1,
      "woocommerce_product_id": 123,
      "reviewer_name": "juanperez123",
      "rating": 5,
      "title": "Excelente producto",
      "comment": "Me encantó este producto, superó mis expectativas. La calidad es excepcional.",
      "is_verified_purchase": true,
      "is_user_review": false,
      "created_at": "2025-10-01T10:30:00Z",
      "updated_at": "2025-10-01T10:30:00Z"
    },
    {
      "id": 2,
      "woocommerce_product_id": 123,
      "reviewer_name": "mariagarcia456",
      "rating": 4,
      "title": "Muy bueno",
      "comment": "Buen producto, llegó rápido y en perfectas condiciones.",
      "is_verified_purchase": false,
      "is_user_review": true,
      "created_at": "2025-09-28T15:20:00Z",
      "updated_at": "2025-09-28T15:20:00Z"
    }
  ]
}
```

**Campos de la Response:**
- `success` (boolean): Indica si la operación fue exitosa
- `woocommerce_product_id` (integer): ID del producto consultado
- `total_reviews` (integer): Número total de reviews
- `reviews` (array): Lista de reviews con los siguientes campos:
  - `id` (integer): ID único de la review
  - `woocommerce_product_id` (integer): ID del producto en WooCommerce
  - `reviewer_name` (string): Username del revisor (usuario registrado o anónimo, **no expone nombre real para mantener privacidad**)
  - `rating` (integer): Calificación de 1 a 5 estrellas
  - `title` (string): Título de la review
  - `comment` (string): Comentario detallado
  - `is_verified_purchase` (boolean): Si es una compra verificada
  - `is_user_review` (boolean): Si la review pertenece al usuario actual (solo si está autenticado)
  - `created_at` (datetime): Fecha de creación
  - `updated_at` (datetime): Fecha de última actualización

---

### 2. Obtener Estadísticas de Reviews

Obtiene estadísticas agregadas de las reviews de un producto: total de reviews, promedio de calificación y distribución de ratings.

**Endpoint:** `GET /reviews/product/<woocommerce_product_id>/stats/`

**Autenticación:** No requerida

**Parámetros de URL:**
- `woocommerce_product_id` (integer): ID del producto en WooCommerce

**Ejemplo de Request:**
```
GET /reviews/product/123/stats/
```

**Response (200 OK):**
```json
{
  "success": true,
  "woocommerce_product_id": 123,
  "stats": {
    "total_reviews": 15,
    "average_rating": 4.3,
    "rating_distribution": {
      "1": 0,
      "2": 1,
      "3": 2,
      "4": 5,
      "5": 7
    }
  }
}
```

**Campos de la Response:**
- `success` (boolean): Indica si la operación fue exitosa
- `woocommerce_product_id` (integer): ID del producto consultado
- `stats` (object): Objeto con estadísticas:
  - `total_reviews` (integer): Número total de reviews
  - `average_rating` (float): Promedio de calificación (0.0 - 5.0)
  - `rating_distribution` (object): Distribución de calificaciones
    - Claves: `"1"`, `"2"`, `"3"`, `"4"`, `"5"` (estrellas)
    - Valores: Cantidad de reviews con esa calificación

---

### 3. Obtener Detalle de una Review

Obtiene información detallada de una review específica.

**Endpoint:** `GET /reviews/<review_id>/`

**Autenticación:** No requerida

**Parámetros de URL:**
- `review_id` (integer): ID de la review

**Ejemplo de Request:**
```
GET /reviews/1/
```

**Response (200 OK):**
```json
{
  "success": true,
  "review": {
    "id": 1,
    "woocommerce_product_id": 123,
    "user": 5,
    "reviewer_name": "juanperez123",
    "reviewer_email": "juan@ejemplo.com",
    "rating": 5,
    "title": "Excelente producto",
    "comment": "Me encantó este producto, superó mis expectativas.",
    "is_verified_purchase": true,
    "is_active": true,
    "is_user_review": false,
    "created_at": "2025-10-01T10:30:00Z",
    "updated_at": "2025-10-01T10:30:00Z"
  }
}
```

**Errores Comunes:**
- `404`: Review no encontrada

---

### 4. Verificar si Usuario ha Revisado un Producto

Verifica si el usuario autenticado ya ha dejado una review para un producto específico.

**Endpoint:** `GET /reviews/product/<woocommerce_product_id>/check/`

**Autenticación:** Requerida (JWT Token)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Parámetros de URL:**
- `woocommerce_product_id` (integer): ID del producto en WooCommerce

**Ejemplo de Request:**
```
GET /reviews/product/123/check/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response - Usuario SÍ ha revisado (200 OK):**
```json
{
  "success": true,
  "has_reviewed": true,
  "review": {
    "id": 1,
    "woocommerce_product_id": 123,
    "user": 5,
    "reviewer_name": "juanperez123",
    "reviewer_email": "juan@ejemplo.com",
    "rating": 5,
    "title": "Excelente producto",
    "comment": "Me encantó este producto.",
    "is_verified_purchase": true,
    "is_active": true,
    "is_user_review": true,
    "created_at": "2025-10-01T10:30:00Z",
    "updated_at": "2025-10-01T10:30:00Z"
  }
}
```

**Response - Usuario NO ha revisado (200 OK):**
```json
{
  "success": true,
  "has_reviewed": false,
  "review": null
}
```

**Errores Comunes:**
- `401`: Usuario no autenticado

---

### 5. Obtener Mis Reviews

Obtiene todas las reviews creadas por el usuario autenticado.

**Endpoint:** `GET /reviews/user/my-reviews/`

**Autenticación:** Requerida (JWT Token)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Ejemplo de Request:**
```
GET /reviews/user/my-reviews/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response (200 OK):**
```json
{
  "success": true,
  "total_reviews": 3,
  "reviews": [
    {
      "id": 1,
      "woocommerce_product_id": 123,
      "reviewer_name": "juanperez123",
      "rating": 5,
      "title": "Excelente producto",
      "comment": "Me encantó este producto.",
      "is_verified_purchase": true,
      "is_user_review": true,
      "created_at": "2025-10-01T10:30:00Z",
      "updated_at": "2025-10-01T10:30:00Z"
    },
    {
      "id": 5,
      "woocommerce_product_id": 456,
      "reviewer_name": "juanperez123",
      "rating": 4,
      "title": "Buena compra",
      "comment": "Cumple con lo esperado.",
      "is_verified_purchase": false,
      "is_user_review": true,
      "created_at": "2025-09-20T14:15:00Z",
      "updated_at": "2025-09-20T14:15:00Z"
    }
  ]
}
```

**Errores Comunes:**
- `401`: Usuario no autenticado

---

## Gestión de Reviews

### 6. Crear Review

Crea una nueva review para un producto de WooCommerce. Puede ser creada por usuarios autenticados o anónimos.

**Endpoint:** `POST /reviews/`

**Autenticación:** Opcional (permite usuarios anónimos)

**Headers (si está autenticado):**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body - Usuario Autenticado:**
```json
{
  "woocommerce_product_id": 123,
  "rating": 5,
  "title": "Excelente producto",
  "comment": "Me encantó este producto, superó todas mis expectativas. La calidad es excepcional y el envío fue muy rápido."
}
```

**Request Body - Usuario Anónimo:**
```json
{
  "woocommerce_product_id": 123,
  "rating": 4,
  "title": "Muy bueno",
  "comment": "Buen producto, cumple con lo que promete.",
  "anonymous_name": "María García",
  "anonymous_email": "maria@ejemplo.com"
}
```

**Campos del Request:**
- `woocommerce_product_id` (integer, **requerido**): ID del producto en WooCommerce
- `rating` (integer, **requerido**): Calificación de 1 a 5 estrellas
- `comment` (string, **requerido**): Comentario detallado de la review
- `title` (string, opcional): Título de la review
- `anonymous_name` (string, **requerido si no autenticado**): Nombre del usuario anónimo
- `anonymous_email` (string, **requerido si no autenticado**): Email del usuario anónimo

**Validaciones:**
- `rating`: Debe estar entre 1 y 5
- `woocommerce_product_id`: Debe ser un entero válido
- `comment`: Campo requerido, no puede estar vacío
- Si usuario autenticado: No puede haber otra review del mismo usuario para el mismo producto
- Si usuario anónimo: `anonymous_name` y `anonymous_email` son requeridos

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Reseña creada exitosamente",
  "review": {
    "id": 1,
    "woocommerce_product_id": 123,
    "user": 5,
    "reviewer_name": "juanperez123",
    "reviewer_email": "juan@ejemplo.com",
    "rating": 5,
    "title": "Excelente producto",
    "comment": "Me encantó este producto, superó todas mis expectativas.",
    "is_verified_purchase": false,
    "is_active": true,
    "is_user_review": true,
    "created_at": "2025-10-01T10:30:00Z",
    "updated_at": "2025-10-01T10:30:00Z"
  }
}
```

**Errores Comunes:**

- `400 - Calificación inválida`:
```json
{
  "success": false,
  "errors": {
    "rating": ["La calificación debe estar entre 1 y 5 estrellas"]
  }
}
```

- `400 - Usuario ya revisó el producto`:
```json
{
  "success": false,
  "errors": {
    "non_field_errors": ["Ya has hecho una reseña de este producto. Puedes editarla o eliminarla."]
  }
}
```

- `400 - Campos requeridos para anónimos`:
```json
{
  "success": false,
  "errors": {
    "anonymous_name": ["El nombre es requerido para usuarios anónimos"],
    "anonymous_email": ["El email es requerido para usuarios anónimos"]
  }
}
```

---

### 7. Actualizar Review

Actualiza una review existente. Solo el propietario de la review puede actualizarla.

**Endpoint:** `PUT /reviews/<review_id>/update/` o `PATCH /reviews/<review_id>/update/`

**Autenticación:** Requerida (JWT Token)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Parámetros de URL:**
- `review_id` (integer): ID de la review a actualizar

**Request Body:**
```json
{
  "rating": 4,
  "title": "Actualicé mi opinión",
  "comment": "Después de usarlo más tiempo, sigue siendo muy bueno pero encontré algunas áreas de mejora."
}
```

**Campos del Request (todos opcionales con PATCH):**
- `rating` (integer): Nueva calificación de 1 a 5 estrellas
- `title` (string): Nuevo título
- `comment` (string): Nuevo comentario

**Validaciones:**
- Solo el propietario de la review puede actualizarla
- `rating`: Debe estar entre 1 y 5 (si se proporciona)

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Reseña actualizada exitosamente",
  "review": {
    "id": 1,
    "woocommerce_product_id": 123,
    "user": 5,
    "reviewer_name": "juanperez123",
    "reviewer_email": "juan@ejemplo.com",
    "rating": 4,
    "title": "Actualicé mi opinión",
    "comment": "Después de usarlo más tiempo, sigue siendo muy bueno.",
    "is_verified_purchase": true,
    "is_active": true,
    "is_user_review": true,
    "created_at": "2025-10-01T10:30:00Z",
    "updated_at": "2025-10-08T16:45:00Z"
  }
}
```

**Errores Comunes:**

- `401`: Usuario no autenticado
- `403 - Sin permisos`:
```json
{
  "success": false,
  "error": "No tienes permiso para editar esta reseña"
}
```

- `404`: Review no encontrada

- `400 - Calificación inválida`:
```json
{
  "success": false,
  "errors": {
    "rating": ["La calificación debe estar entre 1 y 5 estrellas"]
  }
}
```

---

### 8. Eliminar Review

Elimina una review existente. Solo el propietario de la review puede eliminarla.

**Endpoint:** `DELETE /reviews/<review_id>/delete/`

**Autenticación:** Requerida (JWT Token)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Parámetros de URL:**
- `review_id` (integer): ID de la review a eliminar

**Ejemplo de Request:**
```
DELETE /reviews/1/delete/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Reseña eliminada exitosamente",
  "woocommerce_product_id": 123
}
```

**Errores Comunes:**

- `401`: Usuario no autenticado

- `403 - Sin permisos`:
```json
{
  "success": false,
  "error": "No tienes permiso para eliminar esta reseña"
}
```

- `404`: Review no encontrada

---

## Ejemplos de Uso Completos

### Ejemplo 1: Flujo de Usuario Autenticado

```javascript
// 1. Verificar si el usuario ya revisó el producto
const checkResponse = await fetch('http://api.crushme.com/api/reviews/product/123/check/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
const checkData = await checkResponse.json();

if (!checkData.has_reviewed) {
  // 2. Si no ha revisado, crear una nueva review
  const createResponse = await fetch('http://api.crushme.com/api/reviews/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      woocommerce_product_id: 123,
      rating: 5,
      title: "Excelente producto",
      comment: "Me encantó, lo recomiendo mucho."
    })
  });
  const createData = await createResponse.json();
  console.log('Review creada:', createData.review);
} else {
  console.log('Ya has revisado este producto:', checkData.review);
}
```

### Ejemplo 2: Flujo de Usuario Anónimo

```javascript
// Crear review como usuario anónimo
const response = await fetch('http://api.crushme.com/api/reviews/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    woocommerce_product_id: 123,
    rating: 4,
    title: "Buen producto",
    comment: "Cumple con lo esperado.",
    anonymous_name: "María García",
    anonymous_email: "maria@ejemplo.com"
  })
});
const data = await response.json();
console.log('Review creada:', data.review);
```

### Ejemplo 3: Mostrar Reviews con Estadísticas

```javascript
// Obtener estadísticas del producto
const statsResponse = await fetch('http://api.crushme.com/api/reviews/product/123/stats/');
const statsData = await statsResponse.json();
console.log('Promedio:', statsData.stats.average_rating);
console.log('Total:', statsData.stats.total_reviews);

// Obtener todas las reviews
const reviewsResponse = await fetch('http://api.crushme.com/api/reviews/product/123/');
const reviewsData = await reviewsResponse.json();
console.log('Reviews:', reviewsData.reviews);
```

### Ejemplo 4: Actualizar una Review

```javascript
// Actualizar review existente
const response = await fetch('http://api.crushme.com/api/reviews/1/update/', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    rating: 4,
    comment: "Actualicé mi opinión después de usarlo más tiempo."
  })
});
const data = await response.json();
console.log('Review actualizada:', data.review);
```

---

## Notas para Desarrollo Frontend

### Manejo de Errores

Todos los endpoints retornan un campo `success` (boolean) que indica si la operación fue exitosa. En caso de error, se incluye información adicional:

- **Errores de validación**: Campo `errors` con detalles específicos
- **Errores de permisos**: Campo `error` con mensaje descriptivo
- **Errores HTTP estándar**: 400, 401, 403, 404, 500

### Autenticación

- Endpoints públicos: No requieren autenticación
- Endpoints protegidos: Requieren JWT token en el header `Authorization: Bearer <token>`
- Los usuarios anónimos pueden crear reviews proporcionando `anonymous_name` y `anonymous_email`

### Consideraciones de UI/UX

1. **Restricción de una review por usuario**: Antes de mostrar el formulario de crear review, verifica si el usuario ya revisó el producto usando el endpoint `/check/`

2. **Edición vs Creación**: Si el usuario ya tiene una review, muestra opciones de editar/eliminar en lugar de crear nueva

3. **Validación en tiempo real**: Valida el rating (1-5) antes de enviar al backend

4. **Indicador de compra verificada**: Muestra un badge especial para reviews con `is_verified_purchase: true`

5. **Reviews del usuario actual**: Usa el campo `is_user_review` para destacar o permitir edición de reviews del usuario

6. **Distribución de ratings**: Usa las estadísticas para mostrar gráficos de barras o estrellas visuales

### Performance

- Las reviews están indexadas por `woocommerce_product_id` para consultas rápidas
- Usa el parámetro `active_only=true` para mostrar solo reviews aprobadas en producción
- Considera implementar paginación en el frontend si un producto tiene muchas reviews

---

## Contacto y Soporte

Para reportar problemas o solicitar nuevas funcionalidades relacionadas con el sistema de reviews, contacta al equipo de desarrollo.

---

**Última actualización:** Octubre 2025
**Versión:** 1.0

