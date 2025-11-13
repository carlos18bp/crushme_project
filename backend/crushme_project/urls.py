"""
URL configuration for CrushMe e-commerce project
Main URL router that includes app URLs and serves media files in development"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include, re_path
from django.conf.urls.static import static
from crushme_app.admin import admin_site
from crushme_app.views.frontend_views import FrontendView

urlpatterns = [
    # Custom Django admin interface (organized by sections)
    path('admin/', admin_site.urls),
    
    # Standard Django admin (fallback)
    path('django-admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('crushme_app.urls')),
    
    # Frontend routes - Vue.js SPA
    # Root and language-prefixed routes
    path('', FrontendView.as_view(), name='frontend'),
    path('en/', FrontendView.as_view(), name='frontend-en'),
    path('es/', FrontendView.as_view(), name='frontend-es'),
    
    # Authentication routes
    path('en/login/', FrontendView.as_view(), name='login-en'),
    path('es/login/', FrontendView.as_view(), name='login-es'),
    path('en/signup/', FrontendView.as_view(), name='signup-en'),
    path('es/signup/', FrontendView.as_view(), name='signup-es'),
    path('en/verification/', FrontendView.as_view(), name='verification-en'),
    path('es/verification/', FrontendView.as_view(), name='verification-es'),
    path('en/forgot-password/', FrontendView.as_view(), name='forgot-password-en'),
    path('es/forgot-password/', FrontendView.as_view(), name='forgot-password-es'),
    path('en/reset-code/', FrontendView.as_view(), name='reset-code-en'),
    path('es/reset-code/', FrontendView.as_view(), name='reset-code-es'),
    path('en/reset-password/', FrontendView.as_view(), name='reset-password-en'),
    path('es/reset-password/', FrontendView.as_view(), name='reset-password-es'),
    path('en/confirmation/', FrontendView.as_view(), name='confirmation-en'),
    path('es/confirmation/', FrontendView.as_view(), name='confirmation-es'),
    path('en/terms/', FrontendView.as_view(), name='terms-en'),
    path('es/terms/', FrontendView.as_view(), name='terms-es'),
    path('en/privacy/', FrontendView.as_view(), name='privacy-en'),
    path('es/privacy/', FrontendView.as_view(), name='privacy-es'),
    
    # Product routes
    path('en/products/', FrontendView.as_view(), name='products-en'),
    path('es/products/', FrontendView.as_view(), name='products-es'),
    re_path(r'^en/products/category/(?P<category>[\w-]+)/$', FrontendView.as_view(), name='products-by-category-en'),
    re_path(r'^es/products/category/(?P<category>[\w-]+)/$', FrontendView.as_view(), name='products-by-category-es'),
    re_path(r'^en/products/(?P<id>\d+)/$', FrontendView.as_view(), name='product-detail-en'),
    re_path(r'^es/products/(?P<id>\d+)/$', FrontendView.as_view(), name='product-detail-es'),
    
    # Shopping cart routes
    path('en/checkout/', FrontendView.as_view(), name='checkout-en'),
    path('es/checkout/', FrontendView.as_view(), name='checkout-es'),
    path('en/checkout/wompi/success/', FrontendView.as_view(), name='wompi-success-en'),
    path('es/checkout/wompi/success/', FrontendView.as_view(), name='wompi-success-es'),
    
    # Profile routes (protected)
    path('en/profile/', FrontendView.as_view(), name='profile-en'),
    path('es/profile/', FrontendView.as_view(), name='profile-es'),
    path('en/profile/my-profile/', FrontendView.as_view(), name='my-profile-en'),
    path('es/profile/my-profile/', FrontendView.as_view(), name='my-profile-es'),
    path('en/profile/wishlist/', FrontendView.as_view(), name='profile-wishlist-en'),
    path('es/profile/wishlist/', FrontendView.as_view(), name='profile-wishlist-es'),
    path('en/profile/favorites/', FrontendView.as_view(), name='profile-favorites-en'),
    path('es/profile/favorites/', FrontendView.as_view(), name='profile-favorites-es'),
    path('en/profile/my-gifts/', FrontendView.as_view(), name='my-gifts-en'),
    path('es/profile/my-gifts/', FrontendView.as_view(), name='my-gifts-es'),
    path('en/profile/history/', FrontendView.as_view(), name='profile-history-en'),
    path('es/profile/history/', FrontendView.as_view(), name='profile-history-es'),
    
    # About and Contact pages
    path('en/about/', FrontendView.as_view(), name='about-en'),
    path('es/about/', FrontendView.as_view(), name='about-es'),
    path('en/contact/', FrontendView.as_view(), name='contact-en'),
    path('es/contact/', FrontendView.as_view(), name='contact-es'),
    
    # Diaries pages
    path('en/diaries/', FrontendView.as_view(), name='diaries-en'),
    path('es/diaries/', FrontendView.as_view(), name='diaries-es'),
    re_path(r'^en/diaries/@(?P<username>[\w.@+-]+)/$', FrontendView.as_view(), name='diaries-user-en'),
    re_path(r'^es/diaries/@(?P<username>[\w.@+-]+)/$', FrontendView.as_view(), name='diaries-user-es'),
    
    # Wishlist direct checkout routes (with and without language prefix)
    re_path(r'^@(?P<username>[\w.@+-]+)/(?P<wishlist_id>\d+)/$', FrontendView.as_view(), name='wishlist-checkout'),
    re_path(r'^en/@(?P<username>[\w.@+-]+)/(?P<wishlist_id>\d+)/$', FrontendView.as_view(), name='wishlist-checkout-en'),
    re_path(r'^es/@(?P<username>[\w.@+-]+)/(?P<wishlist_id>\d+)/$', FrontendView.as_view(), name='wishlist-checkout-es'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
