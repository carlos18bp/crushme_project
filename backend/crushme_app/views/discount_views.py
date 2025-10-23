"""
Views for discount code functionality
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q

from ..models import DiscountCode
from ..serializers.discount_serializers import (
    DiscountCodeValidationSerializer,
    DiscountCodeResponseSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_discount_code(request):
    """
    Validate a discount code
    
    POST /api/discounts/validate/
    
    Request body:
    {
        "code": "SUMMER2024"
    }
    
    Response (code exists and is valid):
    {
        "exists": true,
        "code": "SUMMER2024",
        "discount_percentage": 20.00,
        "is_valid": true,
        "message": "Discount code is valid"
    }
    
    Response (code doesn't exist):
    {
        "exists": false,
        "message": "Discount code not found"
    }
    
    Response (code exists but is invalid):
    {
        "exists": true,
        "code": "EXPIRED10",
        "discount_percentage": 10.00,
        "is_valid": false,
        "message": "Discount code is not valid or has been used up"
    }
    """
    # Validate request data
    serializer = DiscountCodeValidationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {
                'exists': False,
                'message': 'Invalid request. Please provide a discount code.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    code = serializer.validated_data['code'].strip().upper()
    
    # Search for discount code (case-insensitive)
    try:
        discount_code = DiscountCode.objects.get(
            Q(code__iexact=code)
        )
        
        # Check if code is valid
        is_valid = discount_code.is_valid()
        
        # Serialize discount code
        discount_serializer = DiscountCodeResponseSerializer(discount_code)
        
        response_data = {
            'exists': True,
            **discount_serializer.data,
            'message': 'Discount code is valid' if is_valid else 'Discount code is not valid or has been used up'
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except DiscountCode.DoesNotExist:
        return Response(
            {
                'exists': False,
                'message': 'Discount code not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )
