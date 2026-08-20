"""
PayPal Order Views
Handles PayPal payment integration for order creation
"""
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
import logging
import secrets

from ..models import PaymentSession
from ..serializers.order_serializers import OrderDetailSerializer
from ..services.checkout_service import build_checkout_order
from ..services.payment_session_service import (
    mark_session_paid,
    mark_session_processed,
    payment_matches_session,
)
from ..services.paypal_service import paypal_service
from ..throttles import (
    PaymentConfirmRateThrottle,
    PaymentCreateRateThrottle,
    PublicSearchRateThrottle,
)

# Initialize logger
logger = logging.getLogger(__name__)
User = get_user_model()


def create_paypal_order_data(data_dict, authenticated_user=None, language='en'):
    """
    Create PayPal order from data dictionary (internal function)

    Args:
        data_dict: Dictionary containing order data with keys:
            - customer_email, customer_name, items, shipping_address,
            - shipping_city, shipping_state, shipping_postal_code,
            - shipping_country, phone_number, notes, gift_message,
            - is_gift, sender_username, receiver_username, discount_code

    Returns:
        Response-like object with status_code and data attributes
    """
    try:
        order_data = build_checkout_order(
            data_dict,
            currency='USD',
            authenticated_user=authenticated_user,
            language=language,
        )
        shipping_info = {
            'name': order_data['customer_name'],
            'address_line_1': order_data['shipping_address'],
            'city': order_data['shipping_city'],
            'state': order_data['shipping_state'],
            'zipcode': order_data['shipping_postal_code'],
            'country': order_data['shipping_country'],
            'phone': order_data['phone_number'],
        }
        paypal_result = paypal_service.create_order(
            cart_items=order_data['items'],
            shipping_info=shipping_info,
            total_amount=order_data['total'],
            shipping_cost=order_data['shipping'],
            discount_amount=order_data['discount_amount'],
        )

        if paypal_result['success']:
            PaymentSession.objects.create(
                provider=PaymentSession.PROVIDER_PAYPAL,
                reference=paypal_result['order_id'],
                external_id=paypal_result['order_id'],
                expected_amount=order_data['total'],
                currency='USD',
                order_data=order_data,
            )
            return Response({
                'success': True,
                'message': 'PayPal order created successfully',
                'paypal_order_id': paypal_result['order_id'],
                'total': order_data['total'],
                'items_count': len(order_data['items']),
                'discount_applied': bool(order_data['discount_code']),
            }, status=201)
        return Response({'error': 'Failed to create PayPal order'}, status=502)
    except ValidationError as exc:
        return Response({
            'error': 'Invalid checkout data',
            'fields': exc.detail,
        }, status=400)
    except Exception:
        logger.exception('[PAYPAL] Failed to create payment session')
        return Response({'error': 'Internal server error'}, status=500)


def get_or_create_user(email, name):
    """
    Get existing user by email or create a new one
    
    Args:
        email: User email address
        name: User full name
    
    Returns:
        User: Existing or newly created user instance
    """
    try:
        # Try to get existing user by email
        user = User.objects.filter(email=email).first()
        
        if user:
            logger.info('Existing checkout user resolved')
            return user
        
        # Email doesn't exist, create new user
        logger.info('Creating checkout user')
        
        # Generate username from email
        username_base = email.split('@')[0]
        username = username_base
        
        # Ensure unique username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{username_base}{counter}"
            counter += 1
        
        # Parse name into first_name and last_name
        name_parts = name.strip().split()
        first_name = name_parts[0] if name_parts else 'Guest'
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        
        # Generate random secure password (user won't need it, can reset if needed)
        random_password = secrets.token_urlsafe(32)
        
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=random_password,
            first_name=first_name,
            last_name=last_name
        )
        
        logger.info('Checkout user created')
        return user
        
    except Exception:
        logger.exception('Checkout user resolution failed')
        raise


