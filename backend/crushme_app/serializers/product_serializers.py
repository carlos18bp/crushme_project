"""
Product serializers for CrushMe e-commerce application
Handles product data serialization with gallery support
"""
from rest_framework import serializers
from django_attachments.models import Attachment
from ..models import Product


class AttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for product gallery attachments
    """
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Attachment
        fields = [
            'id', 'original_name', 'file_url', 'thumbnail_url',
            'filesize', 'mimetype', 'image_width', 'image_height',
            'title', 'caption', 'rank', 'is_image'
        ]
        read_only_fields = ['id', 'filesize', 'mimetype', 'image_width', 'image_height', 'is_image']
    
    def get_file_url(self, obj):
        """Get full URL for the file"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_thumbnail_url(self, obj):
        """Get thumbnail URL for images"""
        if obj.is_image and obj.file:
            try:
                # Using easy_thumbnails to generate thumbnail
                from easy_thumbnails.files import get_thumbnailer
                thumbnail = get_thumbnailer(obj.file)['small']
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(thumbnail.url)
                return thumbnail.url
            except:
                return self.get_file_url(obj)
        return None


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for product lists
    Includes only essential information for performance
    """
    primary_image = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display_name', read_only=True)
    is_in_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'category', 'category_display',
            'primary_image', 'is_in_stock', 'stock_quantity', 'created_at'
        ]
    
    def get_primary_image(self, obj):
        """Get primary image URL"""
        primary_image = obj.primary_image
        if primary_image and primary_image.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.file.url)
            return primary_image.file.url
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for individual product views
    Includes gallery and full product information
    """
    gallery_images = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display_name', read_only=True)
    is_in_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'category', 'category_display',
            'stock_quantity', 'is_active', 'is_in_stock',
            'primary_image', 'gallery_images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_primary_image(self, obj):
        """Get primary image with full details"""
        primary_image = obj.primary_image
        if primary_image:
            return AttachmentSerializer(primary_image, context=self.context).data
        return None
    
    def get_gallery_images(self, obj):
        """Get all gallery images"""
        gallery_images = obj.gallery_images
        return AttachmentSerializer(gallery_images, many=True, context=self.context).data


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating products
    Handles validation and business logic
    """
    category_display = serializers.CharField(source='get_category_display_name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'category', 'category_display',
            'stock_quantity', 'is_active'
        ]
        read_only_fields = ['id']
    
    def validate_price(self, value):
        """Validate price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value
    
    def validate_stock_quantity(self, value):
        """Validate stock quantity is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return value
    
    def validate_name(self, value):
        """Validate product name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Product name must be at least 2 characters long.")
        return value.strip()
    
    def validate_description(self, value):
        """Validate product description"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Product description must be at least 10 characters long.")
        return value.strip()


class ProductSearchSerializer(serializers.Serializer):
    """
    Serializer for product search parameters
    """
    q = serializers.CharField(
        required=False,
        help_text="Search query for product name or description"
    )
    category = serializers.ChoiceField(
        choices=Product.CATEGORY_CHOICES,
        required=False,
        help_text="Filter by product category"
    )
    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Minimum price filter"
    )
    max_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Maximum price filter"
    )
    in_stock_only = serializers.BooleanField(
        default=False,
        help_text="Show only products in stock"
    )
    ordering = serializers.ChoiceField(
        choices=[
            ('name', 'Name A-Z'),
            ('-name', 'Name Z-A'),
            ('price', 'Price Low-High'),
            ('-price', 'Price High-Low'),
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
        ],
        default='-created_at',
        help_text="Sort order for results"
    )
    
    def validate(self, attrs):
        """Validate search parameters"""
        min_price = attrs.get('min_price')
        max_price = attrs.get('max_price')
        
        if min_price and min_price < 0:
            raise serializers.ValidationError("Minimum price cannot be negative.")
        
        if max_price and max_price < 0:
            raise serializers.ValidationError("Maximum price cannot be negative.")
        
        if min_price and max_price and min_price > max_price:
            raise serializers.ValidationError("Minimum price cannot be greater than maximum price.")
        
        return attrs


class ProductCategorySerializer(serializers.Serializer):
    """
    Serializer for product categories
    """
    value = serializers.CharField()
    label = serializers.CharField()
    count = serializers.IntegerField(read_only=True)
    
    @classmethod
    def get_categories_with_counts(cls):
        """Get all categories with product counts"""
        from django.db.models import Count
        
        categories = []
        for value, label in Product.CATEGORY_CHOICES:
            count = Product.objects.filter(category=value, is_active=True).count()
            categories.append({
                'value': value,
                'label': label,
                'count': count
            })
        
        return categories


class ProductStockUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating product stock
    """
    stock_quantity = serializers.IntegerField(min_value=0)
    
    def validate_stock_quantity(self, value):
        """Validate stock quantity"""
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return value
