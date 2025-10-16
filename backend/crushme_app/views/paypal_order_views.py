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


def create_paypal_order_data(data_dict):
    """
    Create PayPal order from data dictionary (internal function)

    Args:
        data_dict: Dictionary containing order data with keys:
            - customer_email, customer_name, items, shipping_address,
            - shipping_city, shipping_state, shipping_postal_code,
            - shipping_country, phone_number, notes, gift_message,
            - is_gift, sender_username, receiver_username

    Returns:
        Response-like object with status_code and data attributes
    """
    try:
        # Extract data from dictionary
        items = data_dict.get('items', [])
        customer_name = data_dict.get('customer_name', 'Guest')
        customer_email = data_dict.get('customer_email', '')

        # Validate items
        if not items or len(items) == 0:
            from rest_framework.response import Response
            return Response({'error': 'Cart is empty'}, status=400)

        for item in items:
            if not all(key in item for key in ['woocommerce_product_id', 'product_name', 'quantity', 'unit_price']):
                from rest_framework.response import Response
                return Response({
                    'error': 'Invalid item format. Each item must have: woocommerce_product_id, product_name, quantity, unit_price'
                }, status=400)

        # Get shipping info
        shipping_info = {
            'name': customer_name,
            'address_line_1': data_dict.get('shipping_address', ''),
            'city': data_dict.get('shipping_city', ''),
            'state': data_dict.get('shipping_state', ''),
            'zipcode': data_dict.get('shipping_postal_code', ''),
            'country': data_dict.get('shipping_country', 'CO'),
            'phone': data_dict.get('phone_number', '')
        }

        # Validate required shipping fields
        if not all([shipping_info['address_line_1'], shipping_info['city'],
                   shipping_info['state'], shipping_info['zipcode']]):
            from rest_framework.response import Response
            return Response({'error': 'Missing required shipping information'}, status=400)

        # Build cart items for PayPal
        cart_items = []
        items_total = 0
        for item in items:
            cart_items.append({
                'product_name': item['product_name'],
                'quantity': item['quantity'],
                'unit_price': float(item['unit_price']),
                'woocommerce_product_id': item['woocommerce_product_id']
            })
            items_total += float(item['unit_price']) * item['quantity']

        # Total solo incluye productos para PayPal (envío se maneja en WooCommerce)
        total_amount = items_total

        # Create PayPal order
        paypal_result = paypal_service.create_order(
            cart_items=cart_items,
            shipping_info=shipping_info,
            total_amount=total_amount
        )

        if paypal_result['success']:
            # Store gift data in session-like storage for later retrieval during capture
            # We'll use a simple approach: store in a temporary model or use Django's cache
            from django.core.cache import cache
            gift_data = {
                'is_gift': data_dict.get('is_gift', False),
                'sender_username': data_dict.get('sender_username'),
                'receiver_username': data_dict.get('receiver_username'),
                'gift_message': data_dict.get('gift_message', '')
            }

            # Store gift data with PayPal order ID as key (expires in 1 hour)
            cache.set(f'gift_data_{paypal_result["order_id"]}', gift_data, 3600)

            from rest_framework.response import Response
            return Response({
                'success': True,
                'message': 'PayPal order created successfully',
                'paypal_order_id': paypal_result['order_id'],
                'total': str(total_amount),
                'items_count': len(cart_items)
            }, status=201)
        else:
            from rest_framework.response import Response
            return Response({
                'error': 'Failed to create PayPal order',
                'details': paypal_result.get('error')
            }, status=500)

    except Exception as e:
        from rest_framework.response import Response
        return Response({
            'error': 'Internal server error',
            'details': str(e)
        }, status=500)

logger = logging.getLogger(__name__)
User = get_user_model()


