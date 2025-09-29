# 🛒 Integración con WooCommerce - Documentación de API

## 📋 Descripción General

Esta integración permite conectar tu aplicación CrushMe con la API de WooCommerce de Distrisex para obtener productos y categorías en tiempo real.

## 🔧 Configuración Inicial

### 1. Variables de Entorno

Agrega las siguientes variables de entorno para las credenciales de WooCommerce:

```bash
# En tu archivo .env o configuración del servidor
WOOCOMMERCE_CONSUMER_KEY=tu_consumer_key_aqui
WOOCOMMERCE_CONSUMER_SECRET=tu_consumer_secret_aqui
```

### 2. URL Base de la API

La URL base ya está configurada en settings:
```
https://desarrollo.distrisex.com/wp-json/wc/v3
```

## 🔐 Autenticación

Todos los endpoints de WooCommerce requieren permisos de **administrador** (`IsAdminUser`).

## 📋 Endpoints Disponibles

### 1. **Probar Conexión**
```http
GET /api/products/woocommerce/test/
```

**Descripción:** Verifica que la conexión con WooCommerce funcione correctamente.

**Respuesta exitosa:**
```json
{
    "success": true,
    "message": "Conexión con WooCommerce exitosa",
    "connection_status": "OK",
    "api_response_headers": {...},
    "sample_data_structure": {
        "products_count": 1,
        "first_product_keys": ["id", "name", "slug", "permalink", ...]
    }
}
```

### 2. **Obtener Productos**
```http
GET /api/products/woocommerce/products/?category_id=123&per_page=10&page=1
```

**Parámetros Query:**
- `category_id` (opcional): ID de categoría específica
- `per_page` (opcional): Productos por página (máx 100, default 10)
- `page` (opcional): Número de página (default 1)

**Respuesta exitosa:**
```json
{
    "success": true,
    "message": "Productos obtenidos exitosamente desde WooCommerce",
    "data": [
        {
            "id": 1234,
            "name": "Producto Ejemplo",
            "slug": "producto-ejemplo",
            "type": "simple",
            "status": "publish",
            "featured": false,
            "catalog_visibility": "visible",
            "description": "...",
            "short_description": "...",
            "sku": "SKU123",
            "price": "99.99",
            "regular_price": "99.99",
            "sale_price": "",
            "on_sale": false,
            "purchasable": true,
            "total_sales": 0,
            "virtual": false,
            "downloadable": false,
            "downloads": [],
            "download_limit": -1,
            "download_expiry": -1,
            "external_url": "",
            "button_text": "",
            "tax_status": "taxable",
            "tax_class": "",
            "manage_stock": true,
            "stock_quantity": 10,
            "stock_status": "instock",
            "backorders": "no",
            "backorders_allowed": false,
            "backordered": false,
            "sold_individually": false,
            "weight": "1",
            "dimensions": {
                "length": "10",
                "width": "10",
                "height": "10"
            },
            "shipping_required": true,
            "shipping_taxable": true,
            "shipping_class": "",
            "shipping_class_id": 0,
            "reviews_allowed": true,
            "average_rating": "0.00",
            "rating_count": 0,
            "related_ids": [],
            "upsell_ids": [],
            "cross_sell_ids": [],
            "parent_id": 0,
            "purchase_note": "",
            "categories": [
                {
                    "id": 15,
                    "name": "Categoria Ejemplo",
                    "slug": "categoria-ejemplo"
                }
            ],
            "tags": [],
            "images": [
                {
                    "id": 5678,
                    "date_created": "2024-01-01T00:00:00",
                    "date_created_gmt": "2024-01-01T00:00:00",
                    "date_modified": "2024-01-01T00:00:00",
                    "date_modified_gmt": "2024-01-01T00:00:00",
                    "src": "https://ejemplo.com/imagen.jpg",
                    "name": "imagen.jpg",
                    "alt": "Imagen del producto"
                }
            ],
            "attributes": [],
            "default_attributes": [],
            "variations": [],
            "grouped_products": [],
            "menu_order": 0,
            "meta_data": [],
            "date_created": "2024-01-01T00:00:00",
            "date_created_gmt": "2024-01-01T00:00:00",
            "date_modified": "2024-01-01T00:00:00",
            "date_modified_gmt": "2024-01-01T00:00:00"
        }
    ],
    "pagination_info": {
        "page": 1,
        "per_page": 10,
        "category_id": 123
    },
    "api_info": {
        "status_code": 200,
        "headers": {...}
    }
}
```

