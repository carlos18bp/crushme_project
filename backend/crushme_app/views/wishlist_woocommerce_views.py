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
        
        # ✅ Verificar que el producto existe en la DB local sincronizada
        from ..models.woocommerce_models import WooCommerceProduct
        try:
            wc_product = WooCommerceProduct.objects.get(wc_id=wc_product_id)
        except WooCommerceProduct.DoesNotExist:
            return Response({
                'error': f'Product {wc_product_id} not found in local database. Please sync products first.',
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Add product to wishlist (NO guardar cache JSON - usar DB local)
        wishlist_item, created = wishlist.add_woocommerce_product(
            woocommerce_product_id=wc_product_id,
            product_data=None,  # No guardar cache - usar DB local
            notes=notes,
            priority=priority
        )
        
        if created:
            # Get currency from request (set by CurrencyMiddleware)
            currency = getattr(request, 'currency', 'COP')
            
            detail_serializer = WishListDetailSerializer(wishlist, context={'request': request})
            
            # ✅ NO aplicar convert_price_fields - el serializer ya convierte los precios
            
            return Response({
                'message': f'Added {wc_product.name} to {wishlist.name}',
                'wishlist': detail_serializer.data,
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
        
        # ✅ NO aplicar convert_price_fields - el serializer ya convierte los precios
        
        return Response({
            'message': f'Removed {product_name} from {wishlist.name}',
            'wishlist': detail_serializer.data,
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
    Refresh wishlist data (NO-OP since we use local DB)
    Products are automatically synced from WooCommerce to local DB
    This endpoint now just returns the wishlist with current data
    """
    try:
        wishlist = WishList.objects.get(id=wishlist_id, user=request.user)
    except WishList.DoesNotExist:
        return Response({
            'error': 'Wishlist not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # ✅ NO consultar WooCommerce - los productos ya están sincronizados en la DB local
    # El serializer lee desde WooCommerceProduct table que se sincroniza automáticamente
    
    items_count = wishlist.items.count()
    
    # Get currency from request (set by CurrencyMiddleware)
    currency = getattr(request, 'currency', 'COP')
    
    detail_serializer = WishListDetailSerializer(wishlist, context={'request': request})
    
    # ✅ NO aplicar convert_price_fields - el serializer ya convierte los precios
    
    return Response({
        'message': f'Wishlist data loaded from local database ({items_count} items)',
        'wishlist': detail_serializer.data,
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
        
        # Get currency from request (set by CurrencyMiddleware)
        currency = getattr(request, 'currency', 'COP')
        
        # Serializar wishlists (sin cargar productos para listado rápido)
        from ..serializers.wishlist_serializers import WishListPublicListSerializer
        serializer = WishListPublicListSerializer(wishlists, many=True, context={'request': request})
        
        # ✅ NO aplicar convert_price_fields - el serializer ya convierte los precios
        
        return Response({
            'success': True,
            'message': f'Wishlists de @{username}',
            'username': username,
            'user_id': user.id,
            'total_wishlists': wishlists.count(),
            'wishlists': serializer.data,
            'currency': currency.upper()
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
        
        # ✅ NO aplicar convert_price_fields - el serializer ya convierte los precios
        
        return Response({
            'wishlist': detail_serializer.data,
            'currency': currency.upper()
        }, status=status.HTTP_200_OK)
        
    except WishList.DoesNotExist:
        return Response({
            'error': 'Wishlist not found or is not public'
        }, status=status.HTTP_404_NOT_FOUND)

