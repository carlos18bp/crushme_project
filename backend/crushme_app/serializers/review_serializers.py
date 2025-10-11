"""
Serializers for Review model
Handles WooCommerce product reviews
"""
from rest_framework import serializers
from ..models.review import Review
from ..models.user import User
from ..services.translation_service import create_translator_from_request


class ReviewListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing reviews
    Shows reviewer information and review content
    """
    reviewer_name = serializers.ReadOnlyField()
    is_user_review = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'woocommerce_product_id', 'reviewer_name', 'rating',
            'title', 'comment', 'is_verified_purchase', 'is_user_review',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_user_review(self, obj):
        """Check if the review belongs to the current user"""
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return obj.user == request.user
        return False
    
    def to_representation(self, instance):
        """Translate user-generated review content"""
        representation = super().to_representation(instance)
        request = self.context.get('request')
        
        if request:
            translator = create_translator_from_request(request)
            # Traducir título y comentario de la reseña (auto-detectar idioma)
            if representation.get('title'):
                representation['title'] = translator.translate_user_content(representation['title'])
            if representation.get('comment'):
                representation['comment'] = translator.translate_user_content(representation['comment'])
        
        return representation


class ReviewDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for individual review
    """
    reviewer_name = serializers.ReadOnlyField()
    reviewer_email = serializers.ReadOnlyField()
    is_user_review = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'woocommerce_product_id', 'user', 'reviewer_name',
            'reviewer_email', 'rating', 'title', 'comment',
            'is_verified_purchase', 'is_active', 'is_user_review',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'reviewer_email', 'created_at', 'updated_at']
    
    def get_is_user_review(self, obj):
        """Check if the review belongs to the current user"""
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return obj.user == request.user
        return False
    
    def to_representation(self, instance):
        """Translate user-generated review content"""
        representation = super().to_representation(instance)
        request = self.context.get('request')
        
        if request:
            translator = create_translator_from_request(request)
            # Traducir título y comentario de la reseña (auto-detectar idioma)
            if representation.get('title'):
                representation['title'] = translator.translate_user_content(representation['title'])
            if representation.get('comment'):
                representation['comment'] = translator.translate_user_content(representation['comment'])
        
        return representation


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new review
    Handles both authenticated and anonymous users
    """
    
    class Meta:
        model = Review
        fields = [
            'woocommerce_product_id', 'rating', 'title', 'comment',
            'anonymous_name', 'anonymous_email'
        ]
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("La calificación debe estar entre 1 y 5 estrellas")
        return value
    
    def validate(self, attrs):
        """
        Validate review data
        - If user is authenticated, use user info
        - If anonymous, require name and email
        """
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        
        if not user:
            # Anonymous user - require name and email
            if not attrs.get('anonymous_name'):
                raise serializers.ValidationError({
                    'anonymous_name': 'El nombre es requerido para usuarios anónimos'
                })
            if not attrs.get('anonymous_email'):
                raise serializers.ValidationError({
                    'anonymous_email': 'El email es requerido para usuarios anónimos'
                })
        else:
            # Authenticated user - check if already reviewed this product
            woocommerce_product_id = attrs.get('woocommerce_product_id')
            existing_review = Review.objects.filter(
                user=user,
                woocommerce_product_id=woocommerce_product_id
            ).first()
            
            if existing_review:
                raise serializers.ValidationError(
                    'Ya has hecho una reseña de este producto. Puedes editarla o eliminarla.'
                )
        
        return attrs
    
    def create(self, validated_data):
        """
        Create review with user info if authenticated
        """
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        
        if user:
            validated_data['user'] = user
            # Clear anonymous fields for authenticated users
            validated_data.pop('anonymous_name', None)
            validated_data.pop('anonymous_email', None)
        
        return super().create(validated_data)


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing review
    Only the review owner can update
    """
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("La calificación debe estar entre 1 y 5 estrellas")
        return value


class ProductReviewStatsSerializer(serializers.Serializer):
    """
    Serializer for product review statistics
    """
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()
    rating_distribution = serializers.DictField()
    
    class Meta:
        fields = ['total_reviews', 'average_rating', 'rating_distribution']



