# Resumen: Implementación de Márgenes de Precio por Categoría

## Problema Identificado

Los márgenes de precio configurados en el modelo `CategoryPriceMargin` no se estaban aplicando a los productos en las respuestas de los endpoints. Los precios se retornaban directamente desde WooCommerce sin aplicar los márgenes configurados.

## Solución Implementada

Se centralizó la lógica de aplicación de márgenes en los modelos de productos, permitiendo que TODAS las views usen automáticamente los márgenes sin necesidad de modificar cada endpoint individualmente.

## Cambios Realizados

### 1. Métodos Agregados a `WooCommerceProduct`

**Archivo:** `crushme_app/models/woocommerce_models.py`

```python
def get_price_with_margin(self, base_price=None):
    """Calcula el precio con margen de categoría aplicado"""
    # 1. Busca margen en la primera categoría del producto
    # 2. Si no encuentra, usa margen por defecto
    # 3. Si no hay ningún margen, retorna precio base
    
def get_regular_price_with_margin(self):
    """Calcula el precio regular con margen aplicado"""
    
def get_sale_price_with_margin(self):
    """Calcula el precio de oferta con margen aplicado"""
```

### 2. Métodos Agregados a `WooCommerceProductVariation`

**Archivo:** `crushme_app/models/woocommerce_models.py`

```python
def get_price_with_margin(self, base_price=None):
    """Usa las categorías del producto padre para aplicar margen"""
    
def get_regular_price_with_margin(self):
    """Precio regular de variación con margen"""
    
def get_sale_price_with_margin(self):
    """Precio de oferta de variación con margen"""
```

### 3. Actualización de `calculate_product_price()`

**Archivo:** `crushme_app/utils/translation_helpers.py`

Ahora usa los métodos del modelo en lugar de calcular manualmente:

```python
def calculate_product_price(product, target_currency='COP'):
    # ANTES: Calculaba margen manualmente
    # AHORA: Usa product.get_price_with_margin()
    
    final_price = product.get_price_with_margin()
    final_regular_price = product.get_regular_price_with_margin()
    final_sale_price = product.get_sale_price_with_margin()
    
    # Luego convierte a la moneda solicitada
    converted_price = CurrencyConverter.convert_price(final_price, target_currency)
    # ...
```

### 4. Actualización de Variaciones en `get_product_full_data()`

**Archivo:** `crushme_app/utils/translation_helpers.py`

Las variaciones ahora usan el método del modelo:

```python
# ANTES: Calculaba margen manualmente con regex y porcentajes
# AHORA: Usa variation.get_price_with_margin()

for variation in variations:
    variation_price_with_margin = variation.get_price_with_margin()
    converted_variation_price = CurrencyConverter.convert_price(
        variation_price_with_margin, 
        target_currency
    )
```

### 5. Nuevas Funciones Helper

**Archivo:** `crushme_app/utils/price_helpers.py`

```python
def apply_category_margin_to_product(product):
    """Aplica margen de categoría a un producto"""
    
def apply_margin_and_convert_price(product, currency='COP'):
    """Aplica margen Y convierte a moneda solicitada"""
```

## Endpoints Afectados (Automáticamente)

Todos los endpoints que usan las funciones helper YA aplican márgenes automáticamente:

### Productos
- `GET /api/products/woocommerce/products/` - Lista de productos
- `GET /api/products/woocommerce/products/{id}/` - Detalle de producto
- `GET /api/products/woocommerce/products/{id}/variations/` - Lista de variaciones
- `GET /api/products/woocommerce/products/{id}/variations/{var_id}/` - Detalle de variación
- `GET /api/products/woocommerce/products/search/` - Búsqueda de productos
- `GET /api/products/woocommerce/categories/{id}/products/` - Productos por categoría

### Wishlist
- `GET /api/wishlists/` - Wishlists del usuario
- `GET /api/wishlists/{id}/` - Detalle de wishlist
- `POST /api/wishlists/{id}/products/` - Agregar producto a wishlist
- `GET /@{username}/{wishlist_id}/` - Wishlist pública

### Favoritos
- `GET /api/favorites/products/` - Productos favoritos
- `POST /api/favorites/products/` - Agregar a favoritos

