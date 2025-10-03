"""
Views for Review model
Handles CRUD operations for WooCommerce product reviews
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..models.review import Review
from ..serializers.review_serializers import (
    ReviewListSerializer, ReviewDetailSerializer,
    ReviewCreateSerializer, ReviewUpdateSerializer,
    ProductReviewStatsSerializer
)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_reviews(request, woocommerce_product_id):
    """
    Get all reviews for a specific WooCommerce product
    
    Query params:
    - active_only: (default: true) Only show active/approved reviews
    """
    active_only = request.query_params.get('active_only', 'true').lower() == 'true'
    
    reviews = Review.get_product_reviews(woocommerce_product_id, active_only=active_only)
    serializer = ReviewListSerializer(reviews, many=True, context={'request': request})
    
    return Response({
        'success': True,
        'woocommerce_product_id': woocommerce_product_id,
        'total_reviews': reviews.count(),
        'reviews': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_review_stats(request, woocommerce_product_id):
    """
    Get review statistics for a specific WooCommerce product
    Returns: total reviews, average rating, and rating distribution
    """
    stats = Review.get_product_stats(woocommerce_product_id)
    serializer = ProductReviewStatsSerializer(stats)
    
    return Response({
        'success': True,
        'woocommerce_product_id': woocommerce_product_id,
        'stats': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_review_detail(request, review_id):
    """
    Get detailed information about a specific review
    """
    review = get_object_or_404(Review, id=review_id)
    serializer = ReviewDetailSerializer(review, context={'request': request})
    
    return Response({
        'success': True,
        'review': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_review(request):
    """
    Create a new review for a WooCommerce product
    
    Required fields:
    - woocommerce_product_id: ID of the WooCommerce product
    - rating: Rating from 1 to 5
    - comment: Review comment
    
    Optional fields:
    - title: Review title
    - anonymous_name: Name (required if not authenticated)
    - anonymous_email: Email (required if not authenticated)
    """
    serializer = ReviewCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        review = serializer.save()
        detail_serializer = ReviewDetailSerializer(review, context={'request': request})
        
        return Response({
            'success': True,
            'message': 'Reseña creada exitosamente',
            'review': detail_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_review(request, review_id):
    """
    Update an existing review
    Only the review owner can update their review
    """
    review = get_object_or_404(Review, id=review_id)
    
    # Check if user owns this review
    if review.user != request.user:
        return Response({
            'success': False,
            'error': 'No tienes permiso para editar esta reseña'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ReviewUpdateSerializer(review, data=request.data, partial=True, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        detail_serializer = ReviewDetailSerializer(review, context={'request': request})
        
        return Response({
            'success': True,
            'message': 'Reseña actualizada exitosamente',
            'review': detail_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, review_id):
    """
    Delete a review
    Only the review owner can delete their review
    """
    review = get_object_or_404(Review, id=review_id)
    
    # Check if user owns this review
    if review.user != request.user:
        return Response({
            'success': False,
            'error': 'No tienes permiso para eliminar esta reseña'
        }, status=status.HTTP_403_FORBIDDEN)
    
    woocommerce_product_id = review.woocommerce_product_id
    review.delete()
    
    return Response({
        'success': True,
        'message': 'Reseña eliminada exitosamente',
        'woocommerce_product_id': woocommerce_product_id
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_reviews(request):
    """
    Get all reviews made by the authenticated user
    """
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    serializer = ReviewListSerializer(reviews, many=True, context={'request': request})
    
    return Response({
        'success': True,
        'total_reviews': reviews.count(),
        'reviews': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_user_review(request, woocommerce_product_id):
    """
    Check if the authenticated user has already reviewed this product
    """
    review = Review.objects.filter(
        user=request.user,
        woocommerce_product_id=woocommerce_product_id
    ).first()
    
    if review:
        serializer = ReviewDetailSerializer(review, context={'request': request})
        return Response({
            'success': True,
            'has_reviewed': True,
            'review': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': True,
        'has_reviewed': False,
        'review': None
    }, status=status.HTTP_200_OK)



