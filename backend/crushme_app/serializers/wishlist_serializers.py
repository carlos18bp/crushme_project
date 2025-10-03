"""
Wishlist serializers for CrushMe e-commerce application
Handles wishlist functionality with sharing and favorites
Now supports WooCommerce products
"""
from rest_framework import serializers
from ..models import WishList, WishListItem, FavoriteWishList, Product
from .product_serializers import ProductListSerializer
from .user_serializers import UserSerializer


class WishListItemSerializer(serializers.ModelSerializer):
    """
    Serializer for wishlist items (WooCommerce products)
    """
    # WooCommerce product fields
    woocommerce_product_id = serializers.IntegerField()
    product_name = serializers.SerializerMethodField()
    product_price = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    product_info = serializers.SerializerMethodField()
    is_available = serializers.ReadOnlyField()
    
    # Legacy support
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = WishListItem
        fields = [
            'id', 'woocommerce_product_id', 'product_name', 'product_price', 
            'product_image', 'product_info', 'notes', 'priority',
            'is_available', 'product', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_product_name(self, obj):
        """Get product name from cache"""
        return obj.get_product_name()
    
    def get_product_price(self, obj):
        """Get product price from cache"""
        return obj.get_product_price()
    
    def get_product_image(self, obj):
        """Get product image URL from cache"""
        return obj.get_product_image()
    
    def get_product_info(self, obj):
        """Get full cached product data"""
        return obj.product_data if obj.product_data else None


class WishListItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating wishlist items
    """
    product_id = serializers.IntegerField()
    
    class Meta:
        model = WishListItem
        fields = ['product_id', 'notes', 'priority']
    
    def validate_product_id(self, value):
        """Validate product exists and is active"""
        try:
            product = Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
        
        if not product.is_active:
            raise serializers.ValidationError("Product is not available.")
        
        return value


class WishListListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for wishlist lists
    """
    user = UserSerializer(read_only=True)
    total_items = serializers.ReadOnlyField()
    total_value = serializers.ReadOnlyField()
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = WishList
        fields = [
            'id', 'name', 'description', 'user', 'is_active', 'is_public',
            'total_items', 'total_value', 'is_favorited', 'created_at'
        ]
    
    def get_is_favorited(self, obj):
        """Check if current user has favorited this wishlist"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj.user:
            return FavoriteWishList.objects.filter(
                user=request.user,
                wishlist=obj
            ).exists()
        return False


class WishListDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for individual wishlist views
    """
    items = WishListItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    user_username = serializers.SerializerMethodField()
    total_items = serializers.ReadOnlyField()
    total_value = serializers.ReadOnlyField()
    public_url = serializers.ReadOnlyField()
    shareable_path = serializers.ReadOnlyField()
    is_favorited = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()
    shipping_name = serializers.ReadOnlyField()
    shipping_address = serializers.ReadOnlyField()
    shipping_phone = serializers.ReadOnlyField()
    shipping_email = serializers.ReadOnlyField()
    
    class Meta:
        model = WishList
        fields = [
            'id', 'name', 'description', 'user', 'user_username', 'is_active', 'is_public',
            'unique_link', 'public_url', 'shareable_path', 'items', 'total_items', 'total_value',
            'is_favorited', 'favorites_count', 'shipping_data',
            'shipping_name', 'shipping_address', 'shipping_phone', 'shipping_email',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'unique_link', 'created_at', 'updated_at']
    
    def get_user_username(self, obj):
        """Get username or fallback to email"""
        return obj.user.username or obj.user.email.split('@')[0]
    
    def get_is_favorited(self, obj):
        """Check if current user has favorited this wishlist"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj.user:
            return FavoriteWishList.objects.filter(
                user=request.user,
                wishlist=obj
            ).exists()
        return False
    
    def get_favorites_count(self, obj):
        """Get number of users who favorited this wishlist"""
        return FavoriteWishList.get_wishlist_favorites_count(obj)


class WishListCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating wishlists
    """
    class Meta:
        model = WishList
        fields = [
            'name', 'description', 'is_active', 'is_public', 'shipping_data'
        ]
    
    def validate_name(self, value):
        """Validate wishlist name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Wishlist name must be at least 2 characters long."
            )
        return value.strip()
    
    def validate_description(self, value):
        """Validate description if provided"""
        if value and len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Description must be at least 5 characters long if provided."
            )
        return value.strip() if value else value
    
    def validate_shipping_data(self, value):
        """Validate shipping data structure"""
        if value:
            allowed_keys = {'name', 'address', 'phone', 'email'}
            if not isinstance(value, dict):
                raise serializers.ValidationError(
                    "Shipping data must be a valid JSON object."
                )
            
            invalid_keys = set(value.keys()) - allowed_keys
            if invalid_keys:
                raise serializers.ValidationError(
                    f"Invalid shipping data keys: {', '.join(invalid_keys)}"
                )
        
        return value


class WishListPublicSerializer(serializers.ModelSerializer):
    """
    Serializer for public wishlist access (via UUID link)
    Limited information for privacy
    """
    items = WishListItemSerializer(many=True, read_only=True)
    user_name = serializers.SerializerMethodField()
    total_items = serializers.ReadOnlyField()
    total_value = serializers.ReadOnlyField()
    favorites_count = serializers.SerializerMethodField()
    shipping_name = serializers.ReadOnlyField()
    shipping_address = serializers.ReadOnlyField()
    shipping_phone = serializers.ReadOnlyField()
    shipping_email = serializers.ReadOnlyField()
    
    class Meta:
        model = WishList
        fields = [
            'id', 'name', 'description', 'user_name', 'items',
            'total_items', 'total_value', 'favorites_count',
            'shipping_name', 'shipping_address', 'shipping_phone', 'shipping_email',
            'created_at'
        ]
    
    def get_user_name(self, obj):
        """Get user's display name for public view"""
        return obj.user.get_full_name() or obj.user.email.split('@')[0]
    
    def get_favorites_count(self, obj):
        """Get number of users who favorited this wishlist"""
        return FavoriteWishList.get_wishlist_favorites_count(obj)


class WishListShippingSerializer(serializers.Serializer):
    """
    Serializer for updating wishlist shipping information
    """
    name = serializers.CharField(max_length=100, required=False)
    address = serializers.CharField(max_length=500, required=False)
    phone = serializers.CharField(max_length=20, required=False)
    email = serializers.EmailField(required=False)
    
    def validate_phone(self, value):
        """Validate phone number if provided"""
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Phone number must be at least 10 characters long."
            )
        return value.strip() if value else value
    
    def validate_address(self, value):
        """Validate address if provided"""
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Address must be at least 10 characters long."
            )
        return value.strip() if value else value


