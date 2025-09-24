"""
Cart URLs for CrushMe e-commerce application
Handles shopping cart operations: view, add, update, remove, clear
"""
from django.urls import path
from ..views.cart_views import (
    get_cart, get_cart_summary, add_to_cart, update_cart_item,
    remove_cart_item, clear_cart, validate_cart_for_checkout,
    add_product_to_cart_direct, get_cart_item_count
)

urlpatterns = [
    # Cart overview
    path('', get_cart, name='get_cart'),
    path('summary/', get_cart_summary, name='get_cart_summary'),
    
    # Cart operations
    path('add/', add_to_cart, name='add_to_cart'),
    path('items/<int:item_id>/update/', update_cart_item, name='update_cart_item'),
    path('items/<int:item_id>/remove/', remove_cart_item, name='remove_cart_item'),
    path('clear/', clear_cart, name='clear_cart'),
    
    # Convenience endpoints
    path('products/<int:product_id>/add/', add_product_to_cart_direct, name='add_product_to_cart_direct'),
    path('products/<int:product_id>/count/', get_cart_item_count, name='get_cart_item_count'),
    
    # Checkout validation
    path('validate/', validate_cart_for_checkout, name='validate_cart_for_checkout'),
]
