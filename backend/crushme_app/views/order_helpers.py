"""
Order Helper Functions
Shared logic for order processing across different payment providers (PayPal, Wompi, etc.)
"""
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.contrib.auth import get_user_model
import logging
import threading

from ..models import Order, OrderItem
from ..serializers.order_serializers import OrderDetailSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


def process_order_after_payment(request_data, payment_info, payment_provider='paypal'):
    """
    Process order creation after successful payment capture
    This is the COMMON FLOW that runs after payment is captured (PayPal, Wompi, etc.)
    
    Args:
        request_data: Dict with order data (items, shipping, customer info, etc.)
        payment_info: Dict with payment details from provider
            {
                'transaction_id': 'xxx',  # PayPal order ID, Wompi transaction ID, etc.
                'status': 'COMPLETED',
                'payer_email': 'customer@example.com',
                'payer_name': 'John Doe'
            }
        payment_provider: String identifying payment provider ('paypal', 'wompi')
    
    Returns:
        Response object with order data or error
    """
    try:
        # Get cart items from request
        items = request_data.get('items', [])
        
        if not items or len(items) == 0:
            return Response({
                'error': 'Cart is empty'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate items structure
        for item in items:
            if not all(key in item for key in ['woocommerce_product_id', 'product_name', 'quantity', 'unit_price']):
                return Response({
                    'error': 'Invalid item format'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate total (productos + envío)
        items_total = sum(float(item['unit_price']) * item['quantity'] for item in items)
        shipping_cost = float(request_data.get('shipping', 0))
        total_amount = items_total + shipping_cost
        
        # Get customer info (from request or payment info)
        customer_email = request_data.get('customer_email', payment_info.get('payer_email', 'guest@example.com'))
        customer_name = request_data.get('customer_name', payment_info.get('payer_name', 'Guest'))
        
        # STEP 1: Get or create user
        from .paypal_order_views import get_or_create_user
        user = get_or_create_user(customer_email, customer_name)
        
        # STEP 2: Get gift data from cache (if exists)
        from django.core.cache import cache
        transaction_id = payment_info.get('transaction_id')
        gift_data = cache.get(f'gift_data_{transaction_id}', {})
        
        # STEP 3: Create local order
        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                email=customer_email,
                name=customer_name,
                total=total_amount,
                address_line_1=request_data.get('shipping_address', ''),
                address_line_2=request_data.get('shipping_address_line_2', ''),
                city=request_data.get('shipping_city', ''),
                state=request_data.get('shipping_state', ''),
                zipcode=request_data.get('shipping_postal_code', ''),
                country=request_data.get('shipping_country', 'CO'),
                phone=request_data.get('phone_number', ''),
                notes=request_data.get('notes', ''),
                gift_message=gift_data.get('gift_message', request_data.get('gift_message', '')),
                is_gift=gift_data.get('is_gift', request_data.get('is_gift', False)),
                sender_username=gift_data.get('sender_username', request_data.get('sender_username')),
                receiver_username=gift_data.get('receiver_username', request_data.get('receiver_username')),
                status='processing'  # Payment confirmed, processing order
            )
            
            # Clean up cache after successful order creation
            if gift_data:
                cache.delete(f'gift_data_{transaction_id}')
            
            # Create order items
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    woocommerce_product_id=item['woocommerce_product_id'],
                    woocommerce_variation_id=item.get('variation_id'),
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                    product_name=item['product_name'],
                    product_description=f"Price: ${item['unit_price']}"
                )
            
            logger.info(f"✅ Order {order.order_number} created locally")
        
        # STEP 4: Remove purchased items from wishlist (if purchase is from wishlist)
        is_from_wishlist = gift_data.get('is_from_wishlist', request_data.get('is_from_wishlist', False))
        wishlist_id = gift_data.get('wishlist_id', request_data.get('wishlist_id'))
        
        if is_from_wishlist and wishlist_id:
            try:
                from .gift_views import _remove_purchased_items_from_wishlist
                receiver_username = gift_data.get('receiver_username', request_data.get('receiver_username'))
                _remove_purchased_items_from_wishlist(wishlist_id, items, receiver_username)
                logger.info(f"✅ Removed purchased items from wishlist {wishlist_id}")
            except Exception as e:
                logger.error(f"⚠️ Error removing items from wishlist: {str(e)}")
                # Don't fail the order if wishlist update fails
        
        # STEP 5: Update user history and gift tracking
        from .paypal_order_views import _update_user_history_and_gifts
        receiver_username = gift_data.get('receiver_username', request_data.get('receiver_username'))
        _update_user_history_and_gifts(order, receiver_username)
        
        # STEP 6: Send order to WooCommerce in background (non-blocking)
        from .paypal_order_views import send_to_woocommerce_async
        
        # Build response first (immediate, doesn't wait for WooCommerce)
        order_serializer = OrderDetailSerializer(order)
        
        response_data = {
            'success': True,
            'message': 'Order created successfully',
            'order': order_serializer.data,
            'payment': {
                'provider': payment_provider,
                'transaction_id': transaction_id,
                'status': payment_info.get('status'),
                'payer_email': payment_info.get('payer_email'),
                'payer_name': payment_info.get('payer_name')
            },
            'woocommerce_integration': {
                'status': 'pending',
                'message': 'Order is being sent to WooCommerce in background'
            }
        }
        
        # Start WooCommerce sync in background
        shipping_cost_cents = int(request_data.get('shipping', 0))
        woocommerce_thread = threading.Thread(
            target=send_to_woocommerce_async,
            args=(order.id, shipping_cost_cents),
            name=f"WooCommerce-Sync-{order.order_number}"
        )
        woocommerce_thread.daemon = False
        
        logger.info(f"🔧 [ORDER HELPER] Iniciando thread WooCommerce para orden {order.order_number}")
        woocommerce_thread.start()
        logger.info(f"⏳ WooCommerce sync started in background for order {order.order_number}")
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"❌ Error processing order after payment: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'error': 'Internal server error',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
