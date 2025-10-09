"""
Product URLs for CrushMe e-commerce application
Handles product CRUD operations, search, and category management
"""
from django.urls import path
from ..views.product_views import (
    get_products, get_product, get_products_by_category, search_products,
    get_categories, create_product, update_product, delete_product,
    update_product_stock, get_featured_products, get_product_recommendations,
    # WooCommerce integration endpoints
    get_woocommerce_products, get_woocommerce_categories, 
    get_woocommerce_product_detail, test_woocommerce_connection,
    get_trending_products, get_woocommerce_products_batch
)
from ..views.category_views import (
    get_organized_categories, get_category_tree,
    get_products_stats, get_category_stats
)

urlpatterns = [
    # Product listing and details
    path('', get_products, name='get_products'),
    path('<int:product_id>/', get_product, name='get_product'),
    
    # Product search and filtering
    path('category/', get_products_by_category, name='get_products_by_category'),
    path('search/', search_products, name='search_products'),
    path('categories/', get_categories, name='get_categories'),
    
    # Featured and recommendations
    path('featured/', get_featured_products, name='get_featured_products'),
    path('<int:product_id>/recommendations/', get_product_recommendations, name='get_product_recommendations'),
    
    # Admin operations
    path('create/', create_product, name='create_product'),
    path('<int:product_id>/update/', update_product, name='update_product'),
    path('<int:product_id>/delete/', delete_product, name='delete_product'),
    path('<int:product_id>/stock/', update_product_stock, name='update_product_stock'),
    
    # WooCommerce integration endpoints (Public)
    path('woocommerce/test/', test_woocommerce_connection, name='test_woocommerce_connection'),
    path('woocommerce/products/', get_woocommerce_products, name='get_woocommerce_products'),
    path('woocommerce/products/batch/', get_woocommerce_products_batch, name='get_woocommerce_products_batch'),
    path('woocommerce/products/trending/', get_trending_products, name='get_trending_products'),
    path('woocommerce/categories/', get_woocommerce_categories, name='get_woocommerce_categories'),
    path('woocommerce/products/<int:product_id>/', get_woocommerce_product_detail, name='get_woocommerce_product_detail'),
    
    # Organized categories endpoints (Public) - NEW!
    path('woocommerce/categories/organized/', get_organized_categories, name='get_organized_categories'),
    path('woocommerce/categories/tree/', get_category_tree, name='get_category_tree'),
    
    # Statistics endpoints (Public) - NEW!
    path('woocommerce/stats/', get_products_stats, name='get_products_stats'),
    path('woocommerce/categories/<int:category_id>/stats/', get_category_stats, name='get_category_stats'),
]
