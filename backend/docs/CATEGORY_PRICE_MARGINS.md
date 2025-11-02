# Sistema de Márgenes de Precio por Categoría

## Descripción General

El sistema de márgenes de precio permite configurar diferentes márgenes de ganancia para cada categoría de productos. Los precios finales se calculan automáticamente aplicando estos márgenes sobre los precios base de WooCommerce.

## Modelos

### CategoryPriceMargin

Configura el margen de precio para una categoría específica.

**Campos:**
- `category`: Relación OneToOne con `WooCommerceCategory`
- `margin_percentage`: Porcentaje de margen (ej: 30.00 para 30%)
- `use_fixed_multiplier`: Si es True, usa multiplicador fijo en lugar de porcentaje
- `fixed_multiplier`: Multiplicador fijo (ej: 1.30 para +30%)
- `is_active`: Si el margen está activo
- `notes`: Notas adicionales

**Métodos:**
- `calculate_price(base_price)`: Calcula el precio final aplicando el margen

**Ejemplo:**
```python
# Crear margen del 30% para categoría "Ropa"
category = WooCommerceCategory.objects.get(name="Ropa")
margin = CategoryPriceMargin.objects.create(
    category=category,
    margin_percentage=30.00,
    is_active=True
)

# Calcular precio
base_price = 100000  # COP
final_price = margin.calculate_price(base_price)  # 130000 COP
```

### DefaultPriceMargin

Margen por defecto para productos sin categoría específica o categorías sin margen configurado.

**Campos:**
- `margin_percentage`: Porcentaje de margen por defecto
- `use_fixed_multiplier`: Si usa multiplicador fijo
- `fixed_multiplier`: Multiplicador fijo
- `is_active`: Si el margen está activo

**Métodos:**
- `calculate_price(base_price)`: Calcula el precio con margen por defecto
- `get_active()`: Obtiene el margen por defecto activo (classmethod)

## Métodos en Modelos de Productos

### WooCommerceProduct

**Métodos agregados:**

#### `get_price_with_margin(base_price=None)`
Calcula el precio con margen de categoría aplicado.

**Lógica:**
1. Busca margen en la primera categoría del producto
2. Si no encuentra, usa el margen por defecto
3. Si no hay ningún margen, retorna el precio base

**Args:**
- `base_price`: Precio base. Si es None, usa `self.price`

**Returns:**
- Precio con margen aplicado (float)

**Ejemplo:**
```python
product = WooCommerceProduct.objects.get(wc_id=123)
price_with_margin = product.get_price_with_margin()
```

#### `get_regular_price_with_margin()`
Calcula el precio regular con margen aplicado.

#### `get_sale_price_with_margin()`
Calcula el precio de oferta con margen aplicado (si existe).

### WooCommerceProductVariation

**Métodos agregados:**

Las variaciones heredan el margen de las categorías del producto padre.

#### `get_price_with_margin(base_price=None)`
Usa las categorías del producto padre para aplicar el margen.

#### `get_regular_price_with_margin()`
Precio regular de la variación con margen.

#### `get_sale_price_with_margin()`
Precio de oferta de la variación con margen.

## Funciones Helper

### `calculate_product_price(product, target_currency='COP')`

Ubicación: `crushme_app/utils/translation_helpers.py`

Calcula el precio con margen Y conversión de moneda.

**Args:**
- `product`: Instancia de `WooCommerceProduct` o `WooCommerceProductVariation`
- `target_currency`: Moneda destino ('COP' o 'USD')

**Returns:**
```python
{
    'price': precio_convertido,
    'regular_price': precio_regular_convertido,
    'sale_price': precio_oferta_convertido,
    'converted_price': precio_convertido,
    'converted_regular_price': precio_regular_convertido,
    'margin_applied': "Category: +30%" o "Default: +20%",
    'currency': 'COP' o 'USD',
    'on_sale': True/False
}
```

**Ejemplo:**
```python
from crushme_app.utils.translation_helpers import calculate_product_price

product = WooCommerceProduct.objects.get(wc_id=123)
prices = calculate_product_price(product, target_currency='USD')

print(prices['price'])  # 32.50 (con margen y convertido a USD)
print(prices['margin_applied'])  # "Ropa: +30%"
```

### `apply_margin_and_convert_price(product, currency='COP')`

Ubicación: `crushme_app/utils/price_helpers.py`

Similar a `calculate_product_price` pero más simple.

**Args:**
- `product`: Instancia de producto o variación
- `currency`: Moneda destino

**Returns:**
```python
{
    'price': precio_final,
    'regular_price': precio_regular_final,
    'sale_price': precio_oferta_final,
    'currency': 'COP' o 'USD'
}
```

## Flujo de Cálculo de Precios

### 1. Precio Base (WooCommerce)
```
Precio en WooCommerce: 100,000 COP
```

### 2. Aplicar Margen de Categoría
```python
# Producto en categoría "Ropa" con margen del 30%
category_margin = CategoryPriceMargin.objects.get(category__name="Ropa")
# margin_percentage = 30.00

price_with_margin = product.get_price_with_margin()
# 100,000 * 1.30 = 130,000 COP
```

### 3. Convertir a Moneda Solicitada
```python
from crushme_app.utils.currency_converter import CurrencyConverter

# Si el usuario solicita USD
final_price = CurrencyConverter.convert_price(130000, 'USD')
# 130,000 / 4000 = 32.50 USD
```

