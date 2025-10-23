"""
URL patterns for discount code endpoints
"""
from django.urls import path
from ..views.discount_views import validate_discount_code

urlpatterns = [
    # POST /api/discounts/validate/ - Validate a discount code
    path('validate/', validate_discount_code, name='validate_discount_code'),
]
