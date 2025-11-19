"""
Gift sending views for CrushMe e-commerce application
Handles gift sending between users with shipping verification
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from ..models import UserAddress
from .paypal_order_views import create_paypal_order_data
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_gift(request):
    """
    Send a gift to another user

    Request Body:
    {
        "customer_email": "sender@example.com",  // Optional - email del que envía
        "sender_username": "sender_user",        // Optional - username del que envía
        "receiver_username": "receiver_user",    // Required - username del que recibe
        "items": [
            {
                "woocommerce_product_id": 1234,
                "product_name": "Product Name",
                "quantity": 2,
                "unit_price": 25.99,
                "variation_id": 5679  // Optional
            }
        ],
        "gift_message": "¡Feliz cumpleaños! ❤️"  // Optional - mensaje personalizado
    }

    Returns:
    - If receiver has complete shipping info: Creates PayPal order normally
    - If receiver lacks shipping info: Returns error message
    """
    try:
        # Get receiver username (required)
        receiver_username = request.data.get('receiver_username')
        if not receiver_username:
            return Response({
                'error': 'receiver_username is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get receiver user
        try:
            receiver_user = User.objects.get(username=receiver_username)
        except User.DoesNotExist:
            return Response({
                'error': f'User with username "{receiver_username}" not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if receiver has complete shipping address
        shipping_info = _get_user_shipping_info(receiver_user)

        if not shipping_info['has_complete_info']:
            return Response({
                'error': 'User does not have complete shipping information for receiving gifts',
                'missing_fields': shipping_info['missing_fields'],
                'user_info': {
                    'username': receiver_user.username,
                    'email': receiver_user.email,
                    'has_shipping_address': shipping_info['has_address']
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get gift items
        items = request.data.get('items', [])
        if not items or len(items) == 0:
            return Response({
                'error': 'Items are required for gift'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate items structure
        for item in items:
            if not all(key in item for key in ['woocommerce_product_id', 'product_name', 'quantity', 'unit_price']):
                return Response({
                    'error': 'Invalid item format. Each item must have: woocommerce_product_id, product_name, quantity, unit_price'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Get discount code if provided
        discount_code_raw = request.data.get('discount_code', '')
        discount_code = discount_code_raw.strip().upper() if discount_code_raw else ''
        if discount_code:
            logger.info(f"🎟️ [GIFT] Discount code received: {discount_code}")

        # Get shipping cost from request
        shipping_cost = round(float(request.data.get('shipping', 0)), 2)
        
        # Calculate total (items + shipping)
        items_total = sum(float(item['unit_price']) * item['quantity'] for item in items)
        items_total = round(items_total, 2)
        total_amount = round(items_total + shipping_cost, 2)
        
        # Log for debugging
        logger.info(f"🎁 [GIFT] Items total: {items_total}, Shipping: {shipping_cost}, Total: {total_amount}")

        # Prepare PayPal order data using receiver's shipping info
        paypal_data = {
            'customer_email': receiver_user.email,
            'customer_name': receiver_user.get_full_name() or receiver_username,
            'items': items,
            'shipping': shipping_cost,
            'shipping_address': shipping_info['address']['address_line_1'],
            'shipping_city': shipping_info['address']['city'],
            'shipping_state': shipping_info['address']['state'],
            'shipping_postal_code': shipping_info['address']['zip_code'],
            'shipping_country': shipping_info['address']['country'],
            'phone_number': shipping_info['phone'] or '',
            'notes': request.data.get('notes', ''),
            'gift_message': request.data.get('gift_message', ''),
            'is_gift': True,  # Mark as gift order
            'sender_username': request.data.get('sender_username'),  # Who sent the gift
            'receiver_username': receiver_username,  # Who receives the gift
            'discount_code': discount_code if discount_code else None  # Discount code
        }

        # Create PayPal order
        paypal_response = create_paypal_order_for_gift(paypal_data)

        if paypal_response.status_code == 201:
            return Response({
                'success': True,
                'message': f'Gift order created successfully for {receiver_username}',
                'paypal_order_id': paypal_response.data.get('paypal_order_id'),
                'total': str(total_amount),
                'receiver_info': {
                    'username': receiver_username,
                    'email': receiver_user.email,
                    'name': receiver_user.get_full_name()
                }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': 'Failed to create PayPal order',
                'details': paypal_response.data
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({
            'error': 'Internal server error',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_user_shipping_info(user):
    """
    Get user's shipping information and validate completeness

    Returns:
    {
        'has_complete_info': bool,
        'has_address': bool,
        'missing_fields': list,
        'address': dict or None,
        'phone': str or None
    }
    """
    # Check if user has any address
    try:
        address = UserAddress.objects.get(
            user=user,
            is_default_shipping=True
        )
    except UserAddress.DoesNotExist:
        # Try to get any address for the user
        address = UserAddress.objects.filter(user=user).first()

    if not address:
        return {
            'has_complete_info': False,
            'has_address': False,
            'missing_fields': ['address_line_1', 'city', 'state', 'zip_code', 'country'],
            'address': None,
            'phone': None
        }

    # Check required fields
    required_fields = {
        'address_line_1': address.address_line_1,
        'city': address.city,
        'state': address.state,
        'zip_code': address.zip_code,
        'country': address.country
    }

    missing_fields = []
    for field, value in required_fields.items():
        if not value or str(value).strip() == '':
            missing_fields.append(field)

    # Get phone (from address or user)
    phone = address.guest_phone if address.guest_phone else None
    if not phone and hasattr(user, 'phone') and user.phone:
        phone = user.phone

    has_complete_info = len(missing_fields) == 0

    return {
        'has_complete_info': has_complete_info,
        'has_address': True,
        'missing_fields': missing_fields,
        'address': {
            'address_line_1': address.address_line_1,
            'address_line_2': address.address_line_2,
            'city': address.city,
            'state': address.state,
            'zip_code': address.zip_code,
            'country': address.country,
            'additional_details': address.additional_details
        },
        'phone': phone
    }


def create_paypal_order_for_gift(paypal_data):
    """
    Create PayPal order for gift using the helper function
    """
    return create_paypal_order_data(paypal_data)
