# Documentación - Endpoints de Reviews (Reseñas)

## Descripción General
Sistema de reseñas **exclusivo para productos de WooCommerce**. Las reseñas se identifican por el `woocommerce_product_id` (ID del producto en WooCommerce), no por el modelo Product local de Django.

## Características
- ✅ Soporte para usuarios registrados y anónimos
- ✅ Calificación de 1 a 5 estrellas
- ✅ Un usuario solo puede hacer una reseña por producto
- ✅ Moderación de reseñas (is_active)
- ✅ Indicador de compra verificada
- ✅ Estadísticas de reviews por producto

---

## Endpoints Disponibles

### 1. Obtener Reviews de un Producto

**URL:** `GET /api/reviews/product/<woocommerce_product_id>/`

**Descripción:** Obtiene todas las reseñas de un producto específico de WooCommerce.

**Query Parameters:**
- `active_only` (opcional, default: `true`): Solo mostrar reseñas aprobadas

**Autenticación:** No requiere

**Respuesta Exitosa (200 OK):**
```json
{
  "success": true,
  "woocommerce_product_id": 19300,
  "total_reviews": 15,
  "reviews": [
    {
      "id": 1,
      "woocommerce_product_id": 19300,
      "reviewer_name": "Juan Pérez",
      "rating": 5,
      "title": "Excelente producto",
      "comment": "Me encantó, superó mis expectativas...",
      "is_verified_purchase": true,
      "is_user_review": false,
      "created_at": "2025-10-01T12:00:00Z",
      "updated_at": "2025-10-01T12:00:00Z"
    }
  ]
}
```

---

### 2. Obtener Estadísticas de Reviews de un Producto

**URL:** `GET /api/reviews/product/<woocommerce_product_id>/stats/`

**Descripción:** Obtiene estadísticas de las reseñas de un producto.

**Autenticación:** No requiere

**Respuesta Exitosa (200 OK):**
```json
{
  "success": true,
  "woocommerce_product_id": 19300,
  "stats": {
    "total_reviews": 15,
    "average_rating": 4.53,
    "rating_distribution": {
      "stars_5": 10,
      "stars_4": 3,
      "stars_3": 1,
      "stars_2": 1,
      "stars_1": 0
    }
  }
}
```

---

### 3. Crear una Reseña

**URL:** `POST /api/reviews/`

**Descripción:** Crea una nueva reseña para un producto de WooCommerce.

**Autenticación:** No requiere (pero se recomienda estar autenticado)

**Body (Usuario Autenticado):**
```json
{
  "woocommerce_product_id": 19300,
  "rating": 5,
  "title": "Excelente producto",
  "comment": "Me encantó, superó mis expectativas..."
}
```

**Body (Usuario Anónimo):**
```json
{
  "woocommerce_product_id": 19300,
  "rating": 5,
  "title": "Muy bueno",
  "comment": "Lo recomiendo...",
  "anonymous_name": "María García",
  "anonymous_email": "maria@example.com"
}
```

**Campos:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `woocommerce_product_id` | integer | Sí | ID del producto en WooCommerce |
| `rating` | integer | Sí | Calificación de 1 a 5 estrellas |
| `comment` | string | Sí | Comentario de la reseña |
| `title` | string | No | Título de la reseña |
| `anonymous_name` | string | Sí* | Nombre (solo para anónimos) |
| `anonymous_email` | string | Sí* | Email (solo para anónimos) |

*Requerido solo si el usuario no está autenticado

**Respuesta Exitosa (201 Created):**
```json
{
  "success": true,
  "message": "Reseña creada exitosamente",
  "review": {
    "id": 16,
    "woocommerce_product_id": 19300,
    "user": 5,
    "reviewer_name": "Juan Pérez",
    "reviewer_email": "juan@example.com",
    "rating": 5,
    "title": "Excelente producto",
    "comment": "Me encantó...",
    "is_verified_purchase": false,
    "is_active": true,
    "is_user_review": true,
    "created_at": "2025-10-01T14:30:00Z",
    "updated_at": "2025-10-01T14:30:00Z"
  }
}
```

**Respuesta de Error (400 Bad Request):**
```json
{
  "success": false,
  "errors": {
    "non_field_errors": ["Ya has hecho una reseña de este producto. Puedes editarla o eliminarla."]
  }
}
```

---

### 4. Verificar si el Usuario ya Revisó el Producto

**URL:** `GET /api/reviews/product/<woocommerce_product_id>/check/`

**Descripción:** Verifica si el usuario autenticado ya ha revisado el producto.

**Autenticación:** Requerida

**Respuesta Exitosa (200 OK) - Ya revisó:**
```json
{
  "success": true,
  "has_reviewed": true,
  "review": {
    "id": 16,
    "woocommerce_product_id": 19300,
    "user": 5,
    "reviewer_name": "Juan Pérez",
    "rating": 5,
    "title": "Excelente producto",
    "comment": "Me encantó...",
    "is_verified_purchase": false,
    "is_active": true,
    "is_user_review": true,
    "created_at": "2025-10-01T14:30:00Z",
    "updated_at": "2025-10-01T14:30:00Z"
  }
}
```

