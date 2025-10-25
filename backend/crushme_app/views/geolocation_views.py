"""
Geolocation views for IP-based country detection.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from ..utils.geolocation import GeoLocationService


def get_client_ip(request):
    """
    Get client IP address from request, considering proxies.
    
    Args:
        request: Django request object
        
    Returns:
        str: Client IP address
    """
    # Check for X-Forwarded-For header (proxy/load balancer)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Get first IP in the chain (client IP)
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        # Direct connection
        ip = request.META.get('REMOTE_ADDR')
    
    return ip


@api_view(['POST'])
@permission_classes([AllowAny])
def detect_country_by_ip(request):
    """
    Detect country from IP address.
    
    Public endpoint - no authentication required.
    
    Request body:
        {
            "ip": "181.xxx.xxx.xxx"  // Optional, if not provided uses client IP
        }
    
    Response:
        {
            "ip": "181.xxx.xxx.xxx",
            "country_code": "CO",
            "is_colombia": true,
            "recommended_currency": "COP"
        }
    """
    # Get IP from request body or use client IP
    ip_address = request.data.get('ip')
    
    if not ip_address:
        # Use client IP from request
        ip_address = get_client_ip(request)
    
    if not ip_address:
        return Response(
            {
                'error': 'Could not determine IP address'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get country code
        country_code = GeoLocationService.get_country_code(ip_address)
        
        if country_code is None:
            return Response(
                {
                    'ip': ip_address,
                    'country_code': None,
                    'is_colombia': False,
                    'recommended_currency': 'USD',
                    'message': 'IP address not found in database'
                },
                status=status.HTTP_200_OK
            )
        
        # Check if Colombia
        is_colombia = country_code == 'CO'
        
        # Get recommended currency
        recommended_currency = 'COP' if is_colombia else 'USD'
        
        return Response(
            {
                'ip': ip_address,
                'country_code': country_code,
                'is_colombia': is_colombia,
                'recommended_currency': recommended_currency
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        return Response(
            {
                'error': f'Error detecting country: {str(e)}',
                'ip': ip_address
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def detect_my_country(request):
    """
    Detect country from client's IP address (auto-detect).
    
    Public endpoint - no authentication required.
    
    Response:
        {
            "ip": "181.xxx.xxx.xxx",
            "country_code": "CO",
            "is_colombia": true,
            "recommended_currency": "COP"
        }
    """
    # Get client IP
    ip_address = get_client_ip(request)
    
    if not ip_address:
        return Response(
            {
                'error': 'Could not determine your IP address'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get country code
        country_code = GeoLocationService.get_country_code(ip_address)
        
        if country_code is None:
            return Response(
                {
                    'ip': ip_address,
                    'country_code': None,
                    'is_colombia': False,
                    'recommended_currency': 'USD',
                    'message': 'Your IP address not found in database'
                },
                status=status.HTTP_200_OK
            )
        
        # Check if Colombia
        is_colombia = country_code == 'CO'
        
        # Get recommended currency
        recommended_currency = 'COP' if is_colombia else 'USD'
        
        return Response(
            {
                'ip': ip_address,
                'country_code': country_code,
                'is_colombia': is_colombia,
                'recommended_currency': recommended_currency
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        return Response(
            {
                'error': f'Error detecting your country: {str(e)}',
                'ip': ip_address
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
