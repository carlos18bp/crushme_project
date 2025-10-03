"""
Serializers for Favorite Products functionality
"""
from rest_framework import serializers
from ..models.favorite_product import FavoriteProduct
from ..models.user import User


class FavoriteProductSerializer(serializers.ModelSerializer):
    """
    Serializer for FavoriteProduct model
    Includes cached product data from WooCommerce
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = FavoriteProduct
        fields = [
            'id',
            'user_email',
            'user_username',
            'woocommerce_product_id',
            'product_data',
            'cache_updated_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'user_email',
            'user_username',
            'product_data',
            'cache_updated_at',
            'created_at',
            'updated_at'
        ]


class AddFavoriteProductSerializer(serializers.Serializer):
    """
    Serializer for adding a product to favorites
    Only requires the WooCommerce product ID
    """
    woocommerce_product_id = serializers.IntegerField(
        min_value=1,
        help_text="ID del producto en WooCommerce"
    )
    
    def validate_woocommerce_product_id(self, value):
        """Validate product ID is a positive integer"""
        if value <= 0:
            raise serializers.ValidationError("Product ID must be a positive integer.")
        return value


class RemoveFavoriteProductSerializer(serializers.Serializer):
    """
    Serializer for removing a product from favorites
    """
    woocommerce_product_id = serializers.IntegerField(
        min_value=1,
        help_text="ID del producto en WooCommerce"
    )


class FavoriteProductListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing favorite products
    Focuses on essential product information
    """
    product_name = serializers.SerializerMethodField()
    product_price = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    product_slug = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = FavoriteProduct
        fields = [
            'id',
            'woocommerce_product_id',
            'product_name',
            'product_price',
            'product_image',
            'product_slug',
            'is_in_stock',
            'created_at'
        ]
    
    def get_product_name(self, obj):
        """Extract product name from cached data"""
        return obj.product_data.get('name', 'Unknown Product')
    
    def get_product_price(self, obj):
        """Extract product price from cached data"""
        return obj.product_data.get('price', '0')
    
    def get_product_image(self, obj):
        """Extract product image URL from cached data"""
        images = obj.product_data.get('images', [])
        if images and len(images) > 0:
            return images[0].get('src', '')
        return ''
    
    def get_product_slug(self, obj):
        """Extract product slug from cached data"""
        return obj.product_data.get('slug', '')
    
    def get_is_in_stock(self, obj):
        """Check if product is in stock from cached data"""
        stock_status = obj.product_data.get('stock_status', 'outofstock')
        return stock_status == 'instock'


class BulkFavoriteProductSerializer(serializers.Serializer):
    """
    Serializer for bulk operations on favorite products
    """
    woocommerce_product_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        help_text="Lista de IDs de productos de WooCommerce",
        allow_empty=False
    )
    
    def validate_woocommerce_product_ids(self, value):
        """Validate product IDs list"""
        if len(value) > 100:
            raise serializers.ValidationError("Maximum 100 products allowed per request.")
        
        # Remove duplicates
        unique_ids = list(set(value))
        if len(unique_ids) != len(value):
            raise serializers.ValidationError("Duplicate product IDs found in the list.")
        
        return unique_ids


