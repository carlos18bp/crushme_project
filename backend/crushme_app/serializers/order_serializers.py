"""
Order serializers for CrushMe e-commerce application
Handles order creation, tracking, and history
"""
from rest_framework import serializers
from django.db import transaction
from ..models import Order, OrderItem, Cart, Product
from .product_serializers import ProductListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for order items with WooCommerce products
    Includes product information and historical data
    """
    subtotal = serializers.ReadOnlyField()
    # Product info from WooCommerce (stored at purchase time)
    product = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'woocommerce_product_id', 'quantity', 
            'unit_price', 'subtotal', 'product_name', 'product_description', 
            'created_at'
        ]
        read_only_fields = [
            'id', 'woocommerce_product_id', 'product_name', 
            'product_description', 'created_at'
        ]
    
    def get_product(self, obj):
        """
        Return enriched product information from WooCommerce
        Uses cached data from order item and enriches with current WooCommerce data
        """
        from ..services.woocommerce_service import woocommerce_service

        try:
            # Try to get current product data from WooCommerce
            result = woocommerce_service.get_product_by_id(obj.woocommerce_product_id)
            if result['success']:
                wc_product = result['data']

                # Extract image URL
                image_url = None
                if wc_product.get('images') and len(wc_product['images']) > 0:
                    image_url = wc_product['images'][0].get('src')

                return {
                    'id': obj.woocommerce_product_id,
                    'woocommerce_product_id': obj.woocommerce_product_id,
                    'name': wc_product.get('name', obj.product_name),
                    'price': str(obj.unit_price),
                    'regular_price': str(wc_product.get('regular_price', obj.unit_price)),
                    'sale_price': str(wc_product.get('sale_price', obj.unit_price)) if wc_product.get('sale_price') else None,
                    'image_url': image_url,
                    'description': wc_product.get('short_description', obj.product_description),
                    'stock_quantity': wc_product.get('stock_quantity'),
                    'stock_status': wc_product.get('stock_status'),
                    'categories': [cat.get('name') for cat in wc_product.get('categories', [])],
                    'tags': [tag.get('name') for tag in wc_product.get('tags', [])]
                }
            else:
                # Fallback to cached data if WooCommerce fails
                return {
                    'id': obj.woocommerce_product_id,
                    'woocommerce_product_id': obj.woocommerce_product_id,
                    'name': obj.product_name,
                    'price': str(obj.unit_price),
                    'image_url': None,
                    'description': obj.product_description
                }
        except Exception:
            # Fallback to cached data if any error occurs
            return {
                'id': obj.woocommerce_product_id,
                'woocommerce_product_id': obj.woocommerce_product_id,
                'name': obj.product_name,
                'price': str(obj.unit_price),
                'image_url': None,
                'description': obj.product_description
            }


class OrderListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for order lists
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_items = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'total', 'total_items', 'created_at', 'updated_at'
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for individual order views
    Maps database fields to API names
    """
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_items = serializers.ReadOnlyField()
    full_shipping_address = serializers.ReadOnlyField()
    user = serializers.StringRelatedField(read_only=True)
    
    # Map database fields to API names
    shipping_address = serializers.CharField(source='address_line_1', read_only=True)
    shipping_city = serializers.CharField(source='city', read_only=True)
    shipping_state = serializers.CharField(source='state', read_only=True)
    shipping_postal_code = serializers.CharField(source='zipcode', read_only=True)
    shipping_country = serializers.CharField(source='country', read_only=True)
    phone_number = serializers.CharField(source='phone', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'status', 'status_display',
            'total', 'total_items', 'items', 'email', 'name',
            'shipping_address', 'shipping_city', 'shipping_state',
            'shipping_postal_code', 'shipping_country', 'phone_number',
            'full_shipping_address', 'notes', 'gift_message',
            'woocommerce_order_id', 'is_gift', 'sender_username', 'receiver_username',
            'created_at', 'updated_at', 'shipped_at', 'delivered_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'created_at', 'updated_at',
            'shipped_at', 'delivered_at'
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating orders from cart
    """
    class Meta:
        model = Order
        fields = [
            'shipping_address', 'shipping_city', 'shipping_state',
            'shipping_postal_code', 'shipping_country', 'phone_number', 'notes'
        ]
    
    def validate_shipping_address(self, value):
        """Validate shipping address"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Shipping address must be at least 10 characters long."
            )
        return value.strip()
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Phone number must be at least 10 characters long."
            )
        return value.strip() if value else value
    
    def validate(self, attrs):
        """Validate order creation requirements"""
        user = self.context['request'].user
        
        # Check if user has a cart with items
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("No cart found for user.")
        
        if cart.is_empty:
            raise serializers.ValidationError("Cart is empty.")
        
        # Validate stock availability for all cart items
        for item in cart.items.all():
            if not item.product.is_active:
                raise serializers.ValidationError(
                    f"Product '{item.product.name}' is no longer available."
                )
            
            if item.product.stock_quantity < item.quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for '{item.product.name}'. "
                    f"Available: {item.product.stock_quantity}, Required: {item.quantity}"
                )
        
        attrs['cart'] = cart
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        """Create order from cart"""
        cart = validated_data.pop('cart')
        user = self.context['request'].user
        
        # Calculate total
        total = cart.total_price
        
        # Create order
        order = Order.objects.create(
            user=user,
            total=total,
            **validated_data
        )
        
        # Create order items from cart items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                product_name=cart_item.product.name,
                product_description=cart_item.product.description
            )
            
            # Reduce product stock
            cart_item.product.reduce_stock(cart_item.quantity)
        
        # Clear cart after successful order creation
        cart.clear()
        
        return order


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating order status (admin only)
    """
    class Meta:
        model = Order
        fields = ['status']
    
    def validate_status(self, value):
        """Validate status transition"""
        if self.instance:
            current_status = self.instance.status
            
            # Define valid status transitions
            valid_transitions = {
                'pending': ['processing', 'cancelled'],
                'processing': ['shipped', 'cancelled'],
                'shipped': ['delivered'],
                'delivered': ['refunded'],
                'cancelled': [],  # Cannot transition from cancelled
                'refunded': [],   # Cannot transition from refunded
            }
            
            if value not in valid_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot change status from '{current_status}' to '{value}'."
                )
        
        return value
    
    def update(self, instance, validated_data):
        """Update order status with timestamp handling"""
        new_status = validated_data.get('status')
        
        if new_status == 'shipped' and instance.status != 'shipped':
            instance.mark_as_shipped()
        elif new_status == 'delivered' and instance.status != 'delivered':
            instance.mark_as_delivered()
        elif new_status == 'cancelled' and instance.status != 'cancelled':
            instance.cancel_order()
        else:
            instance.status = new_status
            instance.save()
        
        return instance


class OrderTrackingSerializer(serializers.ModelSerializer):
    """
    Serializer for order tracking information
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    can_be_cancelled = serializers.SerializerMethodField()
    estimated_delivery = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'created_at', 'shipped_at', 'delivered_at',
            'can_be_cancelled', 'estimated_delivery'
        ]
    
    def get_can_be_cancelled(self, obj):
        """Check if order can be cancelled"""
        return obj.can_be_cancelled()
    
    def get_estimated_delivery(self, obj):
        """Calculate estimated delivery date"""
        if obj.status == 'shipped' and obj.shipped_at:
            from datetime import timedelta
            # Estimate 3-7 business days for delivery
            estimated = obj.shipped_at + timedelta(days=5)
            return estimated.date()
        return None


