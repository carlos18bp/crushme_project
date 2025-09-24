"""
Cart serializers for CrushMe e-commerce application
Handles shopping cart functionality with items and calculations
"""
from rest_framework import serializers
from ..models import Cart, CartItem, Product
from .product_serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for cart items
    Includes product information and calculated subtotal
    """
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'quantity', 'unit_price',
            'subtotal', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'unit_price', 'created_at', 'updated_at']
    
    def validate_product_id(self, value):
        """Validate product exists and is available"""
        try:
            product = Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
        
        if not product.is_active:
            raise serializers.ValidationError("Product is not available.")
        
        return value
    
    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value
    
    def validate(self, attrs):
        """Validate cart item data"""
        product_id = attrs.get('product_id')
        quantity = attrs.get('quantity')
        
        if product_id and quantity:
            try:
                product = Product.objects.get(id=product_id)
                if product.stock_quantity < quantity:
                    raise serializers.ValidationError(
                        f"Only {product.stock_quantity} items available in stock."
                    )
            except Product.DoesNotExist:
                pass  # Will be caught by product_id validation
        
        return attrs


class CartItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating cart items
    """
    product_id = serializers.IntegerField()
    
    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity']
    
    def validate_product_id(self, value):
        """Validate product exists and is available"""
        try:
            product = Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
        
        if not product.is_active:
            raise serializers.ValidationError("Product is not available.")
        
        if not product.is_in_stock:
            raise serializers.ValidationError("Product is out of stock.")
        
        return value
    
    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value
    
    def validate(self, attrs):
        """Validate stock availability"""
        product_id = attrs.get('product_id')
        quantity = attrs.get('quantity')
        
        try:
            product = Product.objects.get(id=product_id)
            if product.stock_quantity < quantity:
                raise serializers.ValidationError(
                    f"Only {product.stock_quantity} items available in stock."
                )
        except Product.DoesNotExist:
            pass  # Will be caught by product_id validation
        
        return attrs


class CartItemUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating cart items
    """
    class Meta:
        model = CartItem
        fields = ['quantity']
    
    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value
    
    def validate(self, attrs):
        """Validate stock availability for update"""
        quantity = attrs.get('quantity')
        
        if quantity and self.instance:
            product = self.instance.product
            if product.stock_quantity < quantity:
                raise serializers.ValidationError(
                    f"Only {product.stock_quantity} items available in stock."
                )
        
        return attrs


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for shopping cart
    Includes all cart items and calculated totals
    """
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    is_empty = serializers.ReadOnlyField()
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'items', 'total_items', 'total_price',
            'is_empty', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CartSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight cart serializer for summary views
    """
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'total_items', 'total_price', 'items_count', 'updated_at']
    
    def get_items_count(self, obj):
        """Get count of unique items (not total quantity)"""
        return obj.items.count()


class AddToCartSerializer(serializers.Serializer):
    """
    Serializer for adding products to cart
    """
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)
    
    def validate_product_id(self, value):
        """Validate product exists and is available"""
        try:
            product = Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
        
        if not product.is_active:
            raise serializers.ValidationError("Product is not available.")
        
        if not product.is_in_stock:
            raise serializers.ValidationError("Product is out of stock.")
        
        return value
    
    def validate(self, attrs):
        """Validate stock availability"""
        product_id = attrs.get('product_id')
        quantity = attrs.get('quantity')
        user = self.context['request'].user
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Check if item already exists in cart
            try:
                cart = Cart.objects.get(user=user)
                existing_item = cart.items.filter(product=product).first()
                
                if existing_item:
                    total_quantity = existing_item.quantity + quantity
                    if product.stock_quantity < total_quantity:
                        raise serializers.ValidationError(
                            f"Only {product.stock_quantity} items available in stock. "
                            f"You already have {existing_item.quantity} in your cart."
                        )
                else:
                    if product.stock_quantity < quantity:
                        raise serializers.ValidationError(
                            f"Only {product.stock_quantity} items available in stock."
                        )
            except Cart.DoesNotExist:
                # No cart exists, just check stock
                if product.stock_quantity < quantity:
                    raise serializers.ValidationError(
                        f"Only {product.stock_quantity} items available in stock."
                    )
        
        except Product.DoesNotExist:
            pass  # Will be caught by product_id validation
        
        return attrs


class UpdateCartItemSerializer(serializers.Serializer):
    """
    Serializer for updating cart item quantity
    """
    quantity = serializers.IntegerField(min_value=1)
    
    def validate(self, attrs):
        """Validate stock availability for update"""
        quantity = attrs.get('quantity')
        cart_item = self.context['cart_item']
        
        if cart_item.product.stock_quantity < quantity:
            raise serializers.ValidationError(
                f"Only {cart_item.product.stock_quantity} items available in stock."
            )
        
        return attrs


class CartCheckoutSerializer(serializers.Serializer):
    """
    Serializer for cart checkout validation
    """
    def validate(self, attrs):
        """Validate cart is ready for checkout"""
        user = self.context['request'].user
        
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart is empty.")
        
        if cart.is_empty:
            raise serializers.ValidationError("Cart is empty.")
        
        # Check stock availability for all items
        for item in cart.items.all():
            if not item.product.is_active:
                raise serializers.ValidationError(
                    f"Product '{item.product.name}' is no longer available."
                )
            
            if item.product.stock_quantity < item.quantity:
                raise serializers.ValidationError(
                    f"Only {item.product.stock_quantity} items of '{item.product.name}' "
                    f"available in stock, but you have {item.quantity} in your cart."
                )
        
        attrs['cart'] = cart
        return attrs
