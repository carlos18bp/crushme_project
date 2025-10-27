"""
Wishlist views for CrushMe e-commerce application
Handles wishlist CRUD operations, sharing, and favorites functionality
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.db import transaction

from ..models import WishList, WishListItem, FavoriteWishList, Product
from ..serializers.wishlist_serializers import (
    WishListListSerializer, WishListDetailSerializer, WishListCreateUpdateSerializer,
    WishListPublicSerializer, WishListShippingSerializer, FavoriteWishListSerializer,
    WishListSearchSerializer, AddProductToWishListSerializer, WishListItemSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wishlists(request):
    """
    Get user's wishlists
    """
    wishlists = WishList.objects.filter(user=request.user).order_by('-created_at')
    serializer = WishListListSerializer(wishlists, many=True, context={'request': request})
    
    return Response({
        'wishlists': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_wishlist(request):
    """
    Create a new wishlist
    
    Required fields:
    - name: string (min 2 characters)
    
    Optional fields:
    - description: string (min 5 characters if provided)
    - is_active: boolean (default: true)
    - is_public: boolean (default: false)
    - shipping_data: object with keys: name, address, phone, email
    """
    # Log request data for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Creating wishlist with data: {request.data}")
    
    serializer = WishListCreateUpdateSerializer(data=request.data)
    
    if serializer.is_valid():
        wishlist = serializer.save(user=request.user)
        detail_serializer = WishListDetailSerializer(wishlist, context={'request': request})
        
        return Response({
            'message': 'Wishlist created successfully',
            'wishlist': detail_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    # Log validation errors
    logger.error(f"Wishlist creation failed: {serializer.errors}")
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wishlist(request, wishlist_id):
    """
    Get detailed information about a specific wishlist
    Automatically loads fresh product data from WooCommerce
    """
    try:
        wishlist = WishList.objects.get(id=wishlist_id, user=request.user)
    except WishList.DoesNotExist:
        return Response({
            'error': 'Wishlist not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Enriquecer con datos frescos de WooCommerce
    from ..services.woocommerce_service import woocommerce_service
    
    items = wishlist.items.all()
    if items:
        # Extraer IDs de productos WooCommerce
        wc_product_ids = [item.woocommerce_product_id for item in items if item.woocommerce_product_id]
        
        if wc_product_ids:
            # Consultar productos desde WooCommerce y actualizar caché
            for product_id in wc_product_ids:
                result = woocommerce_service.get_product_by_id(product_id)
                if result['success']:
                    # Actualizar el item correspondiente
                    item = items.filter(woocommerce_product_id=product_id).first()
                    if item:
                        item.update_product_data(result['data'])
    
    serializer = WishListDetailSerializer(wishlist, context={'request': request})
    
    return Response({
        'wishlist': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_wishlist(request, wishlist_id):
    """
    Update wishlist information
    """
    try:
        wishlist = WishList.objects.get(id=wishlist_id, user=request.user)
    except WishList.DoesNotExist:
        return Response({
            'error': 'Wishlist not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = WishListCreateUpdateSerializer(wishlist, data=request.data, partial=True)
    
    if serializer.is_valid():
        wishlist = serializer.save()
        detail_serializer = WishListDetailSerializer(wishlist, context={'request': request})
        
        return Response({
            'message': 'Wishlist updated successfully',
            'wishlist': detail_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_wishlist(request, wishlist_id):
    """
    Delete a wishlist
    """
    try:
        wishlist = WishList.objects.get(id=wishlist_id, user=request.user)
    except WishList.DoesNotExist:
        return Response({
            'error': 'Wishlist not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    wishlist_name = wishlist.name
    wishlist.delete()
    
    return Response({
        'message': f'Wishlist "{wishlist_name}" deleted successfully'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product_to_wishlist(request, wishlist_id):
    """
    Add a product to a wishlist
    """
    try:
        wishlist = WishList.objects.get(id=wishlist_id, user=request.user)
    except WishList.DoesNotExist:
        return Response({
            'error': 'Wishlist not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = AddProductToWishListSerializer(
        data=request.data,
        context={'wishlist': wishlist}
    )
    
    if serializer.is_valid():
        product_id = serializer.validated_data['product_id']
        notes = serializer.validated_data.get('notes', '')
        priority = serializer.validated_data.get('priority', 'medium')
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Add product to wishlist
            wishlist_item, created = wishlist.add_product(product)
            
            if created:
                # Update additional fields if item was created
                wishlist_item.notes = notes
                wishlist_item.priority = priority
                wishlist_item.save()
                
                detail_serializer = WishListDetailSerializer(wishlist, context={'request': request})
                
                return Response({
                    'message': f'Added {product.name} to {wishlist.name}',
                    'wishlist': detail_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Product is already in this wishlist'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Product.DoesNotExist:
            return Response({
                'error': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_product_from_wishlist(request, wishlist_id, product_id):
    """
    Remove a product from a wishlist
    """
    try:
        wishlist = WishList.objects.get(id=wishlist_id, user=request.user)
        product = Product.objects.get(id=product_id)
    except WishList.DoesNotExist:
        return Response({
            'error': 'Wishlist not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Product.DoesNotExist:
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if wishlist.remove_product(product):
        detail_serializer = WishListDetailSerializer(wishlist, context={'request': request})
        
        return Response({
            'message': f'Removed {product.name} from {wishlist.name}',
            'wishlist': detail_serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Product is not in this wishlist'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_public_wishlist(request, unique_link):
    """
    Get public wishlist by UUID link
    Automatically loads fresh product data from WooCommerce
    """
    try:
        wishlist = WishList.objects.get(unique_link=unique_link, is_public=True, is_active=True)
    except WishList.DoesNotExist:
        return Response({
            'error': 'Wishlist not found or is not public'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Enriquecer con datos frescos de WooCommerce
    from ..services.woocommerce_service import woocommerce_service
    
    items = wishlist.items.all()
    if items:
        wc_product_ids = [item.woocommerce_product_id for item in items if item.woocommerce_product_id]
        
        if wc_product_ids:
            for product_id in wc_product_ids:
                result = woocommerce_service.get_product_by_id(product_id)
                if result['success']:
                    item = items.filter(woocommerce_product_id=product_id).first()
                    if item:
                        item.update_product_data(result['data'])
    
    serializer = WishListPublicSerializer(wishlist, context={'request': request})
    
    return Response({
        'wishlist': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_public_wishlists(request):
    """
    Get all public wishlists
    """
    wishlists = WishList.objects.filter(is_public=True, is_active=True).order_by('-created_at')
    serializer = WishListListSerializer(wishlists, many=True, context={'request': request})
    
    return Response({
        'wishlists': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def favorite_wishlist(request, wishlist_id):
    """
    Add a wishlist to user's favorites
    """
    try:
        wishlist = WishList.objects.get(id=wishlist_id, is_public=True, is_active=True)
    except WishList.DoesNotExist:
        return Response({
            'error': 'Wishlist not found or is not public'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if wishlist.user == request.user:
        return Response({
            'error': 'You cannot favorite your own wishlist'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        favorite, created = FavoriteWishList.add_favorite(request.user, wishlist)
        
        if created:
            return Response({
                'message': f'Added {wishlist.name} to your favorites'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Wishlist is already in your favorites'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unfavorite_wishlist(request, wishlist_id):
    """
    Remove a wishlist from user's favorites
    """
    try:
        wishlist = WishList.objects.get(id=wishlist_id)
    except WishList.DoesNotExist:
        return Response({
            'error': 'Wishlist not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if FavoriteWishList.remove_favorite(request.user, wishlist):
        return Response({
            'message': f'Removed {wishlist.name} from your favorites'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Wishlist is not in your favorites'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_favorite_wishlists(request):
    """
    Get user's favorite wishlists
    """
    favorites = FavoriteWishList.get_user_favorites(request.user)
    serializer = FavoriteWishListSerializer(favorites, many=True, context={'request': request})
    
    return Response({
        'favorite_wishlists': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_wishlist_shipping(request, wishlist_id):
    """
    Update wishlist shipping information
    """
    try:
        wishlist = WishList.objects.get(id=wishlist_id, user=request.user)
    except WishList.DoesNotExist:
        return Response({
            'error': 'Wishlist not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = WishListShippingSerializer(data=request.data)
    
    if serializer.is_valid():
        shipping_data = serializer.validated_data
        
        # Update shipping data
        wishlist.set_shipping_data(
            name=shipping_data.get('name'),
            address=shipping_data.get('address'),
            phone=shipping_data.get('phone'),
            email=shipping_data.get('email')
        )
        
        detail_serializer = WishListDetailSerializer(wishlist, context={'request': request})
        
        return Response({
            'message': 'Shipping information updated successfully',
            'wishlist': detail_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_wishlist_item(request, wishlist_id, item_id):
    """
    Update a wishlist item (notes, priority)
    """
    try:
        wishlist = WishList.objects.get(id=wishlist_id, user=request.user)
        wishlist_item = wishlist.items.get(id=item_id)
    except WishList.DoesNotExist:
        return Response({
            'error': 'Wishlist not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except WishListItem.DoesNotExist:
        return Response({
            'error': 'Wishlist item not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = WishListItemSerializer(wishlist_item, data=request.data, partial=True)
    
    if serializer.is_valid():
        wishlist_item = serializer.save()
        
        return Response({
            'message': 'Wishlist item updated successfully',
            'item': WishListItemSerializer(wishlist_item, context={'request': request}).data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
