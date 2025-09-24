"""
Main URL configuration for CrushMe application
Imports all sub-URL configurations
"""
from django.urls import path, include

urlpatterns = [
    path('auth/', include('crushme_app.urls.auth_urls')),
    path('products/', include('crushme_app.urls.product_urls')),
    path('cart/', include('crushme_app.urls.cart_urls')),
    path('orders/', include('crushme_app.urls.order_urls')),
    path('wishlists/', include('crushme_app.urls.wishlist_urls')),
]