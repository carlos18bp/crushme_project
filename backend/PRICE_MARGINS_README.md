# Sistema de Márgenes de Precio por Categoría - Guía Rápida

## ✅ Problema Resuelto

Los márgenes de precio configurados en `CategoryPriceMargin` ahora se aplican **automáticamente** en TODOS los endpoints que retornan productos.

## 🎯 Solución Implementada

Se centralizó la lógica de márgenes en los modelos `WooCommerceProduct` y `WooCommerceProductVariation`, permitiendo que todas las views usen automáticamente los márgenes sin necesidad de modificación.

## 📋 Cambios Realizados

### 1. Métodos Agregados a Modelos

**WooCommerceProduct:**
- `get_price_with_margin(base_price=None)` - Calcula precio con margen
- `get_regular_price_with_margin()` - Precio regular con margen
- `get_sale_price_with_margin()` - Precio de oferta con margen

**WooCommerceProductVariation:**
- `get_price_with_margin(base_price=None)` - Hereda margen del producto padre
- `get_regular_price_with_margin()` - Precio regular con margen
- `get_sale_price_with_margin()` - Precio de oferta con margen

### 2. Funciones Helper Actualizadas

**`calculate_product_price()`** en `translation_helpers.py`:
- Ahora usa los métodos del modelo en lugar de calcular manualmente
- Soporta productos y variaciones
- Aplica margen Y conversión de moneda

### 3. Endpoints Afectados (Automáticamente)

✅ **Todos los endpoints que retornan productos YA usan márgenes:**

- Lista de productos
- Detalle de producto
- Variaciones de producto
- Búsqueda de productos
- Productos por categoría
- Wishlist
- Favoritos
- Carrito
- Historial de compras

## 🚀 Cómo Usar

### Configurar Márgenes en Admin

#### Opción 1: Margen por Categoría

1. Ir al admin de Django
2. Buscar **"Category Price Margins"**
3. Click en **"Add Category Price Margin"**
4. Configurar:
   ```
   Category: [Seleccionar categoría]
   Margin percentage: 30.00  (para 30%)
   Is active: ✓
   ```
5. Guardar

#### Opción 2: Margen Por Defecto

1. Ir al admin de Django
2. Buscar **"Default Price Margins"**
3. Crear/editar margen por defecto:
   ```
   Margin percentage: 20.00  (para 20%)
   Is active: ✓
   ```
4. Guardar

### Usar en Código

```python
# Obtener producto
product = WooCommerceProduct.objects.get(wc_id=123)

# Obtener precio con margen aplicado
price_with_margin = product.get_price_with_margin()
# Ejemplo: 100,000 COP → 130,000 COP (con margen del 30%)

# Obtener precio con margen Y conversión de moneda
from crushme_app.utils.translation_helpers import calculate_product_price

prices = calculate_product_price(product, target_currency='USD')
# Retorna:
# {
#   'price': 32.50,  # Con margen y convertido a USD
#   'currency': 'USD',
#   'margin_applied': 'Ropa: +30%'
# }
```

## 📊 Flujo de Cálculo

```
1. Precio Base (WooCommerce)
   100,000 COP
   ↓
2. Aplicar Margen de Categoría (+30%)
   100,000 * 1.30 = 130,000 COP
   ↓
3. Convertir a Moneda (USD)
   130,000 / 4000 = 32.50 USD
   ↓
4. Retornar al Frontend
   {"price": 32.50, "currency": "USD"}
```

## 🧪 Testing

### Ejecutar Script de Prueba

```bash
cd /home/cerrotico/work/crushme_project/backend
python manage.py shell < scripts/test_price_margins.py
```

Este script:
- ✓ Configura márgenes de prueba
- ✓ Prueba con productos reales
- ✓ Prueba con productos variables
- ✓ Muestra comparación de precios
- ✓ Verifica conversión de moneda

### Probar Endpoints Manualmente

```bash
# Producto con margen en COP
curl -H "X-Currency: COP" \
  "http://localhost:8000/api/products/woocommerce/products/123/"

# Producto con margen en USD
curl -H "X-Currency: USD" \
  "http://localhost:8000/api/products/woocommerce/products/123/"
```

## 📚 Documentación Completa

Ver documentación detallada en:
- `docs/CATEGORY_PRICE_MARGINS.md` - Documentación completa del sistema
- `docs/PRICE_MARGIN_IMPLEMENTATION_SUMMARY.md` - Resumen de implementación

## 🔑 Puntos Clave

1. **Automático:** Todos los endpoints YA usan márgenes (no requieren cambios)
2. **Centralizado:** Lógica en el modelo, no dispersa en views
3. **Prioridad:** Categoría específica → Margen por defecto → Sin margen
4. **Herencia:** Variaciones heredan margen del producto padre
5. **Orden:** Margen primero, luego conversión de moneda

## ⚠️ Notas Importantes

- Solo puede haber **un margen activo por categoría** (OneToOne)
- Solo puede haber **un margen por defecto activo**
- Los márgenes se aplican **ANTES** de la conversión de moneda
- Las variaciones **NO tienen margen propio**, heredan del padre

## 📁 Archivos Modificados

```
crushme_app/
├── models/
│   └── woocommerce_models.py          # Métodos agregados
├── utils/
│   ├── translation_helpers.py         # calculate_product_price actualizada
│   └── price_helpers.py               # Nuevas funciones helper
docs/
├── CATEGORY_PRICE_MARGINS.md          # Documentación completa
└── PRICE_MARGIN_IMPLEMENTATION_SUMMARY.md  # Resumen
scripts/
└── test_price_margins.py              # Script de testing
```

## ✨ Próximos Pasos

1. **Configurar márgenes** para cada categoría en el admin
2. **Ejecutar script de testing** para verificar
3. **Probar endpoints** en frontend
4. **Ajustar márgenes** según necesidad del negocio

## 💡 Ejemplo Rápido

```python
# En Django shell
from crushme_app.models import WooCommerceCategory, CategoryPriceMargin

# Configurar margen del 25% para "Electrónica"
category = WooCommerceCategory.objects.get(name="Electrónica")
CategoryPriceMargin.objects.create(
    category=category,
    margin_percentage=25.00,
    is_active=True
)

# ¡Listo! Todos los productos de "Electrónica" ahora tienen +25%
```

---

**¿Preguntas?** Ver documentación completa en `docs/CATEGORY_PRICE_MARGINS.md`
