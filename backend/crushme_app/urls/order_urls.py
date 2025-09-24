"""
Order URLs for CrushMe e-commerce application
Handles order creation, tracking, history, and management
"""
from django.urls import path
from ..views.order_views import (
    get_orders, get_order, create_order, cancel_order,
    track_order, get_recent_orders, get_all_orders,
    update_order_status, get_order_statistics
)

urlpatterns = [
    # Order management
    path('', get_orders, name='get_orders'),
    path('<int:order_id>/', get_order, name='get_order'),
    path('create/', create_order, name='create_order'),
    path('<int:order_id>/cancel/', cancel_order, name='cancel_order'),
    
    # Order tracking
    path('track/<str:order_number>/', track_order, name='track_order'),
    path('recent/', get_recent_orders, name='get_recent_orders'),
    
    # Admin endpoints
    path('admin/all/', get_all_orders, name='get_all_orders'),
    path('admin/<int:order_id>/status/', update_order_status, name='update_order_status'),
    path('admin/statistics/', get_order_statistics, name='get_order_statistics'),
]
