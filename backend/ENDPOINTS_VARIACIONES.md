# Endpoints de Variaciones de Productos WooCommerce

## Nuevos Endpoints Implementados

### 1. Obtener todas las variaciones de un producto

**Endpoint:**
```
GET /api/products/woocommerce/products/{product_id}/variations/
```

**Parámetros de consulta (Query params):**
- `per_page`: Variaciones por página (máximo 100, default 100)
- `page`: Número de página (default 1)

**Ejemplo de uso:**
```bash
GET /api/products/woocommerce/products/19425/variations/
GET /api/products/woocommerce/products/19425/variations/?per_page=50&page=1
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "message": "Variaciones del producto 19425 obtenidas exitosamente",
  "data": [
    {
      "id": 19427,
      "type": "variation",
      "sku": "EK-CLV-005-TRIO-FRR-SAC",
      "price": "3190",
      "regular_price": "3190",
      "sale_price": "",
      "stock_quantity": 0,
      "stock_status": "outofstock",
      "attributes": [
        {
          "id": 0,
          "name": "Tamaño",
          "slug": "tamano",
          "option": "Sachet"
        }
      ],
      "image": {
        "id": 25286,
        "src": "https://desarrollo.distrisex.com/wp-content/uploads/2023/09/lubricante-intimo-trio-erotika-distrisexcolombia-distrisex.jpg",
        "name": "lubricante-intimo-trio-erotika-distrisexcolombia-distrisex",
        "alt": "Lubricante Íntimo Trío Erotika-DistriSexEcuador-DistriSex"
      },
      ...
    }
  ],
  "total_variations": 2,
  "pagination_info": {
    "page": 1,
    "per_page": 100,
    "product_id": 19425
  },
  "api_info": {
    "status_code": 200,
    "headers": {...}
  }
}
```

---

### 2. Obtener una variación específica

**Endpoint:**
```
GET /api/products/woocommerce/products/{product_id}/variations/{variation_id}/
```

**Ejemplo de uso:**
```bash
GET /api/products/woocommerce/products/19425/variations/19427/
GET /api/products/woocommerce/products/19425/variations/19426/
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "message": "Variación 19427 del producto 19425 obtenida exitosamente",
  "data": {
    "id": 19427,
    "type": "variation",
    "date_created": "2023-09-04T17:42:10",
    "date_modified": "2025-04-08T12:04:51",
    "description": "<h5>...",
    "permalink": "https://desarrollo.distrisex.com/producto/lubricante-intimo-trio-erotika/?attribute_tamano=Sachet",
    "sku": "EK-CLV-005-TRIO-FRR-SAC",
    "price": "3190",
    "regular_price": "3190",
    "sale_price": "",
    "on_sale": false,
    "stock_quantity": 0,
    "stock_status": "outofstock",
    "manage_stock": true,
    "dimensions": {
      "length": "30",
      "width": "30",
      "height": "30"
    },
    "image": {
      "id": 25286,
      "src": "https://desarrollo.distrisex.com/wp-content/uploads/2023/09/lubricante-intimo-trio-erotika-distrisexcolombia-distrisex.jpg",
      "name": "lubricante-intimo-trio-erotika-distrisexcolombia-distrisex",
      "alt": "Lubricante Íntimo Trío Erotika-DistriSexEcuador-DistriSex"
    },
    "attributes": [
      {
        "id": 0,
        "name": "Tamaño",
        "slug": "tamano",
        "option": "Sachet"
      }
    ],
    "meta_data": [...]
  },
  "api_info": {
    "status_code": 200,
    "headers": {...}
  }
}
```

---

## Respuestas de Error

### Error 400 - Bad Request
```json
{
  "error": "ID de producto inválido"
}
```

### Error 502 - Bad Gateway (Error de WooCommerce)
```json
{
  "success": false,
  "error": "API returned status 404",
  "status_code": 404,
  "details": "..."
}
```

### Error 500 - Internal Server Error
```json
{
  "error": "Error interno del servidor",
  "details": "..."
}
```

---

## Campos Importantes de las Variaciones

### Información Básica
- `id`: ID de la variación
- `type`: Siempre "variation"
- `sku`: Código SKU único de la variación
- `permalink`: URL de la variación

### Precios
- `price`: Precio actual
- `regular_price`: Precio regular
- `sale_price`: Precio en oferta (puede estar vacío)
- `on_sale`: Boolean - si está en oferta

### Stock
- `stock_quantity`: Cantidad disponible
- `stock_status`: Estado (instock, outofstock, onbackorder)
- `manage_stock`: Si se gestiona el stock
- `backorders`: Permitir pedidos pendientes

### Atributos de la Variación
Array con los atributos que definen esta variación:
```json
"attributes": [
  {
    "id": 0,
    "name": "Tamaño",
    "slug": "tamano",
    "option": "Sachet"
  },
  {
    "id": 0,
    "name": "Color",
    "slug": "color",
    "option": "Rojo"
  }
]
```

### Imagen
Cada variación puede tener su propia imagen:
```json
"image": {
  "id": 25286,
  "src": "https://...",
  "name": "...",
  "alt": "..."
}
```

---

## Notas de Implementación

1. **Traducción automática**: Los campos de texto se traducen automáticamente según el idioma solicitado en el header `Accept-Language`.

2. **Paginación**: Las variaciones están paginadas con un máximo de 100 por página.

3. **Compatibilidad**: Estos endpoints son compatibles con la API REST de WooCommerce v3.

4. **Acceso público**: Ambos endpoints son públicos (`AllowAny`), no requieren autenticación.

---

## Ejemplos de Uso desde el Frontend

### JavaScript/Fetch
```javascript
// Obtener todas las variaciones
fetch('http://localhost:8000/api/products/woocommerce/products/19425/variations/')
  .then(response => response.json())
  .then(data => {
    console.log('Variaciones:', data.data);
  });

// Obtener una variación específica
fetch('http://localhost:8000/api/products/woocommerce/products/19425/variations/19427/')
  .then(response => response.json())
  .then(data => {
    console.log('Variación:', data.data);
  });
```

### cURL
```bash
# Obtener todas las variaciones
curl -X GET "http://localhost:8000/api/products/woocommerce/products/19425/variations/"

# Obtener variación específica
curl -X GET "http://localhost:8000/api/products/woocommerce/products/19425/variations/19427/"

# Con paginación
curl -X GET "http://localhost:8000/api/products/woocommerce/products/19425/variations/?per_page=50&page=1"
```

---

## Casos de Uso Comunes

1. **Mostrar opciones de producto**: Cuando un producto tiene múltiples tamaños, colores, etc.
2. **Verificar disponibilidad**: Consultar el stock de cada variación.
3. **Mostrar precios diferentes**: Cada variación puede tener su propio precio.
4. **Imágenes por variación**: Mostrar la imagen correspondiente a cada variación.

