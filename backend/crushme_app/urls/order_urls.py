"""
Order URLs for CrushMe e-commerce application
Handles order creation, tracking, history, and management
"""
from django.urls import path
from ..views.order_views import (
    get_orders, get_order, create_order, cancel_order,
    track_order, get_recent_orders, get_all_orders,
    update_order_status, get_order_statistics, get_gift_orders, get_user_purchase_history
)
from ..views.paypal_order_views import (
    create_paypal_order, capture_paypal_order, get_paypal_config
)
from ..views.wompi_order_views import (
    create_wompi_transaction, confirm_wompi_payment, get_wompi_config, wompi_webhook
)
from ..views.gift_views import send_gift

urlpatterns = [
    # Gift sending (NEW - Send gifts to other users)
    path('gifts/send/', send_gift, name='send_gift'),

    # PayPal Payment Flow (Use these for checkout with PayPal)
    path('paypal/config/', get_paypal_config, name='get_paypal_config'),
    path('paypal/create/', create_paypal_order, name='create_paypal_order'),
    path('paypal/capture/', capture_paypal_order, name='capture_paypal_order'),
    
    # Wompi Payment Flow (Use these for checkout with Wompi - COP only)
    path('wompi/config/', get_wompi_config, name='get_wompi_config'),
    path('wompi/create/', create_wompi_transaction, name='create_wompi_transaction'),
    path('wompi/confirm/', confirm_wompi_payment, name='confirm_wompi_payment'),
    path('wompi/webhook/', wompi_webhook, name='wompi_webhook'),  # For Wompi event notifications
    
    # Order management (Legacy - direct order creation without payment)
    path('', get_orders, name='get_orders'),
    path('<int:order_id>/', get_order, name='get_order'),
    path('create/', create_order, name='create_order'),  # Legacy endpoint
    path('<int:order_id>/cancel/', cancel_order, name='cancel_order'),
    
    # Order tracking
    path('track/<str:order_number>/', track_order, name='track_order'),
    path('recent/', get_recent_orders, name='get_recent_orders'),

    # Gift orders (NEW - Get user's gift orders)
    path('gifts/', get_gift_orders, name='get_gift_orders'),

    # User purchase history (NEW - Get user's complete purchase history)
    path('history/', get_user_purchase_history, name='get_user_purchase_history'),

    # Admin endpoints
    path('admin/all/', get_all_orders, name='get_all_orders'),
    path('admin/<int:order_id>/status/', update_order_status, name='update_order_status'),
    path('admin/statistics/', get_order_statistics, name='get_order_statistics'),
]
