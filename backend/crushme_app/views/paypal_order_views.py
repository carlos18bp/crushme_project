"""
PayPal Order Views
Handles PayPal payment integration for order creation
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.contrib.auth import get_user_model
import logging
import secrets
import threading

from ..models import Order, OrderItem
from ..serializers.order_serializers import OrderDetailSerializer
from ..services.paypal_service import paypal_service
from ..services.woocommerce_order_service import woocommerce_order_service

logger = logging.getLogger(__name__)
User = get_user_model()


def send_to_woocommerce_async(order_id):
    """
    Send order to WooCommerce in background thread
    This prevents blocking the response to the frontend
    
    Args:
        order_id: ID of the order to send to WooCommerce
    """
    import sys
    
    # Force flush to ensure logs appear immediately
    print(f"\n{'='*80}", file=sys.stderr, flush=True)
    print(f"🚀 [WOOCOMMERCE THREAD] Thread iniciado para Order ID: {order_id}", file=sys.stderr, flush=True)
    print(f"{'='*80}\n", file=sys.stderr, flush=True)
    
    try:
        from django.db import connection
        # Close the old connection to avoid threading issues
        connection.close()
        
        print(f"📊 [WOOCOMMERCE THREAD] Obteniendo orden de la base de datos...", file=sys.stderr, flush=True)
        
        # Get the order (fresh query in this thread)
        order = Order.objects.get(id=order_id)
        
        print(f"✅ [WOOCOMMERCE THREAD] Orden obtenida: {order.order_number}", file=sys.stderr, flush=True)
        
        logger.info("=" * 80)
        logger.info(f"🔄 [WOOCOMMERCE SYNC] Iniciando sincronización...")
        logger.info(f"📦 [WOOCOMMERCE SYNC] Orden Local: {order.order_number}")
        logger.info(f"💰 [WOOCOMMERCE SYNC] Total: ${order.total}")
        logger.info(f"📧 [WOOCOMMERCE SYNC] Cliente: {order.name} ({order.email})")
        logger.info(f"📍 [WOOCOMMERCE SYNC] Destino: {order.city}, {order.state}, {order.country}")
        
        print(f"🔄 [WOOCOMMERCE THREAD] Enviando a WooCommerce...", file=sys.stderr, flush=True)
        wc_result = woocommerce_order_service.send_order(order)
        
        if wc_result['success']:
            logger.info("=" * 80)
            logger.info(f"✅ [WOOCOMMERCE SYNC] ¡ORDEN ENVIADA EXITOSAMENTE!")
            logger.info(f"🆔 [WOOCOMMERCE SYNC] WooCommerce Order ID: {wc_result.get('woocommerce_order_id')}")
            logger.info(f"🔢 [WOOCOMMERCE SYNC] WooCommerce Order Number: {wc_result.get('woocommerce_order_number')}")
            logger.info(f"📦 [WOOCOMMERCE SYNC] Orden Local: {order.order_number}")
            logger.info(f"🔗 [WOOCOMMERCE SYNC] URL: {wc_result.get('woocommerce_url', 'N/A')}")
            logger.info("=" * 80)
            
            print(f"\n{'='*80}", file=sys.stderr, flush=True)
            print(f"✅ [WOOCOMMERCE THREAD] ÉXITO! WC Order ID: {wc_result.get('woocommerce_order_id')}", file=sys.stderr, flush=True)
            print(f"{'='*80}\n", file=sys.stderr, flush=True)
        else:
            logger.error("=" * 80)
            logger.error(f"❌ [WOOCOMMERCE SYNC] ERROR AL ENVIAR ORDEN")
            logger.error(f"📦 [WOOCOMMERCE SYNC] Orden Local: {order.order_number}")
            logger.error(f"⚠️  [WOOCOMMERCE SYNC] Error: {wc_result.get('error')}")
            logger.error(f"📝 [WOOCOMMERCE SYNC] Detalles: {wc_result.get('details', 'N/A')}")
            logger.error("=" * 80)
            
            print(f"\n{'='*80}", file=sys.stderr, flush=True)
            print(f"❌ [WOOCOMMERCE THREAD] ERROR: {wc_result.get('error')}", file=sys.stderr, flush=True)
            print(f"{'='*80}\n", file=sys.stderr, flush=True)
            
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ [WOOCOMMERCE SYNC] EXCEPCIÓN EN THREAD")
        logger.error(f"📦 [WOOCOMMERCE SYNC] Order ID: {order_id}")
        logger.error(f"⚠️  [WOOCOMMERCE SYNC] Error: {str(e)}")
        logger.error("=" * 80)
        import traceback
        logger.error(traceback.format_exc())
        
        print(f"\n{'='*80}", file=sys.stderr, flush=True)
        print(f"❌ [WOOCOMMERCE THREAD] EXCEPCIÓN: {str(e)}", file=sys.stderr, flush=True)
        print(f"{'='*80}\n", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)


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
            logger.info(f"✅ Usuario existente encontrado: {email}")
            return user
        
        # Email doesn't exist, create new user
        logger.info(f"📝 Creando nuevo usuario para: {email}")
        
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
        
        logger.info(f"✅ Nuevo usuario creado: {username} ({email})")
        return user
        
    except Exception as e:
        logger.error(f"❌ Error al obtener/crear usuario: {str(e)}")
        raise


@api_view(['POST'])
@permission_classes([AllowAny])
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
                "unit_price": 25.99
            }
        ],
        "shipping_address": "Carrera 80 #50-25 Apto 301",
        "shipping_city": "Medellín",
        "shipping_state": "Antioquia",
        "shipping_postal_code": "050031",
        "shipping_country": "CO",
        "phone_number": "+57 300 1234567",
        "notes": "Optional notes"
    }
    
    Returns PayPal order_id for frontend to show PayPal popup
    """
    try:
        # Get cart items from request
        items = request.data.get('items', [])
        
        if not items or len(items) == 0:
            return Response({
                'error': 'Cart is empty'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate items structure
        for item in items:
            if not all(key in item for key in ['woocommerce_product_id', 'product_name', 'quantity', 'unit_price']):
                return Response({
                    'error': 'Invalid item format. Each item must have: woocommerce_product_id, product_name, quantity, unit_price'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get customer info
        customer_name = request.data.get('customer_name', 'Guest')
        customer_email = request.data.get('customer_email', '')
        
        # Get shipping info from request
        shipping_info = {
            'name': customer_name,
            'address_line_1': request.data.get('shipping_address', ''),
            'city': request.data.get('shipping_city', ''),
            'state': request.data.get('shipping_state', ''),
            'zipcode': request.data.get('shipping_postal_code', ''),
            'country': request.data.get('shipping_country', 'CO'),
            'phone': request.data.get('phone_number', '')
        }
        
        # Validate required fields
        if not all([shipping_info['address_line_1'], shipping_info['city'], 
                   shipping_info['state'], shipping_info['zipcode']]):
            return Response({
                'error': 'Missing required shipping information'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Build cart items for PayPal
        cart_items = []
        total_amount = 0
        for item in items:
            cart_items.append({
                'product_name': item['product_name'],
                'quantity': item['quantity'],
                'unit_price': float(item['unit_price']),
                'woocommerce_product_id': item['woocommerce_product_id']
            })
            total_amount += float(item['unit_price']) * item['quantity']
        
        # Create PayPal order
        paypal_result = paypal_service.create_order(
            cart_items=cart_items,
            shipping_info=shipping_info,
            total_amount=total_amount
        )
        
        if paypal_result['success']:
            logger.info(f"✅ PayPal order created: {paypal_result['order_id']}")
            
            return Response({
                'success': True,
                'message': 'PayPal order created successfully',
                'paypal_order_id': paypal_result['order_id'],
                'total': str(total_amount),
                'items_count': len(cart_items)
            }, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"❌ PayPal order creation failed: {paypal_result.get('error')}")
            return Response({
                'error': 'Failed to create PayPal order',
                'details': paypal_result.get('error')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"❌ Error creating PayPal order: {str(e)}")
        return Response({
            'error': 'Internal server error',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@transaction.atomic
def capture_paypal_order(request):
    """
    Step 2: Capture PayPal payment and create order (PUBLIC ENDPOINT)
    
    This is called AFTER user approves payment in PayPal popup
    
    Request Body:
    {
        "paypal_order_id": "PAYPAL-ORDER-ID",
        "customer_email": "customer@example.com",
        "customer_name": "John Doe",
        "items": [
            {
                "woocommerce_product_id": 1234,
                "product_name": "Product Name",
                "quantity": 2,
                "unit_price": 25.99
            }
        ],
        "shipping_address": "Carrera 80 #50-25 Apto 301",
        "shipping_city": "Medellín",
        "shipping_state": "Antioquia",
        "shipping_postal_code": "050031",
        "shipping_country": "CO",
        "phone_number": "+57 300 1234567",
        "notes": "Optional notes"
    }
    
    Flow:
    1. Capture PayPal payment
    2. Get or create user account (auto-register if new email)
    3. If successful → Create local order
    4. Return immediate response to frontend (fast)
    5. Send order to WooCommerce in background (slow, non-blocking)
    
    Note: WooCommerce sync happens asynchronously to prevent timeout issues.
    """
    try:
        paypal_order_id = request.data.get('paypal_order_id')
        
        if not paypal_order_id:
            return Response({
                'error': 'PayPal order ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get cart items from request
        items = request.data.get('items', [])
        
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
        
        # STEP 1: Capture PayPal payment
        logger.info(f"Capturing PayPal payment: {paypal_order_id}")
        capture_result = paypal_service.capture_order(paypal_order_id)
        
        if not capture_result['success']:
            logger.error(f"❌ PayPal capture failed: {capture_result.get('error')}")
            return Response({
                'error': 'Payment capture failed',
                'details': capture_result.get('error'),
                'paypal_status': 'FAILED'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Payment captured successfully!
        logger.info(f"✅ PayPal payment captured: {paypal_order_id}")
        
        # Calculate total
        total_amount = sum(float(item['unit_price']) * item['quantity'] for item in items)
        
        # Get customer info
        customer_email = request.data.get('customer_email', capture_result.get('payer_email', 'guest@example.com'))
        customer_name = request.data.get('customer_name', capture_result.get('payer_name', 'Guest'))
        
        # STEP 2: Get or create user
        user = get_or_create_user(customer_email, customer_name)
        
        # STEP 3: Create local order
        order = Order.objects.create(
            user=user,  # Use obtained/created user
            email=customer_email,
            name=customer_name,
            total=total_amount,
            address_line_1=request.data.get('shipping_address', ''),
            city=request.data.get('shipping_city', ''),
            state=request.data.get('shipping_state', ''),
            zipcode=request.data.get('shipping_postal_code', ''),
            country=request.data.get('shipping_country', 'CO'),
            phone=request.data.get('phone_number', ''),
            notes=request.data.get('notes', ''),
            status='processing'  # Payment confirmed, processing order
        )
        
        # Create order items
        for item in items:
            OrderItem.objects.create(
                order=order,
                woocommerce_product_id=item['woocommerce_product_id'],
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                product_name=item['product_name'],
                product_description=f"Price: ${item['unit_price']}"
            )
        
        logger.info(f"✅ Order {order.order_number} created locally")
        
        # STEP 4: Send order to WooCommerce in background (non-blocking)
        # This prevents timeout issues - WooCommerce sync can take time
        logger.info(f"🔧 [DEBUG] Creando thread para WooCommerce sync (Order ID: {order.id})")
        
        woocommerce_thread = threading.Thread(
            target=send_to_woocommerce_async,
            args=(order.id,),
            name=f"WooCommerce-Sync-{order.order_number}"
        )
        woocommerce_thread.daemon = False  # Allow thread to complete even if main thread ends
        
        logger.info(f"🔧 [DEBUG] Iniciando thread...")
        woocommerce_thread.start()
        logger.info(f"🔧 [DEBUG] Thread iniciado! Thread name: {woocommerce_thread.name}, is_alive: {woocommerce_thread.is_alive()}")
        
        logger.info(f"⏳ WooCommerce sync started in background for order {order.order_number}")
        
        # Build response (immediate, doesn't wait for WooCommerce)
        order_serializer = OrderDetailSerializer(order)
        
        response_data = {
            'success': True,
            'message': 'Order created successfully',
            'order': order_serializer.data,
            'payment': {
                'provider': 'paypal',
                'paypal_order_id': paypal_order_id,
                'status': capture_result.get('status'),
                'payer_email': capture_result.get('payer_email'),
                'payer_name': capture_result.get('payer_name')
            },
            'woocommerce_integration': {
                'status': 'pending',
                'message': 'Order is being sent to WooCommerce in background'
            }
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"❌ Error capturing PayPal order: {str(e)}")
        return Response({
            'error': 'Internal server error',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
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

