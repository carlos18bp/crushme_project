"""
Serializers for Contact model
Handles contact form submissions
"""
from rest_framework import serializers
from ..models.contact import Contact


class ContactCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new contact message
    """
    
    class Meta:
        model = Contact
        fields = [
            'email', 'nombre', 'numero', 'asunto', 'texto'
        ]
    
    def validate_email(self, value):
        """Validate email format"""
        if not value:
            raise serializers.ValidationError("El email es requerido")
        return value.lower()
    
    def validate_nombre(self, value):
        """Validate nombre is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre es requerido")
        return value.strip()
    
    def validate_asunto(self, value):
        """Validate asunto is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("El asunto es requerido")
        return value.strip()
    
    def validate_texto(self, value):
        """Validate texto is not empty and has minimum length"""
        if not value or not value.strip():
            raise serializers.ValidationError("El mensaje es requerido")
        if len(value.strip()) < 10:
            raise serializers.ValidationError("El mensaje debe tener al menos 10 caracteres")
        return value.strip()


class ContactListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing contact messages
    """
    
    class Meta:
        model = Contact
        fields = [
            'id', 'email', 'nombre', 'numero', 'asunto', 'texto',
            'is_read', 'is_responded', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContactDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for individual contact message
    Includes admin notes
    """
    
    class Meta:
        model = Contact
        fields = [
            'id', 'email', 'nombre', 'numero', 'asunto', 'texto',
            'is_read', 'is_responded', 'admin_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


