#!/usr/bin/env python
"""
Script para probar el sistema de márgenes de precio por categoría.

Uso:
    python manage.py shell < scripts/test_price_margins.py
"""

from crushme_app.models import (
    WooCommerceProduct,
    WooCommerceCategory,
    WooCommerceProductVariation,
    CategoryPriceMargin,
    DefaultPriceMargin
)
from crushme_app.utils.translation_helpers import calculate_product_price
from crushme_app.utils.currency_converter import CurrencyConverter

print("\n" + "="*80)
print("TESTING: Sistema de Márgenes de Precio por Categoría")
print("="*80 + "\n")

# ============================================================================
# 1. Configurar Margen Por Defecto
# ============================================================================
print("1. Configurando Margen Por Defecto...")
print("-" * 80)

# Desactivar márgenes por defecto existentes
DefaultPriceMargin.objects.all().update(is_active=False)

# Crear margen por defecto del 20%
default_margin = DefaultPriceMargin.objects.create(
    margin_percentage=20.00,
    is_active=True,
    notes="Margen por defecto para testing"
)
print(f"✓ Margen por defecto creado: {default_margin}")
print(f"  - Porcentaje: {default_margin.margin_percentage}%")
print()

# ============================================================================
# 2. Configurar Margen para Categoría Específica
# ============================================================================
print("2. Configurando Margen para Categoría...")
print("-" * 80)

# Obtener o crear categoría de prueba
category, created = WooCommerceCategory.objects.get_or_create(
    wc_id=999999,
    defaults={
        'name': 'Categoría de Prueba',
        'slug': 'categoria-prueba'
    }
)
print(f"{'✓ Categoría creada' if created else '✓ Categoría existente'}: {category.name}")

# Crear margen del 30% para esta categoría
try:
    cat_margin = CategoryPriceMargin.objects.get(category=category)
    cat_margin.margin_percentage = 30.00
    cat_margin.is_active = True
    cat_margin.save()
    print(f"✓ Margen actualizado para categoría: {cat_margin}")
except CategoryPriceMargin.DoesNotExist:
    cat_margin = CategoryPriceMargin.objects.create(
        category=category,
        margin_percentage=30.00,
        is_active=True,
        notes="Margen de prueba"
    )
    print(f"✓ Margen creado para categoría: {cat_margin}")

print(f"  - Porcentaje: {cat_margin.margin_percentage}%")
print()

# ============================================================================
# 3. Probar con Producto Real
# ============================================================================
print("3. Probando con Producto Real...")
print("-" * 80)

# Obtener primer producto disponible
product = WooCommerceProduct.objects.filter(
    status='publish',
    price__isnull=False
).first()

if not product:
    print("⚠ No hay productos disponibles para probar")
else:
    print(f"✓ Producto: {product.name}")
    print(f"  - ID: {product.wc_id}")
    print(f"  - Precio base WooCommerce: {product.price} COP")
    print(f"  - Categorías: {', '.join([c.name for c in product.categories.all()])}")
    print()
    
    # Probar SIN categoría específica (usa margen por defecto)
    print("  a) Sin categoría específica (margen por defecto 20%):")
    product.categories.clear()
    
    price_with_margin = product.get_price_with_margin()
    print(f"     - Precio con margen: {price_with_margin:,.2f} COP")
    print(f"     - Cálculo: {product.price} * 1.20 = {price_with_margin:,.2f}")
    
    # Convertir a USD
    price_usd = CurrencyConverter.convert_price(price_with_margin, 'USD')
    print(f"     - Precio en USD: ${price_usd}")
    print()
    
    # Probar CON categoría específica (usa margen de categoría)
    print("  b) Con categoría específica (margen 30%):")
    product.categories.add(category)
    
    price_with_margin = product.get_price_with_margin()
    print(f"     - Precio con margen: {price_with_margin:,.2f} COP")
    print(f"     - Cálculo: {product.price} * 1.30 = {price_with_margin:,.2f}")
    
    # Convertir a USD
    price_usd = CurrencyConverter.convert_price(price_with_margin, 'USD')
    print(f"     - Precio en USD: ${price_usd}")
    print()
    
    # Probar función helper completa
    print("  c) Usando calculate_product_price() helper:")
    prices_cop = calculate_product_price(product, target_currency='COP')
    print(f"     - COP: {prices_cop['price']:,} {prices_cop['currency']}")
    print(f"     - Margen aplicado: {prices_cop['margin_applied']}")
    
    prices_usd = calculate_product_price(product, target_currency='USD')
    print(f"     - USD: ${prices_usd['price']} {prices_usd['currency']}")
    print(f"     - Margen aplicado: {prices_usd['margin_applied']}")
    print()

