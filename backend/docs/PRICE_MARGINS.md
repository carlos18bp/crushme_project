# 💰 Sistema de Márgenes de Precio

## 📋 Descripción

Sistema para aplicar márgenes de ganancia automáticos sobre los precios de WooCommerce. Los precios finales enviados al frontend incluyen el margen configurado.

---

## 🏗️ Arquitectura

```
WooCommerce Price (Costo) → Apply Margin → Final Price (Frontend)
      $100                  +30%              $130
```

### Niveles de Configuración:

1. **Por Categoría** (prioridad alta)
   - Cada categoría puede tener su propio margen
   - Se aplica a todos los productos de esa categoría

2. **Margen Default** (fallback)
   - Se aplica cuando una categoría no tiene margen específico
   - Solo puede haber uno activo a la vez

---

## 🎯 Características

### ✅ Ya Implementado

- ✅ Márgenes por categoría
- ✅ Margen default/global
- ✅ Dos modos: porcentaje o multiplicador fijo
- ✅ Activar/desactivar márgenes individuales
- ✅ Interfaz admin completa
- ✅ Acciones masivas (aplicar 20%, 30%, 40%)
- ✅ Cálculo automático en todos los endpoints
- ✅ Aplicación a todos los tipos de precio (regular, sale, etc.)

---

## 📊 Uso desde Django Admin

### Acceso:
```
http://localhost:8000/admin/crushme_app/categoryp ricemargin/
```

### 1. Configurar Margen Default

**Ruta:** Admin → Default Price Margins → Add/Edit

**Campos:**
- **Margin Percentage**: `30.00` (para 30% de ganancia)
- **Use Fixed Multiplier**: ☐ (dejar desmarcado)
- **Fixed Multiplier**: `1.00` (solo si usas multiplicador fijo)
- **Is Active**: ☑️ (activado)

**Ejemplo:**
```
Precio WooCommerce: $100
Margin: 30%
Precio Final: $130
```

---

### 2. Configurar Márgen por Categoría

**Ruta:** Admin → Category Price Margins → Add

**Ejemplo 1: Categoría con 40% de margen**
```
Category: Aceites para Masajes
Margin Percentage: 40.00
Is Active: ✅
```

**Ejemplo 2: Categoría con multiplicador fijo**
```
Category: Juguetes Eróticos
Use Fixed Multiplier: ✅
Fixed Multiplier: 1.50
Is Active: ✅
```

---

### 3. Acciones Masivas

Selecciona múltiples categorías y aplica:

- **💰 Apply 20% margin**: Aplica 20% a todas las seleccionadas
- **💰 Apply 30% margin**: Aplica 30% a todas las seleccionadas
- **💰 Apply 40% margin**: Aplica 40% a todas las seleccionadas
- **✅ Activate margins**: Activa las seleccionadas
- **❌ Deactivate margins**: Desactiva las seleccionadas

---

## 🔧 Comandos de Management

### Inicializar Márgenes

```bash
# Crear márgenes del 30% para todas las categorías
python manage.py setup_margins

# Usar un margen diferente
python manage.py setup_margins --margin 40

# Solo crear margen default (sin categorías)
python manage.py setup_margins --default-only --margin 25
```

**Salida:**
```
🔧 Setting up price margins...
✅ Created default margin: 30.0%
  ✅ Created margin for: Aceites para Masajes (+30%)
  ✅ Created margin for: Juguetes Eróticos (+30%)
  ✅ Created margin for: Lencería (+30%)
==================================================
✅ Created 148 new margins
📊 Total categories with margins: 148
✅ Setup complete!
```

---

## 💻 Cómo Funciona (Backend)

### Flujo de Cálculo:

```python
# 1. Se obtiene el producto de la DB
product = WooCommerceProduct.objects.get(wc_id=123)
# price = $100 (precio de WooCommerce)

# 2. Se calcula el precio con margen
from crushme_app.utils import calculate_product_price
prices = calculate_product_price(product)

# 3. Resultado:
{
    'price': 130.00,              # +30% aplicado
    'regular_price': 130.00,      # +30% aplicado
    'sale_price': None,
    'margin_applied': 30.0,
    'on_sale': False
}
```

### Prioridad de Márgenes:

```
1. CategoryPriceMargin (categoría del producto) ← PRIORIDAD ALTA
   ↓ (si no existe)
2. DefaultPriceMargin (margen global) ← FALLBACK
   ↓ (si no existe o está inactivo)
3. Precio original de WooCommerce (sin margen)
```

---

## 📡 Respuesta en API

Todos los endpoints de productos retornan precios CON margen aplicado:

### GET `/api/products/woocommerce/products/123/` (Producto Simple)

```json
{
  "id": 123,
  "name": "Aceite de Masajes",
  "price": 130.00,              // ← Ya incluye margen
  "regular_price": 130.00,      // ← Ya incluye margen
  "sale_price": null,
  "on_sale": false,
  "categories": [
    {
      "id": 251,
      "name": "Aceites para Masajes"  // ← Esta categoría tiene margen del 30%
    }
  ]
}
```

### GET `/api/products/woocommerce/products/82257/` (Producto Variable)

```json
{
  "id": 82257,
  "name": "Aceite de Masajes Coco",
  "type": "variable",
  "is_variable": true,
  "price": 11037.00,           // ← Precio base con margen
  "categories": [
    {
      "id": 251,
      "name": "Aceites para Masajes"  // ← Margen del 30%
    }
  ],
  "available_variations": [
    {
      "id": 82295,
      "attributes": {"Tamaño": "250ML"},
      "price": 11037.00,      // ← Precio WC: $8490 + 30% = $11037
      "stock_quantity": 10,
      "in_stock": true
    },
    {
      "id": 82296,
      "attributes": {"Tamaño": "30ML"},
      "price": 6487.00,       // ← Precio WC: $4990 + 30% = $6487
      "stock_quantity": 5,
      "in_stock": true
    }
  ]
}
```

### GET `/api/products/woocommerce/products/82257/variations/82295/` (Variación Específica)

```json
{
  "id": 82295,
  "product_id": 82257,
  "product_name": "Aceite de Masajes Coco",
  "price": 11037.00,          // ← Precio con margen aplicado
  "regular_price": 11037.00,  // ← Precio con margen aplicado
  "margin_applied": 30.0,     // ← Indicador del margen aplicado
  "attributes": {
    "Tamaño": "250ML"
  },
  "categories": [
    {
      "id": 251,
      "name": "Aceites para Masajes"
    }
  ]
}
```

**El frontend NO necesita hacer cálculos**, los precios ya vienen listos.

---

## 🎨 Ejemplos de Configuración

### Ejemplo 1: Márgenes Diferentes por Categoría

```
Aceites para Masajes: 40%
Juguetes Eróticos: 35%
Lencería: 30%
Accesorios: 25%
Default: 20%
```

### Ejemplo 2: Promoción en Categoría

```python
# Temporalmente reducir margen en "Aceites"
margin = CategoryPriceMargin.objects.get(category__name="Aceites")
margin.margin_percentage = 15.0  # Reducir de 40% a 15%
margin.notes = "Promoción Navidad 2025"
margin.save()
```

### Ejemplo 3: Desactivar Márgenes Temporalmente

```python
# Desactivar margen de categoría específica
CategoryPriceMargin.objects.filter(
    category__name="Juguetes Eróticos"
).update(is_active=False)

# Ahora esa categoría usará el margen default
```

---

## 🧪 Testing

### Verificar Márgenes Configurados:

```bash
python manage.py shell
```

```python
from crushme_app.models import CategoryPriceMargin, DefaultPriceMargin

# Ver margen default
default = DefaultPriceMargin.get_active()
print(f"Default margin: {default.margin_percentage}%")

# Ver márgenes por categoría
margins = CategoryPriceMargin.objects.filter(is_active=True)
for m in margins:
    print(f"{m.category.name}: {m.margin_percentage}%")

# Probar cálculo
from crushme_app.models import WooCommerceProduct
from crushme_app.utils import calculate_product_price

product = WooCommerceProduct.objects.first()
prices = calculate_product_price(product)
print(f"Base: {product.price} → Final: {prices['price']}")
```

### Verificar en API:

```bash
# Ver producto con margen aplicado
curl http://localhost:8000/api/products/woocommerce/products/82257/ | jq '.data.price'

# Comparar con precio base de WooCommerce
python manage.py shell -c "from crushme_app.models import WooCommerceProduct; p = WooCommerceProduct.objects.get(wc_id=82257); print(f'Base: {p.price}')"
```

---

## 📈 Dashboard de Márgenes

### Estadísticas:

```bash
python manage.py shell
```

```python
from crushme_app.models import CategoryPriceMargin, WooCommerceProduct

# Categorías con márgenes
total_categories = CategoryPriceMargin.objects.count()
active_margins = CategoryPriceMargin.objects.filter(is_active=True).count()

print(f"Categories with margins: {active_margins}/{total_categories}")

# Promedio de márgenes
from django.db.models import Avg
avg_margin = CategoryPriceMargin.objects.filter(
    is_active=True
).aggregate(Avg('margin_percentage'))

print(f"Average margin: {avg_margin['margin_percentage__avg']:.2f}%")

# Productos sin margen específico
products_with_default = WooCommerceProduct.objects.filter(
    categories__price_margin__isnull=True
).count()

print(f"Products using default margin: {products_with_default}")
```

---

## ⚠️ Notas Importantes

1. **Los márgenes NO modifican WooCommerce**: Los precios en WooCommerce permanecen iguales. El margen solo se aplica al enviar datos al frontend.

2. **Sincronización**: Si sincronizas productos de nuevo, los márgenes configurados se mantienen.

3. **Variaciones**: ✅ **Las variaciones SIEMPRE heredan el margen de la categoría del producto padre**. 
   - Si el producto padre está en "Aceites para Masajes" con 40% de margen, TODAS sus variaciones también tendrán 40%.
   - Cada variación puede tener su propio precio base en WooCommerce, pero el margen se aplica consistentemente.
   - Ejemplo: Variación 250ML cuesta $100 → con 40% = $140 | Variación 30ML cuesta $50 → con 40% = $70

4. **Prioridad**: Si un producto tiene múltiples categorías, se usa el margen de la primera categoría.

5. **Cambios en tiempo real**: Los cambios en márgenes se aplican inmediatamente sin necesidad de reiniciar el servidor.

---

## 🔄 Workflow Recomendado

### Setup Inicial:
```bash
# 1. Sincronizar productos de WooCommerce
python manage.py sync_woocommerce --full

# 2. Configurar márgenes
python manage.py setup_margins --margin 30

# 3. Ajustar manualmente en admin si necesario
# http://localhost:8000/admin/crushme_app/categoryp ricemargin/
```

### Mantenimiento:
```bash
# Revisar márgenes semanalmente
# Ajustar según rentabilidad/competencia
# Activar/desactivar para promociones
```

---

## 🎯 Casos de Uso

### 1. Black Friday (Reducir márgenes temporalmente)
```python
# Reducir todos los márgenes al 10%
CategoryPriceMargin.objects.filter(is_active=True).update(
    margin_percentage=10,
    notes="Black Friday 2025"
)
```

### 2. Nuevos Productos (Margen alto inicial)
```python
# Nuevas categorías con margen del 50%
new_categories = ['Novedades', 'Exclusivos']
CategoryPriceMargin.objects.filter(
    category__name__in=new_categories
).update(margin_percentage=50)
```

### 3. Productos de Baja Rotación (Incrementar margen)
```python
# Categorías específicas con margen del 45%
CategoryPriceMargin.objects.filter(
    category__slug='accesorios-especiales'
).update(margin_percentage=45)
```

---

## 📞 Soporte

Para preguntas o issues:
- Revisar logs: `/backend/logs/`
- Django admin: `/admin/crushme_app/categoryp ricemargin/`
- Management commands: `python manage.py help setup_margins`

---

**✅ Sistema completamente funcional y listo para usar!**
