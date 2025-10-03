"""
URLs for favorite products endpoints
"""
from django.urls import path
from ..views.favorite_product_views import (
    add_favorite_product,
    remove_favorite_product,
    get_favorite_products,
    check_favorite_status,
    get_favorite_product_ids,
    refresh_favorite_products,
    clear_all_favorites
)

urlpatterns = [
    # Main favorite operations
    path('', get_favorite_products, name='get_favorite_products'),
    path('add/', add_favorite_product, name='add_favorite_product'),
    path('ids/', get_favorite_product_ids, name='get_favorite_product_ids'),
    
    # Single product operations
    path('<int:woocommerce_product_id>/', remove_favorite_product, name='remove_favorite_product'),
    path('<int:woocommerce_product_id>/status/', check_favorite_status, name='check_favorite_status'),
    
    # Bulk operations
    path('refresh/', refresh_favorite_products, name='refresh_favorite_products'),
    path('clear/', clear_all_favorites, name='clear_all_favorites'),
]