class OrderSearchSerializer(serializers.Serializer):
    """
    Serializer for order search parameters
    """
    status = serializers.ChoiceField(
        choices=Order.STATUS_CHOICES,
        required=False,
        help_text="Filter by order status"
    )
    date_from = serializers.DateField(
        required=False,
        help_text="Filter orders from this date"
    )
    date_to = serializers.DateField(
        required=False,
        help_text="Filter orders to this date"
    )
    min_total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Minimum order total"
    )
    max_total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Maximum order total"
    )
    ordering = serializers.ChoiceField(
        choices=[
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('-total', 'Highest Total'),
            ('total', 'Lowest Total'),
            ('status', 'Status'),
        ],
        default='-created_at',
        help_text="Sort order for results"
    )
    
    def validate(self, attrs):
        """Validate search parameters"""
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        min_total = attrs.get('min_total')
        max_total = attrs.get('max_total')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError(
                "Start date cannot be after end date."
            )
        
        if min_total and min_total < 0:
            raise serializers.ValidationError(
                "Minimum total cannot be negative."
            )
        
        if max_total and max_total < 0:
            raise serializers.ValidationError(
                "Maximum total cannot be negative."
            )
        
        if min_total and max_total and min_total > max_total:
            raise serializers.ValidationError(
                "Minimum total cannot be greater than maximum total."
            )
        
        return attrs


