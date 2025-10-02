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
    
    # Contact endpoints
    path('contact/', include('crushme_app.urls.contact_urls')),
]
