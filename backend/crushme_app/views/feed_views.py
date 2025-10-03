"""
Feed views for CrushMe application
Handles CRUD operations for user feed posts
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from ..models import Feed
from ..serializers.feed_serializers import (
    FeedSerializer, FeedCreateSerializer, FeedUpdateSerializer
)


class FeedPagination(PageNumberPagination):
    """Custom pagination for feed posts"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def feed_list_create(request):
    """
    GET: List all feed posts from all users (paginated)
    POST: Create a new feed post for the authenticated user
    
    Args:
        request: HTTP request object
        
    Returns:
        Response: List of feeds or newly created feed
    """
    if request.method == 'GET':
        feeds = Feed.objects.select_related('user').all()
        
        # Optional: Filter by user_id query parameter
        user_id = request.query_params.get('user_id', None)
        if user_id:
            feeds = feeds.filter(user_id=user_id)
        
        # Pagination
        paginator = FeedPagination()
        paginated_feeds = paginator.paginate_queryset(feeds, request)
        serializer = FeedSerializer(paginated_feeds, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
    elif request.method == 'POST':
        serializer = FeedCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            feed = serializer.save()
            # Return full feed data with user info
            response_serializer = FeedSerializer(feed)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def feed_detail(request, feed_id):
    """
    GET: Retrieve a specific feed post
    PUT/PATCH: Update a feed post (only owner)
    DELETE: Delete a feed post (only owner)
    
    Args:
        request: HTTP request object
        feed_id: ID of the feed post
        
    Returns:
        Response: Feed data or success/error message
    """
    feed = get_object_or_404(Feed, id=feed_id)
    
    if request.method == 'GET':
        serializer = FeedSerializer(feed)
        return Response(serializer.data)
    
    # Check if user owns this feed post
    if feed.user != request.user:
        return Response(
            {"detail": "No tienes permiso para realizar esta acción."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method in ['PUT', 'PATCH']:
        serializer = FeedUpdateSerializer(
            feed,
            data=request.data,
            partial=(request.method == 'PATCH')
        )
        
        if serializer.is_valid():
            serializer.save()
            # Return full feed data
            response_serializer = FeedSerializer(feed)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        feed.delete()
        return Response(
            {"detail": "Feed eliminado correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )


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



