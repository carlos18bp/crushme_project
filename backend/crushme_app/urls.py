"""
URL configuration for CrushMe e-commerce application
Organizes all API endpoints by functionality
"""
from django.urls import path, include

app_name = 'crushme_app'

urlpatterns = [
    # Authentication endpoints
    path('auth/', include('crushme_app.urls.auth_urls')),
    
    # Product endpoints
    path('products/', include('crushme_app.urls.product_urls')),
    
    # Cart endpoints
    path('cart/', include('crushme_app.urls.cart_urls')),
    
    # Order endpoints
    path('orders/', include('crushme_app.urls.order_urls')),
    
    # Wishlist endpoints
    path('wishlists/', include('crushme_app.urls.wishlist_urls')),
    
    # Favorite products endpoints
    path('favorites/products/', include('crushme_app.urls.favorite_product_urls')),
    
    # Review endpoints
    path('reviews/', include('crushme_app.urls.review_urls')),
    
    # Contact endpoints
    path('contact/', include('crushme_app.urls.contact_urls')),
    
    # Feed endpoints
    path('feeds/', include('crushme_app.urls.feed_urls')),
    
    # User search endpoints (for gift sending)
    path('users/', include('crushme_app.urls.user_search_urls')),
    
    # Discount code endpoints
    path('discounts/', include('crushme_app.urls.discount_urls')),
    
    # Geolocation endpoints
    path('geolocation/', include('crushme_app.urls.geolocation_urls')),
]
