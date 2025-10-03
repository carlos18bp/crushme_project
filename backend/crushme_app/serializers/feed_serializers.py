"""
Feed serializers for CrushMe application
Handles serialization of user feed posts
"""
from rest_framework import serializers
from ..models import Feed, User


class FeedSerializer(serializers.ModelSerializer):
    """
    Serializer for Feed model.
    Includes user information and validation for feed posts.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Feed
        fields = [
            'id', 'user', 'user_email', 'user_username', 'user_full_name',
            'text', 'color', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate_text(self, value):
        """Validate that text is not empty and within length limits"""
        if not value or not value.strip():
            raise serializers.ValidationError("El texto no puede estar vacío.")
        if len(value) > 1000:
            raise serializers.ValidationError("El texto no puede exceder 1000 caracteres.")
        return value.strip()
    
    def validate_color(self, value):
        """Validate color format"""
        if not value:
            return "#000000"  # Default color
        
        # Ensure it starts with #
        if not value.startswith('#'):
            value = '#' + value
        
        # Validate hex format
        if len(value) != 7:
            raise serializers.ValidationError("El color debe tener el formato #RRGGBB")
        
        try:
            int(value[1:], 16)  # Try to convert hex to int
        except ValueError:
            raise serializers.ValidationError("Código de color hexadecimal inválido")
        
        return value.upper()


class FeedCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new feed posts.
    Automatically assigns the authenticated user.
    """
    class Meta:
        model = Feed
        fields = ['text', 'color']
    
    def validate_text(self, value):
        """Validate that text is not empty and within length limits"""
        if not value or not value.strip():
            raise serializers.ValidationError("El texto no puede estar vacío.")
        if len(value) > 1000:
            raise serializers.ValidationError("El texto no puede exceder 1000 caracteres.")
        return value.strip()
    
    def validate_color(self, value):
        """Validate and normalize color format"""
        if not value:
            return "#000000"
        
        if not value.startswith('#'):
            value = '#' + value
        
        if len(value) != 7:
            raise serializers.ValidationError("El color debe tener el formato #RRGGBB")
        
        try:
            int(value[1:], 16)
        except ValueError:
            raise serializers.ValidationError("Código de color hexadecimal inválido")
        
        return value.upper()
    
    def create(self, validated_data):
        """Create feed post with authenticated user"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class FeedUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing feed posts.
    Users can only update their own posts.
    """
    class Meta:
        model = Feed
        fields = ['text', 'color']
    
    def validate_text(self, value):
        """Validate text"""
        if not value or not value.strip():
            raise serializers.ValidationError("El texto no puede estar vacío.")
        if len(value) > 1000:
            raise serializers.ValidationError("El texto no puede exceder 1000 caracteres.")
        return value.strip()
    
    def validate_color(self, value):
        """Validate color"""
        if not value:
            return "#000000"
        
        if not value.startswith('#'):
            value = '#' + value
        
        if len(value) != 7:
            raise serializers.ValidationError("El color debe tener el formato #RRGGBB")
        
        try:
            int(value[1:], 16)
        except ValueError:
            raise serializers.ValidationError("Código de color hexadecimal inválido")
        
        return value.upper()



