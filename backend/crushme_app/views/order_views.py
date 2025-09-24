"""
Order views for CrushMe e-commerce application
Handles order creation, tracking, history, and management
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from ..models import Order, Cart
from ..serializers.order_serializers import (
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer,
    OrderStatusUpdateSerializer, OrderTrackingSerializer, OrderSearchSerializer,
    OrderCancelSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    """
    Get user's order history
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderListSerializer(orders, many=True)
    
    return Response({
        'orders': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order(request, order_id):
    """
    Get detailed information about a specific order
    """
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrderDetailSerializer(order)
    
    return Response({
        'order': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """
    Create a new order from user's cart
    """
    serializer = OrderCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        try:
            order = serializer.save()
            detail_serializer = OrderDetailSerializer(order)
            
            return Response({
                'message': 'Order created successfully',
                'order': detail_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': 'Failed to create order',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    """
    Cancel an order (if eligible)
    """
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrderCancelSerializer(
        data=request.data,
        context={'order': order}
    )
    
    if serializer.is_valid():
        reason = serializer.validated_data.get('reason', '')
        
        try:
            if order.cancel_order():
                # Optionally save cancellation reason
                if reason:
                    order.notes = f"{order.notes}\n\nCancellation reason: {reason}".strip()
                    order.save()
                
                detail_serializer = OrderDetailSerializer(order)
                
                return Response({
                    'message': 'Order cancelled successfully',
                    'order': detail_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Order cannot be cancelled'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': 'Failed to cancel order',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def track_order(request, order_number):
    """
    Track order by order number
    """
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrderTrackingSerializer(order)
    
    return Response({
        'tracking': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_orders(request):
    """
    Get user's recent orders (last 5)
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    serializer = OrderListSerializer(orders, many=True)
    
    return Response({
        'recent_orders': serializer.data
    }, status=status.HTTP_200_OK)


# ===========================
# ADMIN VIEWS
# ===========================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_orders(request):
    """
    Get all orders (Admin only)
    """
    # Parse search parameters
    search_serializer = OrderSearchSerializer(data=request.query_params)
    
    if not search_serializer.is_valid():
        return Response({
            'error': 'Invalid search parameters',
            'details': search_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Start with all orders
    queryset = Order.objects.all()
    
    # Apply filters
    search_data = search_serializer.validated_data
    
    if search_data.get('status'):
        queryset = queryset.filter(status=search_data['status'])
    
    if search_data.get('date_from'):
        queryset = queryset.filter(created_at__date__gte=search_data['date_from'])
    
    if search_data.get('date_to'):
        queryset = queryset.filter(created_at__date__lte=search_data['date_to'])
    
    if search_data.get('min_total'):
        queryset = queryset.filter(total__gte=search_data['min_total'])
    
    if search_data.get('max_total'):
        queryset = queryset.filter(total__lte=search_data['max_total'])
    
    # Search by user email or order number
    search_query = request.query_params.get('search', '').strip()
    if search_query:
        queryset = queryset.filter(
            Q(user__email__icontains=search_query) |
            Q(order_number__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )
    
    # Apply ordering
    ordering = search_data.get('ordering', '-created_at')
    queryset = queryset.order_by(ordering)
    
    # Pagination
    page_number = request.query_params.get('page', 1)
    page_size = min(int(request.query_params.get('page_size', 50)), 100)
    
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page_number)
    
    # Serialize orders
    serializer = OrderDetailSerializer(page_obj.object_list, many=True)
    
    return Response({
        'orders': serializer.data,
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'page_size': page_size
        }
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_order_status(request, order_id):
    """
    Update order status (Admin only)
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
    
    if serializer.is_valid():
        order = serializer.save()
        detail_serializer = OrderDetailSerializer(order)
        
        return Response({
            'message': f'Order status updated to {order.get_status_display()}',
            'order': detail_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_order_statistics(request):
    """
    Get order statistics (Admin only)
    """
    from django.db.models import Count, Sum
    from django.utils import timezone
    from datetime import timedelta
    
    # Calculate statistics
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(
        status__in=['delivered', 'shipped']
    ).aggregate(Sum('total'))['total__sum'] or 0
    
    # Orders by status
    orders_by_status = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Recent orders (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_orders = Order.objects.filter(created_at__gte=thirty_days_ago).count()
    recent_revenue = Order.objects.filter(
        created_at__gte=thirty_days_ago,
        status__in=['delivered', 'shipped']
    ).aggregate(Sum('total'))['total__sum'] or 0
    
    # Pending orders requiring attention
    pending_orders = Order.objects.filter(status='pending').count()
    processing_orders = Order.objects.filter(status='processing').count()
    
    return Response({
        'statistics': {
            'total_orders': total_orders,
            'total_revenue': str(total_revenue),
            'orders_by_status': list(orders_by_status),
            'recent_30_days': {
                'orders': recent_orders,
                'revenue': str(recent_revenue)
            },
            'requires_attention': {
                'pending_orders': pending_orders,
                'processing_orders': processing_orders
            }
        }
    }, status=status.HTTP_200_OK)
