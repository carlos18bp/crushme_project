"""
Serializers for discount code functionality
"""
from rest_framework import serializers
from ..models import DiscountCode


class DiscountCodeValidationSerializer(serializers.Serializer):
    """
    Serializer for validating discount codes
    """
    code = serializers.CharField(
        max_length=50,
        required=True,
        help_text="Discount code to validate"
    )


class DiscountCodeResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for discount code response
    """
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = DiscountCode
        fields = ['code', 'discount_percentage', 'is_valid']
    
    def get_is_valid(self, obj):
        """Check if the discount code is valid"""
        return obj.is_valid()