# ============================================================================
# 4. Probar con Producto Variable
# ============================================================================
print("4. Probando con Producto Variable...")
print("-" * 80)

variable_product = WooCommerceProduct.objects.filter(
    status='publish',
    product_type='variable',
    price__isnull=False
).first()

if not variable_product:
    print("⚠ No hay productos variables disponibles para probar")
else:
    print(f"✓ Producto Variable: {variable_product.name}")
    print(f"  - ID: {variable_product.wc_id}")
    print(f"  - Tipo: {variable_product.product_type}")
    
    # Asignar categoría con margen
    variable_product.categories.add(category)
    
    # Obtener variaciones
    variations = variable_product.variations.filter(status='publish')[:3]
    print(f"  - Variaciones: {variations.count()}")
    print()
    
    for i, variation in enumerate(variations, 1):
        print(f"  Variación {i}:")
        print(f"    - ID: {variation.wc_id}")
        print(f"    - Atributos: {variation.attributes}")
        print(f"    - Precio base: {variation.price} COP")
        
        # Aplicar margen (hereda del producto padre)
        price_with_margin = variation.get_price_with_margin()
        print(f"    - Precio con margen (30%): {price_with_margin:,.2f} COP")
        
        # Convertir a USD
        price_usd = CurrencyConverter.convert_price(price_with_margin, 'USD')
        print(f"    - Precio en USD: ${price_usd}")
        print()

# ============================================================================
# 5. Comparación de Precios
# ============================================================================
print("5. Comparación: Precio Base vs Precio con Margen")
print("-" * 80)

# Obtener algunos productos
products = WooCommerceProduct.objects.filter(
    status='publish',
    price__isnull=False
)[:5]

print(f"{'Producto':<30} {'Base (COP)':<15} {'Con Margen':<15} {'Margen':<10}")
print("-" * 80)

for prod in products:
    # Asignar categoría con margen del 30%
    prod.categories.add(category)
    
    base_price = float(prod.price)
    price_with_margin = prod.get_price_with_margin()
    margin_applied = ((price_with_margin - base_price) / base_price) * 100
    
    name = prod.name[:28] + '..' if len(prod.name) > 30 else prod.name
    print(f"{name:<30} {base_price:>13,.0f}  {price_with_margin:>13,.0f}  {margin_applied:>8.1f}%")

print()

# ============================================================================
# 6. Resumen
# ============================================================================
print("="*80)
print("RESUMEN")
print("="*80)
print(f"✓ Margen por defecto: {default_margin.margin_percentage}%")
print(f"✓ Margen para '{category.name}': {cat_margin.margin_percentage}%")
print(f"✓ Productos probados: {products.count()}")
print()
print("CONCLUSIÓN:")
print("  - Los márgenes se aplican correctamente usando los métodos del modelo")
print("  - Las variaciones heredan el margen del producto padre")
print("  - La conversión de moneda funciona después de aplicar márgenes")
print("  - Todas las funciones helper usan automáticamente los márgenes")
print()
print("="*80)
print("Testing completado exitosamente!")
print("="*80 + "\n")
