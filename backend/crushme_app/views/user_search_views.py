"""
User search views for gift sending
Provides user search with crush status and shipping cost
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db.models import Q
import logging

from ..models import UserAddress
from ..utils import calculate_shipping_cost

User = get_user_model()
logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_users_for_gift(request):
    """
    Search users by username for gift sending
    Returns username, crush status, shipping cost, and profile picture
    
    Query Parameters:
        - q: Search query (username)
        - limit: Maximum number of results (default: 10)
    
    Returns:
        List of users with:
        - username: Username of the user
        - is_crush: Whether user has crush relationship with searcher
        - shipping_cost: Cost of shipping to user's city (can be null)
        - profile_picture: URL of user's profile picture (can be null)
    """
    try:
        # Get search query
        search_query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 10))
        
        if not search_query:
            return Response({
                'error': 'Search query is required (parameter: q)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Remove @ symbol if present (common in username searches)
        original_query = search_query
        search_query = search_query.lstrip('@')
        
        if original_query != search_query:
            logger.info(f"🔍 Removed @ from search query: '{original_query}' -> '{search_query}'")
        
        if len(search_query) < 2:
            return Response({
                'error': 'Search query must be at least 2 characters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Search users by username (case-insensitive, partial match)
        users = User.objects.filter(
            username__icontains=search_query
        ).exclude(
            is_active=False
        )[:limit]
        
        logger.info(f"🔍 User search for '{search_query}': found {users.count()} results")
        
        # Build response with minimal user info
        results = []
        for user in users:
            # Get user's shipping cost
            try:
                user_address = UserAddress.objects.get(user=user)
                has_shipping_info = all([
                    user_address.address_line_1,
                    user_address.city,
                    user_address.state,
                    user_address.zip_code
                ])
                city = user_address.city
                shipping_cost = calculate_shipping_cost(city) if has_shipping_info else None
            except UserAddress.DoesNotExist:
                shipping_cost = None
            
            # Get crush status from user model
            is_crush = user.is_crush if hasattr(user, 'is_crush') else False
            
            # Get profile picture URL (absolute URL)
            profile_picture = None
            if hasattr(user, 'profile_picture') and user.profile_picture:
                profile_picture = request.build_absolute_uri(user.profile_picture.url)
            
            user_data = {
                'username': user.username,
                'is_crush': is_crush,
                'shipping_cost': shipping_cost,
                'profile_picture': profile_picture
            }
            
            results.append(user_data)
        
        return Response({
            'success': True,
            'count': len(results),
            'results': results
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"❌ Error searching users: {str(e)}")
        return Response({
            'error': 'Internal server error',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
