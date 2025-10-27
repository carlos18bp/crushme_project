"""
Wishlist views for WooCommerce products integration
Handles adding/removing WooCommerce products to wishlists
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from ..models import WishList, WishListItem
from ..serializers.wishlist_serializers import (
    AddWooCommerceProductToWishListSerializer,
    WishListDetailSerializer
)
from ..services.woocommerce_service import woocommerce_service


def enrich_wishlist_with_woocommerce_data(wishlist):
    """
    Enriquece los items de la wishlist con datos frescos de WooCommerce
    Combina datos del caché con información actualizada
    """
    items = wishlist.items.all()
    
    if not items:
        return wishlist
    
    # Extraer IDs de productos WooCommerce
    wc_product_ids = []
    for item in items:
        if item.woocommerce_product_id:
            wc_product_ids.append(item.woocommerce_product_id)
    
    if not wc_product_ids:
        return wishlist
    
    # Consultar productos en batch desde WooCommerce
    wc_products_map = {}
    for product_id in wc_product_ids:
        result = woocommerce_service.get_product_by_id(product_id)
        if result['success']:
            wc_products_map[product_id] = result['data']
    
    # Actualizar caché de cada item con datos frescos
    for item in items:
        if item.woocommerce_product_id and item.woocommerce_product_id in wc_products_map:
            fresh_data = wc_products_map[item.woocommerce_product_id]
            item.update_product_data(fresh_data)
    
    return wishlist


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_woocommerce_product_to_wishlist(request, wishlist_id):
    """
    Add a WooCommerce product to a wishlist
    
    POST Body:
    {
        "woocommerce_product_id": 123,
        "notes": "Optional notes",
        "priority": "high"  # low, medium, high
    }
    """
    try:
        wishlist = WishList.objects.get(id=wishlist_id, user=request.user)
    except WishList.DoesNotExist:
        return Response({
            'error': 'Wishlist not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = AddWooCommerceProductToWishListSerializer(
        data=request.data,
        context={'wishlist': wishlist}
    )
    
    if serializer.is_valid():
        wc_product_id = serializer.validated_data['woocommerce_product_id']
        notes = serializer.validated_data.get('notes', '')
        priority = serializer.validated_data.get('priority', 'medium')
        
        # Fetch product data from WooCommerce
        wc_response = woocommerce_service.get_product_by_id(wc_product_id)
        
        if not wc_response['success']:
            return Response({
                'error': 'Could not fetch product from WooCommerce',
                'details': wc_response.get('error')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        product_data = wc_response['data']
        
        # Add product to wishlist with cached data
        wishlist_item, created = wishlist.add_woocommerce_product(
            woocommerce_product_id=wc_product_id,
            product_data={
                'name': product_data.get('name'),
                'price': product_data.get('price'),
                'regular_price': product_data.get('regular_price'),
                'sale_price': product_data.get('sale_price'),
                'images': product_data.get('images', [])[:1],
                'stock_status': product_data.get('stock_status'),
                'stock_quantity': product_data.get('stock_quantity'),
            },
            notes=notes,
            priority=priority
        )
        
        if created:
            # Get currency from request (set by CurrencyMiddleware)
            currency = getattr(request, 'currency', 'COP')
            
            detail_serializer = WishListDetailSerializer(wishlist, context={'request': request})
            wishlist_data = detail_serializer.data
            
            # Convert prices to target currency
            from ..utils.price_helpers import convert_price_fields
            wishlist_data = convert_price_fields(wishlist_data, currency)
            
            return Response({
                'message': f'Added {product_data.get("name")} to {wishlist.name}',
                'wishlist': wishlist_data,
                'currency': currency.upper()
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Product is already in this wishlist'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_woocommerce_product_from_wishlist(request, wishlist_id, woocommerce_product_id):
    """
    Remove a WooCommerce product from a wishlist
    """
    try:
        wishlist = WishList.objects.get(id=wishlist_id, user=request.user)
    except WishList.DoesNotExist:
        return Response({
            'error': 'Wishlist not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Find the item
    try:
        item = wishlist.items.get(woocommerce_product_id=woocommerce_product_id)
        product_name = item.get_product_name()
        item.delete()
        
        # Get currency from request (set by CurrencyMiddleware)
        currency = getattr(request, 'currency', 'COP')
        
        detail_serializer = WishListDetailSerializer(wishlist, context={'request': request})
        wishlist_data = detail_serializer.data
        
        # Convert prices to target currency
        from ..utils.price_helpers import convert_price_fields
        wishlist_data = convert_price_fields(wishlist_data, currency)
        
        return Response({
            'message': f'Removed {product_name} from {wishlist.name}',
            'wishlist': wishlist_data,
            'currency': currency.upper()
        }, status=status.HTTP_200_OK)
    except WishListItem.DoesNotExist:
        return Response({
            'error': 'Product is not in this wishlist'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_wishlist_products(request, wishlist_id):
    """
    Refresh product data from WooCommerce for all items in a wishlist
    Useful to update prices and stock status
    """
    try:
        wishlist = WishList.objects.get(id=wishlist_id, user=request.user)
    except WishList.DoesNotExist:
        return Response({
            'error': 'Wishlist not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    updated_count = 0
    failed_count = 0
    
    for item in wishlist.items.all():
        if item.woocommerce_product_id:
            # Fetch fresh data from WooCommerce
            wc_response = woocommerce_service.get_product_by_id(item.woocommerce_product_id)
            
            if wc_response['success']:
                product_data = wc_response['data']
                item.update_product_data(product_data)
                updated_count += 1
            else:
                failed_count += 1
    
    # Get currency from request (set by CurrencyMiddleware)
    currency = getattr(request, 'currency', 'COP')
    
    detail_serializer = WishListDetailSerializer(wishlist, context={'request': request})
    wishlist_data = detail_serializer.data
    
    # Convert prices to target currency
    from ..utils.price_helpers import convert_price_fields
    wishlist_data = convert_price_fields(wishlist_data, currency)
    
    return Response({
        'message': f'Refreshed {updated_count} products ({failed_count} failed)',
        'updated_count': updated_count,
        'failed_count': failed_count,
        'wishlist': wishlist_data,
        'currency': currency.upper()
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_wishlists_by_username(request, username):
    """
    Get all public wishlists from a user by username
    Returns all public and active wishlists from the specified user
    """
    try:
        # Find user by username
        from ..models import User
        
        # Try to find user by username first, then by email prefix
        user = None
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            # Try finding by email prefix
            users = User.objects.filter(email__istartswith=username)
            if users.count() == 1:
                user = users.first()
            elif users.count() > 1:
                # If multiple users, try exact match on email prefix
                for u in users:
                    if u.email.split('@')[0].lower() == username.lower():
                        user = u
                        break
        
        if not user:
            return Response({
                'error': 'Usuario no encontrado',
                'username': username
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get all public wishlists from this user
        wishlists = WishList.objects.filter(
            user=user,
            is_public=True,
            is_active=True
        ).order_by('-created_at')
        
        if not wishlists.exists():
            return Response({
                'success': True,
                'message': f'El usuario @{username} no tiene wishlists públicas',
                'username': username,
                'user_id': user.id,
                'wishlists': []
            }, status=status.HTTP_200_OK)
        
        # Serializar wishlists (sin cargar productos para listado rápido)
        from ..serializers.wishlist_serializers import WishListListSerializer
        serializer = WishListListSerializer(wishlists, many=True, context={'request': request})
        
        return Response({
            'success': True,
            'message': f'Wishlists de @{username}',
            'username': username,
            'user_id': user.id,
            'user_full_name': user.get_full_name(),
            'total_wishlists': wishlists.count(),
            'wishlists': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_public_wishlist_by_username(request, username, wishlist_id):
    """
    Get public wishlist by username and ID
    Format: /@username/{id}
    
    Query Parameters:
    - refresh: 'true' to fetch fresh data from WooCommerce (slower)
    
    By default uses cached product data for fast response
    """
    try:
        # Find wishlist by ID and check if it belongs to the user with that username
        wishlist = WishList.objects.get(
            id=wishlist_id,
            is_public=True,
            is_active=True
        )
        
        # Verify username matches
        wishlist_username = wishlist.user.username or wishlist.user.email.split('@')[0]
        if wishlist_username.lower() != username.lower():
            return Response({
                'error': 'Wishlist not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get currency from request (set by CurrencyMiddleware)
        currency = getattr(request, 'currency', 'COP')
        
        # Only enrich with fresh WooCommerce data if explicitly requested
        refresh = request.GET.get('refresh', 'false').lower() == 'true'
        if refresh:
            wishlist = enrich_wishlist_with_woocommerce_data(wishlist)
        
        detail_serializer = WishListDetailSerializer(wishlist, context={'request': request})
        wishlist_data = detail_serializer.data
        
        # Convert prices in wishlist data (now also converts prices in items)
        from ..utils.price_helpers import convert_price_fields
        wishlist_data = convert_price_fields(wishlist_data, currency)
        
        return Response({
            'wishlist': wishlist_data,
            'currency': currency.upper()
        }, status=status.HTTP_200_OK)
        
    except WishList.DoesNotExist:
        return Response({
            'error': 'Wishlist not found or is not public'
        }, status=status.HTTP_404_NOT_FOUND)

