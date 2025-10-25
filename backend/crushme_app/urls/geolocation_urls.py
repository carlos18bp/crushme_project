"""
URL configuration for geolocation endpoints.
"""
from django.urls import path
from ..views import geolocation_views

urlpatterns = [
    # Detect country by IP (manual IP or auto-detect)
    path('detect/', geolocation_views.detect_country_by_ip, name='detect-country'),
    
    # Auto-detect client's country (GET endpoint)
    path('me/', geolocation_views.detect_my_country, name='detect-my-country'),
]
