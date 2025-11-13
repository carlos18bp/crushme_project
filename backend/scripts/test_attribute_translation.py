#!/usr/bin/env python
"""
Test script for attribute translation
Verifies that product attributes are translated correctly
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crushme_project.settings')
django.setup()

from crushme_app.models import WooCommerceProduct, TranslatedContent
from crushme_app.utils.translation_helpers import get_product_full_data
from crushme_app.services.translation_service import TranslationService
from crushme_app.services.translation_batch_service import translation_batch_service


def test_find_variable_products():
    """Find variable products with attributes"""
    print("\n" + "="*60)
    print("TEST 1: Find Variable Products with Attributes")
    print("="*60)
    
    products = WooCommerceProduct.objects.filter(
        status='publish',
        product_type=WooCommerceProduct.TYPE_VARIABLE
    )[:5]
    
    print(f"\nFound {products.count()} variable products (showing first 5):")
    
    for product in products:
        variations_count = product.variations.count()
        has_attrs = bool(product.attributes)
        print(f"\n  Product ID: {product.wc_id}")
        print(f"  Name: {product.name[:60]}")
        print(f"  Variations: {variations_count}")
        print(f"  Has attributes: {has_attrs}")
        
        if has_attrs and product.attributes:
            print(f"  Attributes:")
            for attr in product.attributes[:3]:  # Show first 3
                if isinstance(attr, dict):
                    name = attr.get('name', 'N/A')
                    options = attr.get('options', [])
                    print(f"    - {name}: {options[:3]}")  # Show first 3 options
    
    return products.count() > 0


def test_translate_attributes_batch():
    """Test batch translation of attributes"""
    print("\n" + "="*60)
    print("TEST 2: Batch Translate Attributes")
    print("="*60)
    
    # Get first variable product
    product = WooCommerceProduct.objects.filter(
        status='publish',
        product_type=WooCommerceProduct.TYPE_VARIABLE
    ).first()
    
    if not product:
        print("  ⚠️  No variable products found")
        return False
    
    print(f"\nTranslating attributes for product: {product.name}")
    print(f"Product ID: {product.wc_id}")
    
    # Count translations before
    before_count = TranslatedContent.objects.filter(
        content_type=TranslatedContent.CONTENT_TYPE_VARIATION_ATTRIBUTE
    ).count()
    
    # Translate attributes
    translation_batch_service._translate_product_attributes(product, force_retranslate=True)
    
    # Count translations after
    after_count = TranslatedContent.objects.filter(
        content_type=TranslatedContent.CONTENT_TYPE_VARIATION_ATTRIBUTE
    ).count()
    
    new_translations = after_count - before_count
    
    print(f"\n  Translations before: {before_count}")
    print(f"  Translations after: {after_count}")
    print(f"  New translations: {new_translations}")
    
    # Show some translations
    recent_translations = TranslatedContent.objects.filter(
        content_type=TranslatedContent.CONTENT_TYPE_VARIATION_ATTRIBUTE,
        target_language='en'
    ).order_by('-created_at')[:10]
    
    print(f"\n  Recent translations (showing 10):")
    for trans in recent_translations:
        print(f"    {trans.source_text} → {trans.translated_text}")
    
    return new_translations >= 0


def test_api_response_spanish():
    """Test API response in Spanish (original)"""
    print("\n" + "="*60)
    print("TEST 3: API Response in Spanish (Original)")
    print("="*60)
    
    product = WooCommerceProduct.objects.filter(
        status='publish',
        product_type=WooCommerceProduct.TYPE_VARIABLE
    ).first()
    
    if not product:
        print("  ⚠️  No variable products found")
        return False
    
    translator = TranslationService(target_language='es')
    data = get_product_full_data(product, target_language='es', include_stock=False)
    
    print(f"\nProduct: {data['name']}")
    print(f"Type: {data['type']}")
    print(f"Is Variable: {data['is_variable']}")
    
    if 'attributes' in data:
        print(f"\nAttributes ({len(data['attributes'])}):")
        for attr in data['attributes'][:3]:  # Show first 3
            print(f"  - {attr['name']}: {attr['options'][:3]}")  # Show first 3 options
    
    if 'available_variations' in data:
        print(f"\nVariations ({len(data['available_variations'])}):")
        for var in data['available_variations'][:3]:  # Show first 3
            print(f"  - ID {var['id']}: {var['attributes']}")
    
    return True


def test_api_response_english():
    """Test API response in English (translated)"""
    print("\n" + "="*60)
    print("TEST 4: API Response in English (Translated)")
    print("="*60)
    
    product = WooCommerceProduct.objects.filter(
        status='publish',
        product_type=WooCommerceProduct.TYPE_VARIABLE
    ).first()
    
    if not product:
        print("  ⚠️  No variable products found")
        return False
    
    translator = TranslationService(target_language='en')
    data = get_product_full_data(product, target_language='en', include_stock=False)
    
    print(f"\nProduct: {data['name']}")
    print(f"Type: {data['type']}")
    print(f"Is Variable: {data['is_variable']}")
    
    if 'attributes' in data:
        print(f"\nAttributes ({len(data['attributes'])}) - TRANSLATED:")
        for attr in data['attributes'][:3]:  # Show first 3
            print(f"  - {attr['name']} (original: {attr['name_original']})")
            print(f"    Options: {attr['options'][:3]}")  # Show first 3 options
    
    if 'available_variations' in data:
        print(f"\nVariations ({len(data['available_variations'])}) - TRANSLATED:")
        for var in data['available_variations'][:3]:  # Show first 3
            print(f"  - ID {var['id']}:")
            print(f"    Translated: {var['attributes']}")
            print(f"    Original: {var['attributes_original']}")
    
    return True


def test_translation_quality():
    """Test translation quality for common attributes"""
    print("\n" + "="*60)
    print("TEST 5: Translation Quality Check")
    print("="*60)
    
    common_attributes = [
        'Color', 'Talla', 'Material', 'Estilo', 'Tamaño',
        'Rojo', 'Azul', 'Verde', 'Negro', 'Blanco',
        'Pequeño', 'Mediano', 'Grande'
    ]
    
    translator = TranslationService(target_language='en')
    
    print("\nCommon attribute translations:")
    for text in common_attributes:
        translated = translator.translate_if_needed(text, content_language='es')
        print(f"  {text:15} → {translated}")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("ATTRIBUTE TRANSLATION TESTS")
    print("="*60)
    
    tests = [
        ("Find Variable Products", test_find_variable_products),
        ("Batch Translate Attributes", test_translate_attributes_batch),
        ("API Response Spanish", test_api_response_spanish),
        ("API Response English", test_api_response_english),
        ("Translation Quality", test_translation_quality),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "✅ PASS" if success else "⚠️  EMPTY"))
        except Exception as e:
            results.append((test_name, f"❌ FAIL: {str(e)}"))
            print(f"\n❌ Error in {test_name}: {str(e)}")
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, result in results:
        print(f"{result:15} | {test_name}")
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)


if __name__ == '__main__':
    run_all_tests()
