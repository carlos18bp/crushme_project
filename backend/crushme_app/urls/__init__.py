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
    path('favorites/products/', include('crushme_app.urls.favorite_product_urls')),
    path('reviews/', include('crushme_app.urls.review_urls')),
    path('contact/', include('crushme_app.urls.contact_urls')),
]