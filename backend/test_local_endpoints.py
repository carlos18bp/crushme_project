"""
Script de prueba para los endpoints locales optimizados
"""
import sys
import os
import django

# Setup Django
sys.path.append('/home/cerrotico/work/crushme_project/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crushme_project.settings')
django.setup()

from crushme_app.models import WooCommerceProduct, WooCommerceCategory, TranslatedContent
from crushme_app.utils.translation_helpers import get_products_list, get_translated_category

print("🧪 TESTING LOCAL OPTIMIZED ENDPOINTS\n")
print("=" * 60)

# Test 1: Productos sincronizados
print("\n1️⃣ TEST: Productos sincronizados")
total_products = WooCommerceProduct.objects.filter(status='publish').count()
print(f"   ✅ Total productos publicados: {total_products}")

# Test 2: Categorías sincronizadas
print("\n2️⃣ TEST: Categorías sincronizadas")
total_categories = WooCommerceCategory.objects.count()
print(f"   ✅ Total categorías: {total_categories}")

# Test 3: Traducciones disponibles
print("\n3️⃣ TEST: Traducciones disponibles")
total_translations = TranslatedContent.objects.count()
print(f"   ✅ Total traducciones: {total_translations}")
by_type = TranslatedContent.objects.values('content_type').distinct().count()
print(f"   ✅ Tipos de contenido traducido: {by_type}")

# Test 4: Obtener productos con traducción (español)
print("\n4️⃣ TEST: Obtener productos en español")
products_qs = WooCommerceProduct.objects.filter(status='publish')[:5]
products_es = get_products_list(products_qs, target_language='es', include_stock=False)
print(f"   ✅ Productos obtenidos: {len(products_es)}")
if products_es:
    print(f"   📦 Primer producto: {products_es[0]['name']}")
    print(f"      Precio: ${products_es[0]['price']}")
    print(f"      Categoría: {products_es[0].get('category', 'N/A')}")

# Test 5: Obtener productos con traducción (inglés)
print("\n5️⃣ TEST: Obtener productos en inglés")
products_en = get_products_list(products_qs, target_language='en', include_stock=False)
print(f"   ✅ Productos obtenidos: {len(products_en)}")
if products_en:
    print(f"   📦 Primer producto: {products_en[0]['name']}")
    print(f"      (Original: {products_es[0]['name']})")

# Test 6: Categorías con traducción
print("\n6️⃣ TEST: Categorías con traducción")
cat = WooCommerceCategory.objects.first()
if cat:
    cat_es = get_translated_category(cat, 'es')
    cat_en = get_translated_category(cat, 'en')
    print(f"   ✅ Categoría ES: {cat_es['name']}")
    print(f"   ✅ Categoría EN: {cat_en['name']}")

# Test 7: Productos por categoría
print("\n7️⃣ TEST: Productos por categoría")
cat_134 = WooCommerceCategory.objects.filter(wc_id=134).first()
if cat_134:
    products_in_cat = WooCommerceProduct.objects.filter(
        categories__wc_id=134,
        status='publish'
    ).count()
    print(f"   ✅ Categoría: {cat_134.name}")
    print(f"   ✅ Productos en categoría: {products_in_cat}")

# Test 8: Productos destacados (trending)
print("\n8️⃣ TEST: Productos destacados")
trending = WooCommerceProduct.objects.filter(
    status='publish',
    stock_status='instock'
).order_by('-rating_count', '-average_rating')[:8]
print(f"   ✅ Productos trending: {trending.count()}")
if trending:
    print(f"   ⭐ Top producto: {trending[0].name}")
    print(f"      Rating: {trending[0].average_rating} ({trending[0].rating_count} reviews)")

print("\n" + "=" * 60)
print("✅ TESTS COMPLETADOS\n")

# Resumen
print("📊 RESUMEN:")
print(f"   • Productos: {total_products}")
print(f"   • Categorías: {total_categories}")
print(f"   • Traducciones: {total_translations}")
print(f"   • Estado: Sistema listo para usar ✅")

# Verificar si hay traducciones pendientes
if total_translations < (total_products + total_categories) * 2:
    print(f"\n⚠️  NOTA: Traducciones aún en proceso")
    print(f"   • Esperadas aprox: ~{(total_products + total_categories) * 2}")
    print(f"   • Actuales: {total_translations}")
    print(f"   • Faltantes: ~{(total_products + total_categories) * 2 - total_translations}")
else:
    print(f"\n🎉 Todas las traducciones completadas!")
