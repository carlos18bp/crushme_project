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
    get_trending_products, get_woocommerce_products_batch,
    get_product_variations, get_product_variation_detail
)
from ..views.category_views import (
    get_organized_categories, get_category_tree,
    get_products_stats, get_category_stats, get_random_featured_categories
)
from ..views.woocommerce_local_views import (
    get_woocommerce_products_local, get_woocommerce_product_detail_local,
    get_trending_products_local, get_product_variations_local,
    get_product_variation_detail_local,
    get_woocommerce_categories_local, get_woocommerce_stats_local,
    get_organized_categories_local, get_category_tree_local,
    get_random_featured_categories_local, get_product_stock_local
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
    
    # WooCommerce integration endpoints - OPTIMIZED (Local DB)
    path('woocommerce/test/', test_woocommerce_connection, name='test_woocommerce_connection'),
    
    # OPTIMIZED ENDPOINTS - Use local DB with translations (DEFAULT)
    # NOTE: Order matters! More specific paths MUST come before generic ones
    path('woocommerce/products/trending/', get_trending_products_local, name='get_trending_products'),
    path('woocommerce/products/<int:product_id>/variations/<int:variation_id>/', get_product_variation_detail_local, name='get_product_variation_detail'),
    path('woocommerce/products/<int:product_id>/variations/', get_product_variations_local, name='get_product_variations'),
    path('woocommerce/products/<int:product_id>/stock/', get_product_stock_local, name='get_product_stock'),
    path('woocommerce/products/<int:product_id>/', get_woocommerce_product_detail_local, name='get_woocommerce_product_detail'),
    path('woocommerce/products/', get_woocommerce_products_local, name='get_woocommerce_products'),
    path('woocommerce/categories/', get_woocommerce_categories_local, name='get_woocommerce_categories'),
    path('woocommerce/categories/organized/', get_organized_categories_local, name='get_organized_categories'),
    path('woocommerce/categories/tree/', get_category_tree_local, name='get_category_tree'),
    path('woocommerce/categories/featured-random/', get_random_featured_categories_local, name='get_random_featured_categories'),
    path('woocommerce/stats/', get_woocommerce_stats_local, name='get_products_stats'),
    
    # LEGACY ENDPOINTS - Direct WooCommerce API (slower, for compatibility)
    path('woocommerce/legacy/products/', get_woocommerce_products, name='get_woocommerce_products_legacy'),
    path('woocommerce/legacy/products/batch/', get_woocommerce_products_batch, name='get_woocommerce_products_batch'),
    path('woocommerce/legacy/products/trending/', get_trending_products, name='get_trending_products_legacy'),
    path('woocommerce/legacy/categories/', get_woocommerce_categories, name='get_woocommerce_categories_legacy'),
    path('woocommerce/legacy/products/<int:product_id>/', get_woocommerce_product_detail, name='get_woocommerce_product_detail_legacy'),
    path('woocommerce/legacy/products/<int:product_id>/variations/', get_product_variations, name='get_product_variations_legacy'),
    path('woocommerce/legacy/products/<int:product_id>/variations/<int:variation_id>/', get_product_variation_detail, name='get_product_variation_detail'),
    path('woocommerce/legacy/categories/organized/', get_organized_categories, name='get_organized_categories_legacy'),
    path('woocommerce/legacy/categories/tree/', get_category_tree, name='get_category_tree_legacy'),
    path('woocommerce/legacy/categories/featured-random/', get_random_featured_categories, name='get_random_featured_categories_legacy'),
    path('woocommerce/legacy/stats/', get_products_stats, name='get_products_stats_legacy'),
    path('woocommerce/legacy/categories/<int:category_id>/stats/', get_category_stats, name='get_category_stats'),
]
