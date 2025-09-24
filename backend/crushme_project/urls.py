"""
URL configuration for CrushMe e-commerce project
Main URL router that includes app URLs and serves media files in development"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from crushme_app.admin import admin_site

urlpatterns = [
    # Custom Django admin interface (organized by sections)
    path('admin/', admin_site.urls),
    
    # Standard Django admin (fallback)
    path('django-admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('crushme_app.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