def send_to_woocommerce_async(order_id, shipping_cost_cents=0):
    """
    Send order to WooCommerce in background thread
    This prevents blocking the response to the frontend

    Args:
        order_id: ID of the order to send to WooCommerce
        shipping_cost_cents: Shipping cost in cents for WooCommerce
    """
    import sys
    import time

    # Force flush to ensure logs appear immediately
    print(f"\n{'='*80}", file=sys.stderr, flush=True)
    print(f"🚀 [WOOCOMMERCE THREAD] Thread iniciado para Order ID: {order_id}", file=sys.stderr, flush=True)
    print(f"{'='*80}\n", file=sys.stderr, flush=True)

    try:
        # Small delay to ensure the main transaction is committed
        time.sleep(0.1)

        print(f"📊 [WOOCOMMERCE THREAD] Obteniendo orden de la base de datos...", file=sys.stderr, flush=True)

        # Check if order exists before trying to get it
        if not Order.objects.filter(id=order_id).exists():
            print(f"❌ [WOOCOMMERCE THREAD] Orden {order_id} no existe en la base de datos", file=sys.stderr, flush=True)
            print(f"{'='*80}\n", file=sys.stderr, flush=True)
            return

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
        # Use shipping cost passed as parameter
        print(f"📦 [WOOCOMMERCE THREAD] Shipping cost: {shipping_cost_cents} cents", file=sys.stderr, flush=True)
        wc_result = woocommerce_order_service.send_order(order, shipping_cost=shipping_cost_cents)
        
        if wc_result['success']:
            try:
                # Update order with WooCommerce ID (check if order still exists)
                if Order.objects.filter(id=order.id).exists():
                    order.woocommerce_order_id = wc_result.get('woocommerce_order_id')
                    order.save(update_fields=['woocommerce_order_id'])

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
                    logger.warning(f"⚠️ [WOOCOMMERCE SYNC] Orden {order.order_number} ya no existe para actualizar ID de WooCommerce")
                    logger.warning(f"🆔 [WOOCOMMERCE SYNC] WooCommerce Order ID: {wc_result.get('woocommerce_order_id')} (pero orden local eliminada)")

                    print(f"\n{'='*80}", file=sys.stderr, flush=True)
                    print(f"⚠️ [WOOCOMMERCE THREAD] Orden eliminada después de envío a WooCommerce", file=sys.stderr, flush=True)
                    print(f"🆔 [WOOCOMMERCE THREAD] WC Order ID: {wc_result.get('woocommerce_order_id')}", file=sys.stderr, flush=True)
                    print(f"{'='*80}\n", file=sys.stderr, flush=True)
            except Exception as update_error:
                logger.error(f"❌ [WOOCOMMERCE SYNC] Error actualizando orden con WC ID: {update_error}")

                print(f"\n{'='*80}", file=sys.stderr, flush=True)
                print(f"❌ [WOOCOMMERCE THREAD] Error actualizando orden: {update_error}", file=sys.stderr, flush=True)
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
    result = create_paypal_order_data(dict(request.data))

    if result.status_code == 201:
        logger.info(f"✅ PayPal order created: {result.data.get('paypal_order_id')}")
        return Response(result.data, status=status.HTTP_201_CREATED)
    else:
        logger.error(f"❌ PayPal order creation failed: {result.data}")
        return Response(result.data, status=result.status_code)


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
        "notes": "Optional notes",
        "gift_message": "¡Feliz cumpleaños! Espero que te guste este regalo ❤️"
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
        
        # Calculate total (productos + envío para orden local)
        items_total = sum(float(item['unit_price']) * item['quantity'] for item in items)
        shipping_cost = float(request.data.get('shipping', 0))
        total_amount = items_total + shipping_cost
        
        # Get customer info
        customer_email = request.data.get('customer_email', capture_result.get('payer_email', 'guest@example.com'))
        customer_name = request.data.get('customer_name', capture_result.get('payer_name', 'Guest'))
        
        # STEP 2: Get or create user
        user = get_or_create_user(customer_email, customer_name)
        
        # STEP 3: Try to get gift data from cache (from PayPal order creation)
        from django.core.cache import cache
        gift_data = cache.get(f'gift_data_{paypal_order_id}', {})

        # STEP 3: Create local order (incluye costo de envío en el total)
        shipping_cost_for_order = float(request.data.get('shipping', 0))
        order_total_with_shipping = total_amount + shipping_cost_for_order
        order = Order.objects.create(
            user=user,  # Use obtained/created user
            email=customer_email,
            name=customer_name,
            total=order_total_with_shipping,
            address_line_1=request.data.get('shipping_address', ''),
            city=request.data.get('shipping_city', ''),
            state=request.data.get('shipping_state', ''),
            zipcode=request.data.get('shipping_postal_code', ''),
            country=request.data.get('shipping_country', 'CO'),
            phone=request.data.get('phone_number', ''),
            notes=request.data.get('notes', ''),
            gift_message=gift_data.get('gift_message', request.data.get('gift_message', '')),  # From cache or request
            is_gift=gift_data.get('is_gift', request.data.get('is_gift', False)),  # From cache or request
            sender_username=gift_data.get('sender_username', request.data.get('sender_username')),  # From cache or request
            receiver_username=gift_data.get('receiver_username', request.data.get('receiver_username')),  # From cache or request
            status='processing'  # Payment confirmed, processing order
        )

        # Clean up cache after successful order creation
        if gift_data:
            cache.delete(f'gift_data_{paypal_order_id}')
        
        # Create order items
        for item in items:
            OrderItem.objects.create(
                order=order,
                woocommerce_product_id=item['woocommerce_product_id'],
                woocommerce_variation_id=item.get('variation_id'),  # Optional field
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                product_name=item['product_name'],
                product_description=f"Price: ${item['unit_price']}"
            )
        
        logger.info(f"✅ Order {order.order_number} created locally")

        # STEP 4: Update user history and gift tracking
        _update_user_history_and_gifts(order, receiver_username if 'receiver_username' in locals() else None)

        # STEP 5: Send order to WooCommerce in background (non-blocking)
        # This prevents timeout issues - WooCommerce sync can take time

        # Build response first (immediate, doesn't wait for WooCommerce)
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

        # Start WooCommerce sync in background AFTER building response
        # This ensures the transaction is committed before the thread tries to read
        shipping_cost_cents = int(request.data.get('shipping', 0))
        woocommerce_thread = threading.Thread(
            target=send_to_woocommerce_async,
            args=(order.id, shipping_cost_cents),
            name=f"WooCommerce-Sync-{order.order_number}"
        )
        woocommerce_thread.daemon = False  # Allow thread to complete even if main thread ends

        logger.info(f"🔧 [DEBUG] Iniciando thread DESPUÉS de preparar respuesta...")
        woocommerce_thread.start()
        logger.info(f"🔧 [DEBUG] Thread iniciado! Thread name: {woocommerce_thread.name}, is_alive: {woocommerce_thread.is_alive()}")

        logger.info(f"⏳ WooCommerce sync started in background for order {order.order_number}")

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


