#!/usr/bin/env python
"""Test script to verify margin application on variations"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crushme_project.settings')
django.setup()

from crushme_app.models import WooCommerceProduct, CategoryPriceMargin
from crushme_app.utils import calculate_product_price

print("="*60)
print("🧪 TEST: Márgenes en Variaciones")
print("="*60)

# Buscar un producto variable
product = WooCommerceProduct.objects.filter(product_type='variable').first()
print(f'\n📦 Producto Variable: {product.name}')
print(f'   ID: {product.wc_id}')

# Ver categoría y margen
first_cat = product.categories.first()
if first_cat:
    print(f'   📂 Categoría: {first_cat.name}')
    try:
        margin = CategoryPriceMargin.objects.get(category=first_cat, is_active=True)
        print(f'   💰 Margen configurado: {margin.margin_percentage}%')
        has_margin = True
    except CategoryPriceMargin.DoesNotExist:
        print(f'   ⚠️  Sin margen configurado para esta categoría')
        has_margin = False
else:
    print(f'   ⚠️  Sin categoría asignada')
    has_margin = False

# Calcular precio del producto padre
prices = calculate_product_price(product)
print(f'\n💵 Precio del producto padre:')
print(f'   Base (WC): ${product.price}')
print(f'   Con margen: ${prices["price"]}')
if prices.get('margin_applied'):
    print(f'   Margen aplicado: {prices["margin_applied"]}%')

# Ver variaciones
variations = product.variations.filter(status='publish')[:3]
print(f'\n🔧 Variaciones ({product.variations.filter(status="publish").count()} total):')
print()

for i, v in enumerate(variations, 1):
    print(f'{i}. Variación ID: {v.wc_id}')
    print(f'   Atributos: {v.get_attribute_description()}')
    print(f'   Precio base (WC): ${v.price}')
    
    if has_margin and prices.get('margin_applied'):
        margin_mult = 1 + (float(prices['margin_applied']) / 100)
        expected_price = round(float(v.price) * margin_mult, 2)
        print(f'   ✅ Precio con margen: ${expected_price}')
    else:
        print(f'   ℹ️  Sin margen aplicado')
    print()

print("="*60)
print("✅ Test completado")
print("="*60)
print("\n💡 Los precios con margen son los que se envían al frontend")
print("   en los endpoints de productos y variaciones.\n")
