"""
Order Helper Functions
Shared logic for order processing across different payment providers (PayPal, Wompi, etc.)
"""
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone
from django.contrib.auth import get_user_model
import logging

from ..models import Order, OrderItem, Feed
from ..serializers.order_serializers import OrderDetailSerializer
from ..services.email_service import email_service
from ..tasks import sync_order_to_woocommerce

logger = logging.getLogger(__name__)
User = get_user_model()


def process_order_after_payment(request_data, payment_info, payment_provider='paypal', lang='es'):
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
        lang: Language code ('es' or 'en') for feed messages
    
    Returns:
        Response object with order data or error
    """
    try:
        transaction_id = payment_info.get('transaction_id')
        if not transaction_id:
            return Response({
                'error': 'Payment transaction ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        existing_order = Order.objects.filter(transaction_id=transaction_id).first()
        if existing_order:
            return Response({
                'success': True,
                'message': 'Order already processed',
                'order': OrderDetailSerializer(existing_order).data,
                'payment': {
                    'provider': payment_provider,
                    'transaction_id': transaction_id,
                    'status': payment_info.get('status'),
                },
            }, status=status.HTTP_200_OK)

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
        
        # The checkout service already computed the discounted, gateway-verified total.
        items_total = sum(float(item['unit_price']) * item['quantity'] for item in items)
        shipping_cost = float(request_data.get('shipping', 0))
        total_amount = float(request_data.get('total', items_total + shipping_cost))
        if total_amount <= 0:
            return Response({
                'error': 'Invalid order total'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get customer info (from request or payment info)
        customer_email = request_data.get('customer_email', payment_info.get('payer_email', 'guest@example.com'))
        customer_name = request_data.get('customer_name', payment_info.get('payer_name', 'Guest'))
        
        # STEP 1: Get or create user
        from .paypal_order_views import get_or_create_user
        user = get_or_create_user(customer_email, customer_name)
        
        # STEP 2: Get gift data from cache (if exists)
        from django.core.cache import cache
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
                transaction_id=transaction_id,  # Save payment transaction ID
                payment_provider=payment_provider,  # Save payment provider
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
                    woocommerce_variation_id=(
                        item.get('woocommerce_variation_id')
                        or item.get('variation_id')
                    ),
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                    product_name=item['product_name'],
                    product_description=f"Price: ${item['unit_price']}"
                )
            
            discount_code = request_data.get('discount_code')
            if discount_code:
                from ..models import DiscountCode

                DiscountCode.objects.filter(code=discount_code).update(
                    times_used=F('times_used') + 1,
                    updated_at=timezone.now(),
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
        
        # STEP 5.5: Send email notifications
        try:
            # Detect currency based on payment provider
            # Wompi = COP, PayPal = USD
            currency = 'COP' if payment_provider == 'wompi' else 'USD'
            
            # Prepare items for email (filter out dropshipping products)
            email_items = []
            dropshipping_cost = 0
            
            for item in items:
                # Check if product is dropshipping (ID 48500 or contains "dropshipping" in name)
                is_dropshipping = (
                    item.get('woocommerce_product_id') == 48500 or
                    'dropshipping' in item.get('product_name', '').lower()
                )
                
                if is_dropshipping:
                    # Add dropshipping cost to shipping
                    dropshipping_cost += float(item['unit_price']) * item['quantity']
                    logger.info(f"📦 Dropshipping product found: {item['product_name']} - Adding ${dropshipping_cost} to shipping")
                else:
                    # Use product name from request (frontend sends it)
                    product_name = item.get('product_name', 'Product')
                    # Price with margin (unit_price already includes margin from frontend)
                    unit_price = float(item['unit_price'])
                    # Format price based on currency
                    if currency == 'COP':
                        formatted_price = f"{int(round(unit_price))}"
                    else:
                        formatted_price = f"{round(unit_price, 2):.2f}"
                    
                    # Add regular product to email items (name, quantity, and price)
                    email_items.append({
                        'name': product_name,
                        'quantity': item['quantity'],
                        'price': formatted_price
                    })
            
            # Calculate shipping for email (includes dropshipping cost)
            email_shipping = shipping_cost + dropshipping_cost
            
            # Calculate subtotal (only regular products)
            email_subtotal = sum(float(item['unit_price']) * item['quantity'] for item in items if not (
                item.get('woocommerce_product_id') == 48500 or 'dropshipping' in item.get('product_name', '').lower()
            ))
            
            # Format amounts based on currency
            if currency == 'COP':
                # COP: no decimals
                formatted_total = f"{int(round(total_amount))}"
                formatted_subtotal = f"{int(round(email_subtotal))}"
                formatted_shipping = f"{int(round(email_shipping))}"
            else:
                # USD: 2 decimals
                formatted_total = f"{round(total_amount, 2):.2f}"
                formatted_subtotal = f"{round(email_subtotal, 2):.2f}"
                formatted_shipping = f"{round(email_shipping, 2):.2f}"
            
            # Send order confirmation to purchaser
            email_service.send_order_confirmation(
                to_email=customer_email,
                order_number=order.order_number,
                total=formatted_total,
                subtotal=formatted_subtotal,
                shipping=formatted_shipping,
                currency=currency,
                items=email_items,
                username=user.username,
                lang=lang
            )
            logger.info(
                'Order confirmation email accepted for order %s',
                order.order_number,
            )
            
            # Create feed entry for order confirmation
            try:
                Feed.create_feed_entry(
                    user=user,
                    action='order_confirmation',
                    lang=lang
                )
            except Exception as feed_error:
                logger.error(f"Feed creation error: {str(feed_error)}")
            
            # If it's a gift, send notifications
            if order.is_gift and receiver_username:
                try:
                    receiver_user = User.objects.get(username=receiver_username)
                    
                    # Send gift received notification to receiver
                    email_service.send_gift_received_notification(
                        to_email=receiver_user.email,
                        sender_username=user.username,
                        gift_message=order.gift_message or '',
                        order_number=order.order_number,
                        username=receiver_user.username,
                        lang=lang
                    )
                    logger.info(
                        'Gift recipient notification accepted for order %s',
                        order.order_number,
                    )
                    
                    # Create feed entry for gift received
                    try:
                        Feed.create_feed_entry(
                            user=receiver_user,
                            action='gift_received',
                            lang=lang,
                            sender_username=user.username
                        )
                    except Exception as feed_error:
                        logger.error(f"Feed creation error: {str(feed_error)}")
                    
                    # Send gift sent confirmation to sender
                    email_service.send_gift_sent_confirmation(
                        to_email=customer_email,
                        receiver_username=receiver_user.username,
                        order_number=order.order_number,
                        username=user.username,
                        lang=lang
                    )
                    logger.info(
                        'Gift sender notification accepted for order %s',
                        order.order_number,
                    )
                    
                    # Create feed entry for gift sent
                    try:
                        Feed.create_feed_entry(
                            user=user,
                            action='gift_sent',
                            lang=lang,
                            receiver_username=receiver_user.username
                        )
                    except Exception as feed_error:
                        logger.error(f"Feed creation error: {str(feed_error)}")
                    
                except User.DoesNotExist:
                    logger.warning(f"⚠️ Receiver user {receiver_username} not found for gift notifications")
        except Exception:
            logger.exception('Order notification processing failed')
            # Don't fail the order if email fails
        
        # STEP 6: Send order to WooCommerce in background (non-blocking)
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
        shipping_cost_value = request_data.get('shipping', '0')
        transaction.on_commit(
            lambda: sync_order_to_woocommerce(order.id, str(shipping_cost_value))
        )
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    except IntegrityError:
        existing_order = Order.objects.filter(
            transaction_id=payment_info.get('transaction_id')
        ).first()
        if existing_order:
            return Response({
                'success': True,
                'message': 'Order already processed',
                'order': OrderDetailSerializer(existing_order).data,
            }, status=status.HTTP_200_OK)
        logger.exception('Payment order persistence conflict')
        return Response({
            'error': 'Order persistence conflict'
        }, status=status.HTTP_409_CONFLICT)
    except Exception:
        logger.exception('Order post-payment processing failed')
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