def _update_user_history_and_gifts(order, receiver_username=None):
    """
    Update user purchase history and gift tracking

    Args:
        order: Order instance that was just created
        receiver_username: Username of gift recipient (if this is a gift order)
    """
    try:
        # Add order to purchaser's history
        order.user.purchase_history.add(order)
        logger.info(f"✅ Added order {order.order_number} to {order.user.username}'s purchase history")

        # Handle gift tracking
        if order.is_gift and receiver_username:
            try:
                # Find gift recipient and add to their received gifts
                recipient_user = User.objects.get(username=receiver_username)
                recipient_user.received_gifts.add(order)
                logger.info(f"✅ Added gift order {order.order_number} to {receiver_username}'s received gifts")

                # Increment sender's gift count (if sender is different from order owner)
                if order.sender_username and order.sender_username != order.user.username:
                    try:
                        sender_user = User.objects.get(username=order.sender_username)
                        sender_user.sent_gifts_count += 1
                        sender_user.save(update_fields=['sent_gifts_count'])
                        logger.info(f"✅ Incremented {order.sender_username}'s sent gifts count to {sender_user.sent_gifts_count}")

                    except User.DoesNotExist:
                        logger.warning(f"⚠️ Sender user {order.sender_username} not found for gift count increment")

            except User.DoesNotExist:
                logger.warning(f"⚠️ Gift recipient user {receiver_username} not found")

        logger.info(f"✅ User history and gift tracking updated for order {order.order_number}")

    except Exception as e:
        logger.error(f"❌ Error updating user history and gifts for order {order.order_number}: {str(e)}")


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([PaymentCreateRateThrottle])
def create_paypal_order(request):
    """
    Step 1: Create PayPal order for payment (PUBLIC ENDPOINT)

    Request Body:
    {
        "customer_email": "customer@example.com",
        "customer_name": "John Doe",
        "items": [
            {
                "woocommerce_product_id": 1234,
                "product_name": "Product Name",
                "quantity": 2,
                "unit_price": 25.99,
                "variation_id": 5679  // Optional - for product variations
            }
        ],
        "shipping_address": "Carrera 80 #50-25 Apto 301",
        "shipping_city": "Medellín",
        "shipping_state": "Antioquia",
        "shipping_postal_code": "050031",
        "shipping_country": "CO",
        "phone_number": "+57 300 1234567",
        "shipping": 15000,  // ← Costo de envío en pesos colombianos (opcional)
        "notes": "Optional notes"
    }

    Returns PayPal order_id for frontend to show PayPal popup
    """
    # Convert request.data to dict and call helper function
    result = create_paypal_order_data(
        dict(request.data),
        authenticated_user=request.user,
        language=request.headers.get('Accept-Language', 'en'),
    )

    if result.status_code == 201:
        logger.info(f"✅ PayPal order created: {result.data.get('paypal_order_id')}")
        return Response(result.data, status=status.HTTP_201_CREATED)
    logger.warning('PayPal order creation was rejected')
    return Response(result.data, status=result.status_code)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([PaymentConfirmRateThrottle])
def capture_paypal_order(request):
    """Capture a PayPal order after verifying its durable checkout session."""
    paypal_order_id = request.data.get('paypal_order_id')
    if not paypal_order_id:
        return Response(
            {'error': 'PayPal order ID is required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        session = PaymentSession.objects.select_related('order').get(
            provider=PaymentSession.PROVIDER_PAYPAL,
            external_id=paypal_order_id,
        )
    except PaymentSession.DoesNotExist:
        return Response(
            {'error': 'Payment session not found'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if session.status == PaymentSession.STATUS_PROCESSED and session.order:
        return Response({
            'success': True,
            'message': 'Order already processed',
            'order': OrderDetailSerializer(session.order).data,
            'payment': {
                'provider': PaymentSession.PROVIDER_PAYPAL,
                'paypal_order_id': paypal_order_id,
                'status': 'COMPLETED',
            },
        }, status=status.HTTP_200_OK)

    try:
        capture_result = paypal_service.capture_order(paypal_order_id)
        if not capture_result['success']:
            logger.warning('[PAYPAL] Capture was not completed for order %s', paypal_order_id)
            return Response({
                'error': 'Payment capture failed',
                'paypal_status': capture_result.get('status', 'FAILED'),
            }, status=status.HTTP_400_BAD_REQUEST)

        if not payment_matches_session(
            session,
            capture_result.get('captured_amount'),
            capture_result.get('currency'),
        ):
            logger.error('[PAYPAL] Rejected capture with mismatched amount or currency')
            return Response(
                {'error': 'Payment does not match checkout session'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not mark_session_paid(session, external_id=paypal_order_id):
            return Response(
                {'error': 'Payment session conflict'},
                status=status.HTTP_409_CONFLICT,
            )

        from .order_helpers import process_order_after_payment

        payment_info = {
            'transaction_id': capture_result.get('capture_id') or paypal_order_id,
            'status': capture_result.get('status'),
            'payer_email': capture_result.get('payer_email'),
            'payer_name': capture_result.get('payer_name'),
        }
        result = process_order_after_payment(
            request_data=session.order_data,
            payment_info=payment_info,
            payment_provider=PaymentSession.PROVIDER_PAYPAL,
            lang=session.order_data.get('language', 'en'),
        )
        if result.status_code in {status.HTTP_200_OK, status.HTTP_201_CREATED}:
            if not mark_session_processed(session, result):
                logger.error('[PAYPAL] Could not link processed order to payment session')
                return Response(
                    {'error': 'Payment was captured but order finalization failed'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return result
    except Exception:
        logger.exception('[PAYPAL] Unexpected capture processing failure')
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([PublicSearchRateThrottle])
def get_paypal_config(request):
    """
    Get PayPal configuration for frontend (PUBLIC ENDPOINT)
    Returns client_id needed for PayPal SDK
    """
    from django.conf import settings
    
    return Response({
        'client_id': settings.PAYPAL_CLIENT_ID,
        'currency': 'USD',  # Cambiar según tu moneda
        'mode': settings.PAYPAL_MODE
    }, status=status.HTTP_200_OK)
