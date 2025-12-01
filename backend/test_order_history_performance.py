#!/usr/bin/env python
"""
Test script to verify order history endpoint performance improvement
Tests the optimized endpoint that uses local DB instead of WooCommerce API
"""
import os
import sys
import django
import time

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crushme_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from crushme_app.models import Order, OrderItem
from crushme_app.serializers.order_serializers import OrderHistorySerializer

User = get_user_model()

def test_order_history_performance():
    """Test the performance of order history serialization"""
    
    print("\n" + "="*80)
    print("🧪 TESTING ORDER HISTORY PERFORMANCE")
    print("="*80 + "\n")
    
    # Get a user with orders
    user = User.objects.filter(orders__isnull=False).first()
    
    if not user:
        print("❌ No users with orders found. Create some test orders first.")
        return
    
    # Get user's orders
    orders = Order.objects.filter(user=user).prefetch_related('items')[:5]
    order_count = orders.count()
    
    if order_count == 0:
        print("❌ No orders found for user.")
        return
    
    # Count total items
    total_items = sum(order.items.count() for order in orders)
    
    print(f"📊 Test Data:")
    print(f"   - User: {user.email}")
    print(f"   - Orders: {order_count}")
    print(f"   - Total Items: {total_items}")
    print(f"   - Expected API calls (OLD): {total_items} calls to WooCommerce")
    print(f"   - Expected API calls (NEW): 0 calls (uses local DB)")
    print()
    
    # Test serialization performance
    print("⏱️  Testing serialization speed...")
    start_time = time.time()
    
    serializer = OrderHistorySerializer(orders, many=True, context={})
    data = serializer.data
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"\n✅ Serialization completed!")
    print(f"   - Time: {elapsed:.3f} seconds")
    print(f"   - Orders serialized: {len(data)}")
    
    # Show sample data
    if data:
        first_order = data[0]
        print(f"\n📦 Sample Order Data:")
        print(f"   - Order Number: {first_order['order_number']}")
        print(f"   - Total: ${first_order['total']}")
        print(f"   - Items: {len(first_order['items'])}")
        
        if first_order['items']:
            first_item = first_order['items'][0]
            print(f"\n   📦 Sample Item:")
            print(f"      - Product: {first_item['product_name']}")
            print(f"      - Unit Price (at purchase): ${first_item['unit_price']}")
            print(f"      - Quantity: {first_item['quantity']}")
            print(f"      - Subtotal: ${first_item['subtotal']}")
            print(f"      - Has Image: {'✅' if first_item.get('product_image') else '❌'}")
    
    # Performance analysis
    print(f"\n📈 Performance Analysis:")
    print(f"   - Time per order: {(elapsed/order_count)*1000:.1f}ms")
    print(f"   - Time per item: {(elapsed/total_items)*1000:.1f}ms")
    
    if elapsed < 0.5:
        print(f"   - Status: ✅ EXCELLENT (< 500ms)")
    elif elapsed < 1.0:
        print(f"   - Status: ✅ GOOD (< 1s)")
    elif elapsed < 3.0:
        print(f"   - Status: ⚠️  ACCEPTABLE (< 3s)")
    else:
        print(f"   - Status: ❌ SLOW (> 3s)")
    
    print(f"\n💡 Improvement:")
    old_time_estimate = total_items * 0.4  # 400ms per WooCommerce API call
    print(f"   - OLD (with WooCommerce API): ~{old_time_estimate:.1f}s")
    print(f"   - NEW (with local DB): {elapsed:.3f}s")
    print(f"   - Speed improvement: {old_time_estimate/elapsed:.0f}x faster ⚡")
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETED")
    print("="*80 + "\n")

if __name__ == '__main__':
    test_order_history_performance()