### Carrito
- `GET /api/cart/` - Ver carrito
- `POST /api/cart/add/` - Agregar al carrito

### Órdenes
- `GET /api/orders/purchases/` - Historial de compras
- `GET /api/orders/gifts/` - Órdenes de regalos

## Flujo de Aplicación de Márgenes

```
1. Precio Base WooCommerce (100,000 COP)
   ↓
2. Aplicar Margen de Categoría (+30%)
   → 100,000 * 1.30 = 130,000 COP
   ↓
3. Convertir a Moneda Solicitada (USD)
   → 130,000 / 4000 = 32.50 USD
   ↓
4. Retornar al Frontend
   → {"price": 32.50, "currency": "USD"}
```

## Configuración de Márgenes

### Admin Django

1. **Margen por Categoría:**
   - Ir a "Category Price Margins"
   - Crear margen para categoría específica
   - Configurar porcentaje o multiplicador
   - Activar

2. **Margen Por Defecto:**
   - Ir a "Default Price Margins"
   - Crear/editar margen por defecto
   - Solo puede haber uno activo

### Ejemplo de Configuración

```python
# Margen del 30% para categoría "Ropa"
category = WooCommerceCategory.objects.get(name="Ropa")
CategoryPriceMargin.objects.create(
    category=category,
    margin_percentage=30.00,
    is_active=True
)

# Margen por defecto del 20%
DefaultPriceMargin.objects.create(
    margin_percentage=20.00,
    is_active=True
)
```

## Prioridad de Márgenes

1. **Margen de categoría específica** (si existe y está activo)
2. **Margen por defecto** (si existe y está activo)
3. **Sin margen** (precio base de WooCommerce)

## Ventajas de la Solución

✅ **Centralizada:** Lógica en el modelo, no dispersa en views
✅ **Automática:** Todas las views usan márgenes sin modificación
✅ **Mantenible:** Un solo lugar para actualizar la lógica
✅ **Reutilizable:** Métodos disponibles en cualquier parte del código
✅ **Consistente:** Mismo cálculo en todos los endpoints
✅ **Escalable:** Fácil agregar nuevos tipos de márgenes

## Testing

### Verificar que los Márgenes se Aplican

```bash
# 1. Configurar margen en admin
# 2. Consultar producto

curl -H "X-Currency: COP" \
  "http://localhost:8000/api/products/woocommerce/products/123/"

# Respuesta esperada:
{
  "id": 123,
  "name": "Producto X",
  "price": 130000,  # Con margen aplicado
  "currency": "COP",
  "margin_applied": "Ropa: +30%"
}
```

### Verificar Conversión de Moneda

```bash
curl -H "X-Currency: USD" \
  "http://localhost:8000/api/products/woocommerce/products/123/"

# Respuesta esperada:
{
  "id": 123,
  "name": "Producto X",
  "price": 32.50,  # Con margen Y convertido a USD
  "currency": "USD",
  "margin_applied": "Ropa: +30%"
}
```

## Archivos Modificados

1. `crushme_app/models/woocommerce_models.py`
   - Métodos en WooCommerceProduct
   - Métodos en WooCommerceProductVariation

2. `crushme_app/utils/translation_helpers.py`
   - calculate_product_price() actualizada
   - get_product_full_data() actualizada (variaciones)

3. `crushme_app/utils/price_helpers.py`
   - apply_category_margin_to_product() nueva
   - apply_margin_and_convert_price() nueva

4. `docs/CATEGORY_PRICE_MARGINS.md` (nuevo)
   - Documentación completa del sistema

## Próximos Pasos

1. **Configurar márgenes en admin** para cada categoría
2. **Verificar precios** en frontend
3. **Ajustar márgenes** según necesidad del negocio
4. **Monitorear** que todos los endpoints retornen precios correctos

## Notas Importantes

- Los márgenes se aplican ANTES de la conversión de moneda
- Las variaciones heredan el margen del producto padre
- Solo puede haber un margen activo por categoría
- Solo puede haber un margen por defecto activo
- Todas las views existentes YA usan el sistema (no requieren cambios)