**Respuesta Exitosa (200 OK) - No ha revisado:**
```json
{
  "success": true,
  "has_reviewed": false,
  "review": null
}
```

---

### 5. Obtener Detalle de una Reseña

**URL:** `GET /api/reviews/<review_id>/`

**Descripción:** Obtiene los detalles de una reseña específica.

**Autenticación:** No requiere

**Respuesta Exitosa (200 OK):**
```json
{
  "success": true,
  "review": {
    "id": 16,
    "woocommerce_product_id": 19300,
    "user": 5,
    "reviewer_name": "Juan Pérez",
    "reviewer_email": "juan@example.com",
    "rating": 5,
    "title": "Excelente producto",
    "comment": "Me encantó...",
    "is_verified_purchase": false,
    "is_active": true,
    "is_user_review": true,
    "created_at": "2025-10-01T14:30:00Z",
    "updated_at": "2025-10-01T14:30:00Z"
  }
}
```

---

### 6. Actualizar una Reseña

**URL:** `PUT/PATCH /api/reviews/<review_id>/update/`

**Descripción:** Actualiza una reseña existente. Solo el propietario puede actualizar.

**Autenticación:** Requerida

**Body:**
```json
{
  "rating": 4,
  "title": "Buen producto",
  "comment": "Después de usarlo más tiempo, actualizo mi reseña..."
}
```

**Campos Actualizables:**
- `rating`: Calificación (1-5)
- `title`: Título
- `comment`: Comentario

**Respuesta Exitosa (200 OK):**
```json
{
  "success": true,
  "message": "Reseña actualizada exitosamente",
  "review": {
    "id": 16,
    "woocommerce_product_id": 19300,
    "user": 5,
    "reviewer_name": "Juan Pérez",
    "rating": 4,
    "title": "Buen producto",
    "comment": "Después de usarlo más tiempo...",
    "is_verified_purchase": false,
    "is_active": true,
    "is_user_review": true,
    "created_at": "2025-10-01T14:30:00Z",
    "updated_at": "2025-10-01T15:45:00Z"
  }
}
```

**Respuesta de Error (403 Forbidden):**
```json
{
  "success": false,
  "error": "No tienes permiso para editar esta reseña"
}
```

---

### 7. Eliminar una Reseña

**URL:** `DELETE /api/reviews/<review_id>/delete/`

**Descripción:** Elimina una reseña. Solo el propietario puede eliminar.

**Autenticación:** Requerida

**Respuesta Exitosa (200 OK):**
```json
{
  "success": true,
  "message": "Reseña eliminada exitosamente",
  "woocommerce_product_id": 19300
}
```

**Respuesta de Error (403 Forbidden):**
```json
{
  "success": false,
  "error": "No tienes permiso para eliminar esta reseña"
}
```

---

### 8. Obtener Todas las Reseñas del Usuario

**URL:** `GET /api/reviews/user/my-reviews/`

**Descripción:** Obtiene todas las reseñas creadas por el usuario autenticado.

**Autenticación:** Requerida

**Respuesta Exitosa (200 OK):**
```json
{
  "success": true,
  "total_reviews": 5,
  "reviews": [
    {
      "id": 16,
      "woocommerce_product_id": 19300,
      "reviewer_name": "Juan Pérez",
      "rating": 5,
      "title": "Excelente producto",
      "comment": "Me encantó...",
      "is_verified_purchase": false,
      "is_user_review": true,
      "created_at": "2025-10-01T14:30:00Z",
      "updated_at": "2025-10-01T14:30:00Z"
    }
  ]
}
```

---

## Resumen de URLs

| Método | URL | Descripción | Auth |
|--------|-----|-------------|------|
| GET | `/api/reviews/product/<wc_id>/` | Listar reviews de un producto | No |
| GET | `/api/reviews/product/<wc_id>/stats/` | Estadísticas de reviews | No |
| GET | `/api/reviews/product/<wc_id>/check/` | Verificar si usuario ya revisó | Sí |
| GET | `/api/reviews/<id>/` | Detalle de una review | No |
| POST | `/api/reviews/` | Crear review | No* |
| PUT/PATCH | `/api/reviews/<id>/update/` | Actualizar review | Sí |
| DELETE | `/api/reviews/<id>/delete/` | Eliminar review | Sí |
| GET | `/api/reviews/user/my-reviews/` | Reviews del usuario | Sí |

*No requiere autenticación, pero se recomienda

---

## Notas Importantes

1. **Solo productos de WooCommerce:** Las reviews solo funcionan con `woocommerce_product_id`, no con el modelo Product local.

2. **Una review por usuario:** Un usuario autenticado solo puede crear una reseña por producto. Si intenta crear otra, recibirá un error.

3. **Usuarios anónimos:** Pueden crear reviews proporcionando `anonymous_name` y `anonymous_email`.

4. **Moderación:** Las reviews tienen un campo `is_active` que permite aprobar/rechazar reviews desde el admin.

5. **Compra verificada:** El campo `is_verified_purchase` debe ser marcado manualmente desde el admin cuando se confirme que el usuario compró el producto.

6. **Permisos de edición/eliminación:** Solo el propietario de una review puede editarla o eliminarla.

---

**Última actualización:** Octubre 2025  
**Versión de la API:** 1.0