def test_paypal_woocommerce_flow():
    """
    Función de prueba para verificar el flujo completo
    Crea una orden de prueba y la envía a WooCommerce
    """
    from decimal import Decimal

    print("🧪 Iniciando prueba del flujo completo...")

    # Crear orden de prueba
    order = Order.objects.create(
        user=User.objects.first() if User.objects.exists() else User.objects.create_user(
            username='test_user', email='test@example.com', password='test123'
        ),
        email='test@example.com',
        name='Usuario de Prueba',
        total=Decimal('100.00'),
        address_line_1='Carrera 80 #50-25',
        city='Medellín',
        state='Antioquia',
        zipcode='050031',
        country='CO',
        phone='+57 300 1234567',
        status='processing'
    )

    # Crear item de prueba
    OrderItem.objects.create(
        order=order,
        woocommerce_product_id=123,
        quantity=1,
        unit_price=Decimal('100.00'),
        product_name='Producto de Prueba'
    )

    print(f"📦 Orden de prueba creada: {order.order_number} (ID: {order.id})")
    print(f"🎁 is_gift: {order.is_gift}")
    print(f"👤 sender_username: {order.sender_username}")
    print(f"🎯 receiver_username: {order.receiver_username}")
    print(f"💌 gift_message: {order.gift_message}")

    # Simular el flujo del hilo de WooCommerce
    print("🔄 Simulando envío a WooCommerce...")

    # Probar envío a WooCommerce con costo de envío real
    shipping_cost_cents = int(request.data.get('shipping', 0))
    result = woocommerce_order_service.send_order(order, shipping_cost=shipping_cost_cents)

    if result['success']:
        print(f"✅ Orden enviada exitosamente a WooCommerce")
        print(f"🆔 WooCommerce Order ID: {result['woocommerce_order_id']}")

        # Actualizar orden local
        order.woocommerce_order_id = result['woocommerce_order_id']
        order.save(update_fields=['woocommerce_order_id'])
        print("✅ Orden local actualizada con ID de WooCommerce")

        # Verificar que la orden existe en la base de datos
        check_order = Order.objects.filter(id=order.id).first()
        if check_order:
            print(f"✅ Orden verificada en BD: {check_order.order_number}")
            print(f"🆔 WC ID en BD: {check_order.woocommerce_order_id}")
            print(f"🎁 is_gift en BD: {check_order.is_gift}")
            print(f"👤 sender_username en BD: {check_order.sender_username}")
            print(f"🎯 receiver_username en BD: {check_order.receiver_username}")
            print(f"💌 gift_message en BD: {check_order.gift_message}")
        else:
            print("❌ Orden no encontrada en BD después de actualizar")
    else:
        print(f"❌ Error enviando orden a WooCommerce: {result['error']}")

    print("✅ Prueba completada")
    return order