class FavoriteWishListSerializer(serializers.ModelSerializer):
    """
    Serializer for favorite wishlists
    """
    wishlist = WishListListSerializer(read_only=True)
    wishlist_id = serializers.IntegerField(write_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = FavoriteWishList
        fields = ['id', 'user', 'wishlist', 'wishlist_id', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_wishlist_id(self, value):
        """Validate wishlist exists and is public"""
        try:
            wishlist = WishList.objects.get(id=value)
        except WishList.DoesNotExist:
            raise serializers.ValidationError("Wishlist does not exist.")
        
        if not wishlist.is_public:
            raise serializers.ValidationError("Wishlist is not public.")
        
        if not wishlist.is_active:
            raise serializers.ValidationError("Wishlist is not active.")
        
        return value
    
    def validate(self, attrs):
        """Validate user is not favoriting their own wishlist"""
        wishlist_id = attrs.get('wishlist_id')
        user = self.context['request'].user
        
        try:
            wishlist = WishList.objects.get(id=wishlist_id)
            if wishlist.user == user:
                raise serializers.ValidationError(
                    "You cannot favorite your own wishlist."
                )
            
            # Check if already favorited
            if FavoriteWishList.objects.filter(user=user, wishlist=wishlist).exists():
                raise serializers.ValidationError(
                    "You have already favorited this wishlist."
                )
        
        except WishList.DoesNotExist:
            pass  # Will be caught by wishlist_id validation
        
        return attrs


class WishListSearchSerializer(serializers.Serializer):
    """
    Serializer for wishlist search parameters
    """
    user = serializers.CharField(
        required=False,
        help_text="Search by user email or name"
    )
    name = serializers.CharField(
        required=False,
        help_text="Search by wishlist name"
    )
    public_only = serializers.BooleanField(
        default=True,
        help_text="Show only public wishlists"
    )
    ordering = serializers.ChoiceField(
        choices=[
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('name', 'Name A-Z'),
            ('-name', 'Name Z-A'),
            ('-total_items', 'Most Items'),
            ('total_items', 'Least Items'),
        ],
        default='-created_at',
        help_text="Sort order for results"
    )


class AddWooCommerceProductToWishListSerializer(serializers.Serializer):
    """
    Serializer for adding WooCommerce products to wishlist
    """
    woocommerce_product_id = serializers.IntegerField()
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    priority = serializers.ChoiceField(
        choices=WishListItem.PRIORITY_CHOICES,
        default='medium',
        required=False
    )
    
    def validate_woocommerce_product_id(self, value):
        """Validate WooCommerce product ID is positive integer"""
        if value <= 0:
            raise serializers.ValidationError("Invalid WooCommerce product ID.")
        return value
    
    def validate(self, attrs):
        """Validate product is not already in wishlist"""
        wc_product_id = attrs.get('woocommerce_product_id')
        wishlist = self.context.get('wishlist')
        
        if wishlist and wishlist.items.filter(woocommerce_product_id=wc_product_id).exists():
            raise serializers.ValidationError({
                'woocommerce_product_id': "Product is already in this wishlist."
            })
        
        return attrs


class AddProductToWishListSerializer(serializers.Serializer):
    """
    Legacy serializer for adding local products to wishlist
    Kept for backwards compatibility
    """
    product_id = serializers.IntegerField()
    notes = serializers.CharField(max_length=500, required=False)
    priority = serializers.ChoiceField(
        choices=WishListItem.PRIORITY_CHOICES,
        default='medium'
    )
    
    def validate_product_id(self, value):
        """Validate product exists and is active"""
        try:
            product = Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
        
        if not product.is_active:
            raise serializers.ValidationError("Product is not available.")
        
        return value
    
    def validate(self, attrs):
        """Validate product is not already in wishlist"""
        product_id = attrs.get('product_id')
        wishlist = self.context['wishlist']
        
        if wishlist.items.filter(product_id=product_id).exists():
            raise serializers.ValidationError(
                "Product is already in this wishlist."
            )
        
        return attrs
