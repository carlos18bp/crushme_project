"""
Wompi Order Views
Handles Wompi payment integration for order creation (Colombian market - COP only)
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.conf import settings
import logging

from ..services.wompi_service import wompi_service
from .order_helpers import process_order_after_payment

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_wompi_transaction(request):
    """
    Step 1: Create Wompi transaction for payment (PUBLIC ENDPOINT)
    
    Request Body:
    {
        "customer_email": "customer@example.com",
        "customer_name": "John Doe",
        "items": [
            {
                "woocommerce_product_id": 1234,
                "product_name": "Product Name",
                "quantity": 2,
                "unit_price": 25000,  // COP (pesos colombianos)
                "variation_id": 5679  // Optional - for product variations
            }
        ],
        "shipping_address": "Carrera 80 #50-25 Apto 301",
        "shipping_city": "Medellín",
        "shipping_state": "Antioquia",
        "shipping_postal_code": "050031",
        "shipping_country": "CO",
        "phone_number": "+57 300 1234567",
        "shipping": 15000,  // Costo de envío en COP
        "notes": "Optional notes",
        "gift_message": "Optional gift message",
        "is_gift": false,
        "sender_username": "optional_sender",
        "receiver_username": "optional_receiver"
    }
    
    Returns Wompi transaction_id and payment_url for frontend to redirect user
    """
    try:
        # Extract data from request
        items = request.data.get('items', [])
        customer_name = request.data.get('customer_name', 'Guest')
        customer_email = request.data.get('customer_email', '')
        phone_number = request.data.get('phone_number', '')
        
        # Log received data for debugging
        logger.info(f"📦 [WOMPI] Received {len(items)} items from frontend")
        logger.info(f"👤 [WOMPI] Customer: {customer_name} ({customer_email})")
        logger.info(f"📱 [WOMPI] Phone: {phone_number}")
        for idx, item in enumerate(items):
            logger.info(f"  Item {idx + 1}: {item}")
        
        # Validate items
        if not items or len(items) == 0:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter out empty or invalid items and validate
        valid_items = []
        for item in items:
            # Check if item has all required keys
            if not all(key in item for key in ['woocommerce_product_id', 'product_name', 'quantity', 'unit_price']):
                logger.warning(f"⚠️ Skipping invalid item (missing keys): {item}")
                continue
            
            # Check if values are not empty/null
            if not item.get('woocommerce_product_id') or not item.get('product_name'):
                logger.warning(f"⚠️ Skipping item with empty values: {item}")
                continue
            
            # Check if quantity and price are valid numbers
            try:
                quantity = int(item['quantity'])
                unit_price = float(item['unit_price'])
                
                if quantity <= 0 or unit_price <= 0:
                    logger.warning(f"⚠️ Skipping item with invalid quantity/price: {item}")
                    continue
                
                valid_items.append(item)
            except (ValueError, TypeError) as e:
                logger.warning(f"⚠️ Skipping item with invalid numeric values: {item} - Error: {e}")
                continue
        
        # Check if we have any valid items after filtering
        if not valid_items:
            return Response({
                'error': 'No valid items in cart. All items were filtered out due to invalid data.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Replace items with valid_items
        items = valid_items
        logger.info(f"✅ Validated {len(items)} items for Wompi transaction")
        
        # Calculate total
        items_total = sum(float(item['unit_price']) * item['quantity'] for item in items)
        shipping_cost = float(request.data.get('shipping', 0))
        total_amount = items_total + shipping_cost
        
        # Convert to cents (Wompi requires amount in cents)
        amount_in_cents = int(total_amount * 100)
        
        # Generate unique reference (will be used as order number later)
        from ..models import Order
        reference = Order.generate_order_number()
        
        # Get redirect URL from settings
        redirect_url = f"{settings.FRONTEND_URL}/checkout/wompi/success"
        
        logger.info(f"💰 [WOMPI] Items total: {items_total}, Shipping: {shipping_cost}, Total: {total_amount} COP")
        logger.info(f"💰 [WOMPI] Amount in cents: {amount_in_cents}")
        
        # Create Wompi transaction
        wompi_result = wompi_service.create_transaction(
            amount_in_cents=amount_in_cents,
            reference=reference,
            customer_email=customer_email,
            customer_name=customer_name,
            redirect_url=redirect_url,
            phone_number=phone_number,
            currency='COP'
        )
        
        if wompi_result['success']:
            # Store gift and wishlist data in cache for later retrieval during confirmation
            from django.core.cache import cache
            gift_data = {
                'is_gift': request.data.get('is_gift', False),
                'sender_username': request.data.get('sender_username'),
                'receiver_username': request.data.get('receiver_username'),
                'gift_message': request.data.get('gift_message', ''),
                # Wishlist data
                'is_from_wishlist': request.data.get('is_from_wishlist', False),
                'wishlist_id': request.data.get('wishlist_id'),
                'wishlist_name': request.data.get('wishlist_name')
            }
            
            # Store gift and wishlist data with transaction ID as key (expires in 1 hour)
            cache.set(f'gift_data_{wompi_result["transaction_id"]}', gift_data, 3600)
            
            return Response({
                'success': True,
                'message': 'Wompi transaction created successfully',
                'transaction_id': wompi_result['transaction_id'],
                'payment_url': wompi_result['payment_url'],
                'reference': reference,
                'total': str(total_amount),
                'amount_in_cents': amount_in_cents,
                'items_count': len(items)
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': 'Failed to create Wompi transaction',
                'details': wompi_result.get('error')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"❌ [WOMPI] Error creating transaction: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'error': 'Internal server error',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@transaction.atomic
def confirm_wompi_payment(request):
    """
    Step 2: Confirm Wompi payment and create order (PUBLIC ENDPOINT)
    
    This is called AFTER user completes payment in Wompi
    
    Request Body:
    {
        "transaction_id": "WOMPI-TRANSACTION-ID",
        "customer_email": "customer@example.com",
        "customer_name": "John Doe",
        "items": [
            {
                "woocommerce_product_id": 1234,
                "product_name": "Product Name",
                "quantity": 2,
                "unit_price": 25000,
                "variation_id": 5679  // Optional
            }
        ],
        "shipping_address": "Carrera 80 #50-25",
        "shipping_address_line_2": "Apto 301",  // Optional
        "shipping_city": "Medellín",
        "shipping_state": "Antioquia",
        "shipping_postal_code": "050031",
        "shipping_country": "CO",
        "phone_number": "+57 300 1234567",
        "shipping": 15000,  // Costo de envío en COP
        "notes": "Optional notes",
        "gift_message": "Optional gift message"
    }
    
    Flow:
    1. Verify Wompi payment status
    2. If APPROVED → Use common order processing flow
    3. Create local order, update user history
    4. Send to WooCommerce in background
    """
    try:
        transaction_id = request.data.get('transaction_id')
        
        if not transaction_id:
            return Response({
                'error': 'Wompi transaction ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # STEP 1: Verify payment with Wompi
        logger.info(f"🔵 [WOMPI] Verifying payment: {transaction_id}")
        verification_result = wompi_service.get_transaction(transaction_id)
        
        if not verification_result['success']:
            logger.error(f"❌ [WOMPI] Verification failed: {verification_result.get('error')}")
            return Response({
                'error': 'Payment verification failed',
                'details': verification_result.get('error'),
                'wompi_status': 'FAILED'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if payment was approved
        payment_status = verification_result.get('status')
        if payment_status != 'APPROVED':
            logger.warning(f"⚠️ [WOMPI] Payment not approved: {payment_status}")
            return Response({
                'error': 'Payment was not approved',
                'status': payment_status,
                'transaction_id': transaction_id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Payment approved!
        logger.info(f"✅ [WOMPI] Payment approved: {transaction_id}")
        
        # STEP 2: Use common order processing flow (BIFURCATION MERGE POINT)
        # From here, the flow is the same as PayPal
        payment_info = {
            'transaction_id': transaction_id,
            'status': payment_status,
            'payer_email': verification_result.get('customer_email', request.data.get('customer_email')),
            'payer_name': request.data.get('customer_name', 'Guest')
        }
        
        # Get language from request
        from ..services.translation_service import get_language_from_request
        lang = get_language_from_request(request)
        
        # Call common order processing function
        return process_order_after_payment(
            request_data=dict(request.data),
            payment_info=payment_info,
            payment_provider='wompi',
            lang=lang
        )
    
    except Exception as e:
        logger.error(f"❌ [WOMPI] Error confirming payment: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'error': 'Internal server error',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_wompi_config(request):
    """
    Get Wompi configuration for frontend (PUBLIC ENDPOINT)
    Returns public_key needed for Wompi SDK
    """
    return Response({
        'public_key': settings.WOMPI_PUBLIC_KEY,
        'currency': 'COP',  # Wompi solo soporta COP
        'environment': getattr(settings, 'WOMPI_ENVIRONMENT', 'production')
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def wompi_webhook(request):
    """
    Webhook endpoint for Wompi events (PUBLIC ENDPOINT)
    Wompi will send notifications here when payment status changes
    
    This is optional - can be used for real-time updates
    """
    try:
        # Get signature from headers
        signature = request.headers.get('X-Wompi-Signature', '')
        
        # Verify signature
        if not wompi_service.verify_signature(request.data, signature):
            logger.warning(f"⚠️ [WOMPI WEBHOOK] Invalid signature")
            return Response({
                'error': 'Invalid signature'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get event data
        event_type = request.data.get('event')
        transaction_data = request.data.get('data', {})
        transaction_id = transaction_data.get('id')
        status_value = transaction_data.get('status')
        
        logger.info(f"📬 [WOMPI WEBHOOK] Event: {event_type}, Transaction: {transaction_id}, Status: {status_value}")
        
        # Handle different event types
        if event_type == 'transaction.updated':
            # Transaction status changed
            # You can add logic here to update order status in real-time
            pass
        
        return Response({
            'success': True,
            'message': 'Webhook received'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"❌ [WOMPI WEBHOOK] Error: {str(e)}")
        return Response({
            'error': 'Internal server error',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