### 3. **Obtener Categorías**
```http
GET /api/products/woocommerce/categories/?per_page=100&page=1
```

**Parámetros Query:**
- `per_page` (opcional): Categorías por página (default 100)
- `page` (opcional): Número de página (default 1)

**Respuesta exitosa:**
```json
{
    "success": true,
    "message": "Categorías obtenidas exitosamente desde WooCommerce",
    "data": [
        {
            "id": 15,
            "name": "Categoria Ejemplo",
            "slug": "categoria-ejemplo",
            "parent": 0,
            "description": "Descripción de la categoría",
            "display": "default",
            "image": {
                "id": 123,
                "date_created": "2024-01-01T00:00:00",
                "date_created_gmt": "2024-01-01T00:00:00",
                "date_modified": "2024-01-01T00:00:00",
                "date_modified_gmt": "2024-01-01T00:00:00",
                "src": "https://ejemplo.com/categoria.jpg",
                "name": "categoria.jpg",
                "alt": "Imagen de categoría"
            },
            "menu_order": 0,
            "count": 25
        }
    ],
    "pagination_info": {
        "page": 1,
        "per_page": 100
    },
    "api_info": {
        "status_code": 200,
        "headers": {...}
    }
}
```

### 4. **Obtener Producto Específico**
```http
GET /api/products/woocommerce/products/1234/
```

**Respuesta:** Similar a la estructura de un producto individual de la lista anterior.

## 🚨 Manejo de Errores

### Errores de Autenticación (401)
```json
{
    "success": false,
    "error": "API returned status 401",
    "status_code": 401,
    "details": "Consumer key is missing or invalid"
}
```

### Errores de Conexión
```json
{
    "success": false,
    "error": "Connection error",
    "status_code": null
}
```

### Producto No Encontrado (404)
```json
{
    "success": false,
    "error": "API returned status 404",
    "status_code": 404,
    "details": "No product was found matching the selection"
}
```

## 🔗 Campos Importantes de WooCommerce

### Producto
- **`id`**: ID único del producto
- **`name`**: Nombre del producto
- **`price`**: Precio actual (string)
- **`regular_price`**: Precio regular
- **`sale_price`**: Precio de oferta
- **`sku`**: Código del producto
- **`stock_quantity`**: Cantidad en stock
- **`stock_status`**: Estado del stock ("instock", "outofstock", "onbackorder")
- **`images`**: Array de imágenes del producto
- **`categories`**: Array de categorías asignadas
- **`description`**: Descripción completa (HTML)
- **`short_description`**: Descripción corta

### Categoría
- **`id`**: ID único de la categoría
- **`name`**: Nombre de la categoría
- **`slug`**: Slug URL de la categoría
- **`parent`**: ID de la categoría padre (0 si es raíz)
- **`count`**: Número de productos en la categoría
- **`image`**: Imagen de la categoría

## 🔧 Ejemplos de Uso

### 1. Obtener todas las categorías
```bash
curl -X GET "http://localhost:8000/api/products/woocommerce/categories/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 2. Obtener productos de una categoría específica
```bash
curl -X GET "http://localhost:8000/api/products/woocommerce/products/?category_id=15&per_page=20" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 3. Probar la conexión
```bash
curl -X GET "http://localhost:8000/api/products/woocommerce/test/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 📝 Notas Importantes

1. **Credenciales**: Asegúrate de configurar las credenciales correctas en las variables de entorno
2. **Límites**: WooCommerce tiene un límite máximo de 100 productos por página
3. **Timeouts**: Las requests tienen un timeout de 30 segundos configurado
4. **Logging**: Todas las peticiones se registran en los logs de Django para debugging
5. **Permisos**: Solo usuarios administradores pueden acceder a estos endpoints

## 🛠️ Próximos Pasos

Una vez que veas la estructura de datos que te devuelve WooCommerce, podrás:

1. **Mapear campos**: Crear un mapeo entre los campos de WooCommerce y tu modelo de Product
2. **Sincronización**: Implementar endpoints para sincronizar productos desde WooCommerce a tu base de datos
3. **Órdenes**: Implementar la creación de órdenes en WooCommerce cuando se hagan compras en tu tienda

¡La integración está lista para usar! 🚀