### 4. Retornar al Frontend
```json
{
  "id": 123,
  "name": "Producto X",
  "price": 32.50,
  "regular_price": 32.50,
  "currency": "USD",
  "margin_applied": "Ropa: +30%"
}
```

## Uso en Views

Todas las views que retornan productos ya usan automáticamente el sistema de márgenes a través de las funciones helper:

### Ejemplo: Lista de Productos
```python
from ..utils.translation_helpers import get_products_list

@api_view(['GET'])
def list_products(request):
    target_currency = getattr(request, 'currency', 'COP')
    target_language = get_language_from_request(request)
    
    queryset = WooCommerceProduct.objects.filter(status='publish')
    
    # Esta función ya aplica márgenes automáticamente
    products = get_products_list(
        queryset, 
        target_language=target_language,
        target_currency=target_currency
    )
    
    return Response({'products': products})
```

### Ejemplo: Detalle de Producto
```python
from ..utils.translation_helpers import get_product_full_data

@api_view(['GET'])
def product_detail(request, product_id):
    target_currency = getattr(request, 'currency', 'COP')
    target_language = get_language_from_request(request)
    
    product = WooCommerceProduct.objects.get(wc_id=product_id)
    
    # Esta función ya aplica márgenes automáticamente
    product_data = get_product_full_data(
        product,
        target_language=target_language,
        target_currency=target_currency
    )
    
    return Response(product_data)
```

## Configuración en Admin

### Crear Margen para Categoría

1. Ir al admin de Django
2. Buscar "Category Price Margins"
3. Crear nuevo margen:
   - Seleccionar categoría
   - Configurar margen:
     - **Opción 1:** Porcentaje (ej: 30.00 para 30%)
     - **Opción 2:** Multiplicador fijo (ej: 1.30 para +30%)
   - Marcar como activo
   - Guardar

### Crear Margen Por Defecto

1. Ir al admin de Django
2. Buscar "Default Price Margins"
3. Crear/editar margen por defecto:
   - Configurar margen (porcentaje o multiplicador)
   - Marcar como activo
   - Solo puede haber uno activo

## Prioridad de Márgenes

El sistema aplica márgenes en este orden:

1. **Margen de la primera categoría del producto** (si existe y está activo)
2. **Margen por defecto** (si existe y está activo)
3. **Sin margen** (retorna precio base de WooCommerce)

## Ejemplos Completos

### Producto Simple con Margen de Categoría

```python
# Configuración
category = WooCommerceCategory.objects.get(name="Electrónica")
margin = CategoryPriceMargin.objects.create(
    category=category,
    margin_percentage=25.00,  # 25%
    is_active=True
)

# Producto
product = WooCommerceProduct.objects.get(wc_id=456)
product.price = 200000  # COP
product.categories.add(category)

# Cálculo
price_with_margin = product.get_price_with_margin()
# 200,000 * 1.25 = 250,000 COP

# Convertir a USD
from crushme_app.utils.currency_converter import CurrencyConverter
price_usd = CurrencyConverter.convert_price(250000, 'USD')
# 250,000 / 4000 = 62.50 USD
```

### Producto Variable con Variaciones

```python
# Producto padre
product = WooCommerceProduct.objects.get(wc_id=789)
product.product_type = 'variable'
product.categories.add(category)  # Categoría con 25% margen

# Variaciones
variation1 = WooCommerceProductVariation.objects.get(wc_id=1001)
variation1.product = product
variation1.price = 150000  # COP

variation2 = WooCommerceProductVariation.objects.get(wc_id=1002)
variation2.product = product
variation2.price = 180000  # COP

# Las variaciones heredan el margen del producto padre
v1_price = variation1.get_price_with_margin()  # 150,000 * 1.25 = 187,500 COP
v2_price = variation2.get_price_with_margin()  # 180,000 * 1.25 = 225,000 COP
```

### Producto sin Categoría (Usa Margen Por Defecto)

```python
# Margen por defecto
default_margin = DefaultPriceMargin.objects.create(
    margin_percentage=20.00,  # 20%
    is_active=True
)

# Producto sin categoría
product = WooCommerceProduct.objects.get(wc_id=999)
product.price = 50000  # COP
# product.categories.count() == 0

# Usa margen por defecto
price_with_margin = product.get_price_with_margin()
# 50,000 * 1.20 = 60,000 COP
```

## Archivos Modificados

- `crushme_app/models/woocommerce_models.py`: Métodos en WooCommerceProduct y WooCommerceProductVariation
- `crushme_app/utils/translation_helpers.py`: Función calculate_product_price actualizada
- `crushme_app/utils/price_helpers.py`: Nuevas funciones apply_category_margin_to_product y apply_margin_and_convert_price

## Notas Importantes

1. **Los márgenes se aplican ANTES de la conversión de moneda**
   - Primero: Precio base → Precio con margen (en COP)
   - Segundo: Precio con margen → Precio convertido (COP o USD)

2. **Las variaciones heredan el margen del producto padre**
   - No se configuran márgenes por variación
   - Usan las categorías del producto padre

3. **Solo puede haber un margen activo por categoría**
   - Relación OneToOne entre CategoryPriceMargin y WooCommerceCategory

4. **Solo puede haber un margen por defecto activo**
   - Usar `DefaultPriceMargin.get_active()` para obtenerlo

5. **Todas las views existentes ya usan el sistema de márgenes**
   - No es necesario modificar las views
   - Las funciones helper (`calculate_product_price`, `get_products_list`, `get_product_full_data`) ya aplican márgenes automáticamente
