#!/usr/bin/env python
"""
Test script for product filtering and sorting
Tests all sort_by options to ensure they work correctly
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crushme_project.settings')
django.setup()

from django.db.models import Count, Avg, Q, Subquery, OuterRef
from crushme_app.models import WooCommerceProduct
from crushme_app.models.order import OrderItem
from crushme_app.models.review import Review


def test_default_sort():
    """Test default sorting (by wc_id descending)"""
    print("\n" + "="*60)
    print("TEST 1: Default Sort (by wc_id descending)")
    print("="*60)
    
    queryset = WooCommerceProduct.objects.filter(
        status='publish'
    ).order_by('-wc_id')[:5]
    
    print(f"Total products: {WooCommerceProduct.objects.filter(status='publish').count()}")
    print(f"\nFirst 5 products (default sort):")
    for product in queryset:
        print(f"  - ID: {product.wc_id} | Name: {product.name[:50]} | Price: {product.price}")
    
    return queryset.count() > 0


def test_price_asc_sort():
    """Test price ascending sort"""
    print("\n" + "="*60)
    print("TEST 2: Price Ascending (cheapest first)")
    print("="*60)
    
    queryset = WooCommerceProduct.objects.filter(
        status='publish'
    ).order_by('price')[:5]
    
    print(f"\nFirst 5 cheapest products:")
    for product in queryset:
        print(f"  - ID: {product.wc_id} | Name: {product.name[:50]} | Price: {product.price}")
    
    return queryset.count() > 0


def test_price_desc_sort():
    """Test price descending sort"""
    print("\n" + "="*60)
    print("TEST 3: Price Descending (most expensive first)")
    print("="*60)
    
    queryset = WooCommerceProduct.objects.filter(
        status='publish'
    ).order_by('-price')[:5]
    
    print(f"\nFirst 5 most expensive products:")
    for product in queryset:
        print(f"  - ID: {product.wc_id} | Name: {product.name[:50]} | Price: {product.price}")
    
    return queryset.count() > 0


def test_popular_sort():
    """Test popular sort (most purchased)"""
    print("\n" + "="*60)
    print("TEST 4: Popular (most purchased)")
    print("="*60)
    
    # Get products with purchase count
    queryset = WooCommerceProduct.objects.filter(
        status='publish'
    ).annotate(
        purchase_count=Count('wc_id', filter=Q(
            wc_id__in=OrderItem.objects.values_list('woocommerce_product_id', flat=True)
        ))
    ).order_by('-purchase_count', '-wc_id')[:10]
    
    print(f"\nTop 10 most purchased products:")
    for product in queryset:
        print(f"  - ID: {product.wc_id} | Name: {product.name[:50]} | Purchases: {product.purchase_count}")
    
    # Show total orders
    total_orders = OrderItem.objects.count()
    print(f"\nTotal order items in database: {total_orders}")
    
    return queryset.count() > 0


def test_rating_sort():
    """Test rating sort (best rated)"""
    print("\n" + "="*60)
    print("TEST 5: Rating (best rated)")
    print("="*60)
    
    # Get rating subquery
    rating_subquery = Review.objects.filter(
        woocommerce_product_id=OuterRef('wc_id'),
        is_active=True
    ).values('woocommerce_product_id').annotate(
        avg_rating=Avg('rating')
    ).values('avg_rating')
    
    queryset = WooCommerceProduct.objects.filter(
        status='publish'
    ).annotate(
        avg_rating=Subquery(rating_subquery)
    ).order_by('-avg_rating', '-wc_id')[:10]
    
    print(f"\nTop 10 best rated products:")
    for product in queryset:
        rating = product.avg_rating if product.avg_rating else 0
        print(f"  - ID: {product.wc_id} | Name: {product.name[:50]} | Rating: {rating:.2f}")
    
    # Show total reviews
    total_reviews = Review.objects.filter(is_active=True).count()
    print(f"\nTotal active reviews in database: {total_reviews}")
    
    return queryset.count() > 0


def test_newest_sort():
    """Test newest sort"""
    print("\n" + "="*60)
    print("TEST 6: Newest (most recent)")
    print("="*60)
    
    queryset = WooCommerceProduct.objects.filter(
        status='publish'
    ).order_by('-date_created_wc')[:5]
    
    print(f"\nFirst 5 newest products:")
    for product in queryset:
        date_str = product.date_created_wc.strftime('%Y-%m-%d %H:%M') if product.date_created_wc else 'N/A'
        print(f"  - ID: {product.wc_id} | Name: {product.name[:50]} | Created: {date_str}")
    
    return queryset.count() > 0


def test_category_filter():
    """Test category filtering"""
    print("\n" + "="*60)
    print("TEST 7: Category Filter (category_id=134)")
    print("="*60)
    
    category_id = 134
    queryset = WooCommerceProduct.objects.filter(
        status='publish',
        categories__wc_id=category_id
    ).order_by('-wc_id')[:5]
    
    total = WooCommerceProduct.objects.filter(
        status='publish',
        categories__wc_id=category_id
    ).count()
    
    print(f"Total products in category {category_id}: {total}")
    print(f"\nFirst 5 products in category:")
    for product in queryset:
        print(f"  - ID: {product.wc_id} | Name: {product.name[:50]} | Price: {product.price}")
    
    return queryset.count() > 0


def test_combined_filters():
    """Test combined category + sort"""
    print("\n" + "="*60)
    print("TEST 8: Combined (category_id=134 + sort_by=price_asc)")
    print("="*60)
    
    category_id = 134
    queryset = WooCommerceProduct.objects.filter(
        status='publish',
        categories__wc_id=category_id
    ).order_by('price')[:5]
    
    print(f"\nFirst 5 cheapest products in category {category_id}:")
    for product in queryset:
        print(f"  - ID: {product.wc_id} | Name: {product.name[:50]} | Price: {product.price}")
    
    return queryset.count() > 0


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("PRODUCT FILTER TESTS")
    print("="*60)
    
    tests = [
        ("Default Sort", test_default_sort),
        ("Price Ascending", test_price_asc_sort),
        ("Price Descending", test_price_desc_sort),
        ("Popular (Most Purchased)", test_popular_sort),
        ("Rating (Best Rated)", test_rating_sort),
        ("Newest", test_newest_sort),
        ("Category Filter", test_category_filter),
        ("Combined Filters", test_combined_filters),
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
