"""
Feed views for CrushMe application
Handles READ operations for user feed posts (feeds are created automatically by actions)
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from ..models import Feed
from ..serializers.feed_serializers import FeedSerializer


class FeedPagination(PageNumberPagination):
    """Custom pagination for feed posts"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feed_list(request):
    """
    GET: List all feed posts from all users (paginated)
    Feeds are created automatically by system actions (signup, orders, gifts, etc.)
    
    Args:
        request: HTTP request object
        
    Returns:
        Response: List of feeds with text, action, style, and created_at
    """
    feeds = Feed.objects.select_related('user').all()
    
    # Optional: Filter by user_id query parameter
    user_id = request.query_params.get('user_id', None)
    if user_id:
        feeds = feeds.filter(user_id=user_id)
    
    # Optional: Filter by action type
    action = request.query_params.get('action', None)
    if action:
        feeds = feeds.filter(action=action)
    
    # Pagination
    paginator = FeedPagination()
    paginated_feeds = paginator.paginate_queryset(feeds, request)
    serializer = FeedSerializer(paginated_feeds, many=True)
    
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_feeds(request):
    """
    Get all feed posts from the authenticated user (paginated)
    
    Args:
        request: HTTP request object
        
    Returns:
        Response: List of user's feed posts
    """
    feeds = Feed.objects.filter(user=request.user).select_related('user')
    
    # Pagination
    paginator = FeedPagination()
    paginated_feeds = paginator.paginate_queryset(feeds, request)
    serializer = FeedSerializer(paginated_feeds, many=True)
    
    return paginator.get_paginated_response(serializer.data)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_feeds(request, user_id):
    """
    Get all feed posts from a specific user (paginated)
    
    Args:
        request: HTTP request object
        user_id: ID of the user
        
    Returns:
        Response: List of user's feed posts
    """
    feeds = Feed.objects.filter(user_id=user_id).select_related('user')
    
    # Pagination
    paginator = FeedPagination()
    paginated_feeds = paginator.paginate_queryset(feeds, request)
    serializer = FeedSerializer(paginated_feeds, many=True)
    
    return paginator.get_paginated_response(serializer.data)