class OrderCancelSerializer(serializers.Serializer):
    """
    Serializer for cancelling orders
    """
    reason = serializers.CharField(
        required=False,
        max_length=500,
        help_text="Optional reason for cancellation"
    )
    
    def validate(self, attrs):
        """Validate order can be cancelled"""
        order = self.context['order']

        if not order.can_be_cancelled():
            raise serializers.ValidationError(
                f"Order with status '{order.status}' cannot be cancelled."
            )

        return attrs


class OrderItemLocalSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for order items using ONLY local DB data
    Does NOT query WooCommerce - much faster for purchase history
    """
    subtotal = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'woocommerce_product_id', 'woocommerce_variation_id',
            'quantity', 'unit_price', 'subtotal', 'product_name',
            'product_description', 'product_image', 'created_at'
        ]
        read_only_fields = fields
    
    def get_subtotal(self, obj):
        """Calculate subtotal from stored data"""
        return float(obj.quantity * obj.unit_price)
    
    def get_product_image(self, obj):
        """Get product image from context (batch fetched)"""
        # Image will be provided by parent serializer via context
        product_images = self.context.get('product_images', {})
        return product_images.get(obj.woocommerce_product_id)


class OrderPrivateSerializer(serializers.ModelSerializer):
    """
    Enhanced serializer for private user order endpoints
    Includes shipping information for regular orders but limits it for gifts
    Enriches product information with current WooCommerce data
    """
    items = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_items = serializers.ReadOnlyField()
    full_shipping_address = serializers.ReadOnlyField()

    # Gift information
    gift_summary = serializers.SerializerMethodField()

    # Shipping information (conditional for gifts)
    shipping_address = serializers.SerializerMethodField()
    shipping_city = serializers.SerializerMethodField()
    shipping_state = serializers.SerializerMethodField()
    shipping_postal_code = serializers.SerializerMethodField()
    shipping_country = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'total', 'total_items', 'items', 'email', 'name',
            'shipping_address', 'shipping_city', 'shipping_state',
            'shipping_postal_code', 'shipping_country', 'phone_number',
            'full_shipping_address', 'notes', 'gift_message',
            'woocommerce_order_id', 'is_gift', 'sender_username', 'receiver_username',
            'gift_summary', 'created_at', 'updated_at', 'shipped_at', 'delivered_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'created_at', 'updated_at',
            'shipped_at', 'delivered_at'
        ]

    def get_items(self, obj):
        """Get enriched items with current WooCommerce product data"""
        items_data = []
        for item in obj.items.all():
            try:
                # Get current product data from WooCommerce
                from ..services.woocommerce_service import woocommerce_service
                result = woocommerce_service.get_product_by_id(item.woocommerce_product_id)

                if result['success']:
                    wc_product = result['data']
                    image_url = None
                    if wc_product.get('images') and len(wc_product['images']) > 0:
                        image_url = wc_product['images'][0].get('src')

                    item_data = {
                        'id': item.id,
                        'woocommerce_product_id': item.woocommerce_product_id,
                        'woocommerce_variation_id': item.woocommerce_variation_id,
                        'quantity': item.quantity,
                        'unit_price': float(item.unit_price),
                        'subtotal': float(item.quantity * item.unit_price),
                        'product_name': wc_product.get('name', item.product_name),
                        'product_description': wc_product.get('short_description', item.product_description),
                        'image_url': image_url,
                        'categories': [cat.get('name') for cat in wc_product.get('categories', [])],
                        'stock_status': wc_product.get('stock_status')
                    }
                else:
                    # Fallback to cached data
                    item_data = {
                        'id': item.id,
                        'woocommerce_product_id': item.woocommerce_product_id,
                        'woocommerce_variation_id': item.woocommerce_variation_id,
                        'quantity': item.quantity,
                        'unit_price': float(item.unit_price),
                        'subtotal': float(item.quantity * item.unit_price),
                        'product_name': item.product_name,
                        'product_description': item.product_description,
                        'image_url': None
                    }

                items_data.append(item_data)

            except Exception:
                # Fallback for any error
                items_data.append({
                    'id': item.id,
                    'woocommerce_product_id': item.woocommerce_product_id,
                    'woocommerce_variation_id': item.woocommerce_variation_id,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'subtotal': float(item.quantity * item.unit_price),
                    'product_name': item.product_name,
                    'product_description': item.product_description,
                    'image_url': None
                })

        return items_data

    def get_shipping_address(self, obj):
        """Return shipping address only for non-gift orders"""
        if obj.is_gift:
            return "Dirección de envío privada (regalo)"
        return obj.address_line_1

    def get_shipping_city(self, obj):
        """Return shipping city only for non-gift orders"""
        if obj.is_gift:
            return None
        return obj.city

    def get_shipping_state(self, obj):
        """Return shipping state only for non-gift orders"""
        if obj.is_gift:
            return None
        return obj.state

    def get_shipping_postal_code(self, obj):
        """Return shipping postal code only for non-gift orders"""
        if obj.is_gift:
            return None
        return obj.zipcode

    def get_shipping_country(self, obj):
        """Return shipping country only for non-gift orders"""
        if obj.is_gift:
            return None
        return obj.country

    def get_phone_number(self, obj):
        """Return phone only for non-gift orders"""
        if obj.is_gift:
            return None
        return obj.phone

    def get_gift_summary(self, obj):
        """Return gift summary for gift orders"""
        if not obj.is_gift:
            return None

        return {
            'type': 'gift_order',
            'sender': obj.sender_username,
            'receiver': obj.receiver_username,
            'message': obj.gift_message,
            'privacy_note': 'Shipping details hidden for privacy'
        }


class OrderHistorySerializer(serializers.ModelSerializer):
    """
    Fast serializer for purchase history using ONLY local DB data
    Fetches product images in batch for efficiency
    """
    items = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_items = serializers.ReadOnlyField()
    full_shipping_address = serializers.ReadOnlyField()

    # Gift information
    gift_summary = serializers.SerializerMethodField()

    # Shipping information (conditional for gifts)
    shipping_address = serializers.SerializerMethodField()
    shipping_city = serializers.SerializerMethodField()
    shipping_state = serializers.SerializerMethodField()
    shipping_postal_code = serializers.SerializerMethodField()
    shipping_country = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'total', 'total_items', 'items', 'email', 'name',
            'shipping_address', 'shipping_city', 'shipping_state',
            'shipping_postal_code', 'shipping_country', 'phone_number',
            'full_shipping_address', 'notes', 'gift_message',
            'woocommerce_order_id', 'is_gift', 'sender_username', 'receiver_username',
            'gift_summary', 'created_at', 'updated_at', 'shipped_at', 'delivered_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'created_at', 'updated_at',
            'shipped_at', 'delivered_at'
        ]

    def get_shipping_address(self, obj):
        """Return shipping address only for non-gift orders"""
        if obj.is_gift:
            return "Dirección de envío privada (regalo)"
        return obj.address_line_1

    def get_shipping_city(self, obj):
        """Return shipping city only for non-gift orders"""
        if obj.is_gift:
            return None
        return obj.city

    def get_shipping_state(self, obj):
        """Return shipping state only for non-gift orders"""
        if obj.is_gift:
            return None
        return obj.state

    def get_shipping_postal_code(self, obj):
        """Return shipping postal code only for non-gift orders"""
        if obj.is_gift:
            return None
        return obj.zipcode

    def get_shipping_country(self, obj):
        """Return shipping country only for non-gift orders"""
        if obj.is_gift:
            return None
        return obj.country

    def get_phone_number(self, obj):
        """Return phone only for non-gift orders"""
        if obj.is_gift:
            return None
        return obj.phone

    def get_gift_summary(self, obj):
        """Return gift summary for gift orders"""
        if not obj.is_gift:
            return None

        return {
            'type': 'gift_order',
            'sender': obj.sender_username,
            'receiver': obj.receiver_username,
            'message': obj.gift_message,
            'privacy_note': 'Shipping details hidden for privacy'
        }
    
    def get_items(self, obj):
        """Get items with product images fetched in batch"""
        items = obj.items.all()
        
        # Collect all product IDs
        product_ids = [item.woocommerce_product_id for item in items]
        
        # Fetch images in batch from WooCommerce
        product_images = {}
        if product_ids:
            from ..services.woocommerce_service import woocommerce_service
            for product_id in product_ids:
                try:
                    result = woocommerce_service.get_product_by_id(product_id)
                    if result['success']:
                        wc_product = result['data']
                        if wc_product.get('images') and len(wc_product['images']) > 0:
                            product_images[product_id] = wc_product['images'][0].get('src')
                except Exception:
                    pass  # Skip if product fetch fails
        
        # Serialize items with images in context
        serializer = OrderItemLocalSerializer(
            items, 
            many=True, 
            context={'product_images': product_images}
        )
        return serializer.data
