"""
Views for managing user's favorite products
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import logging

from ..models.favorite_product import FavoriteProduct
from ..serializers.favorite_product_serializers import (
    FavoriteProductSerializer,
    AddFavoriteProductSerializer,
    FavoriteProductListSerializer
)
from ..services.woocommerce_service import woocommerce_service

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_favorite_product(request):
    """
    Add a product to user's favorites
    
    POST Body:
    {
        "woocommerce_product_id": 123
    }
    
    Returns the favorite with product data loaded from WooCommerce
    """
    serializer = AddFavoriteProductSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'error': 'Datos inválidos',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    woocommerce_product_id = serializer.validated_data['woocommerce_product_id']
    
    # Check if already favorited
    if FavoriteProduct.is_favorited(request.user, woocommerce_product_id):
        return Response({
            'success': False,
            'error': 'Este producto ya está en tus favoritos'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Fetch product data from WooCommerce
        wc_result = woocommerce_service.get_product_by_id(woocommerce_product_id)
        
        if not wc_result['success']:
            return Response({
                'success': False,
                'error': 'No se pudo obtener información del producto desde WooCommerce',
                'details': wc_result.get('error')
            }, status=status.HTTP_502_BAD_GATEWAY)
        
        product_data = wc_result['data']
        
        # Add to favorites with cached product data
        favorite, created = FavoriteProduct.add_favorite(
            user=request.user,
            woocommerce_product_id=woocommerce_product_id,
            product_data=product_data
        )
        
        if created:
            # Get currency from request (set by CurrencyMiddleware)
            currency = getattr(request, 'currency', 'COP')
            
            serializer = FavoriteProductSerializer(favorite)
            response_data = {
                'success': True,
                'message': 'Producto agregado a favoritos exitosamente',
                'data': serializer.data
            }
            
            # Convert prices to target currency
            from ..utils.price_helpers import convert_price_fields
            response_data = convert_price_fields(response_data, currency)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'error': 'El producto ya estaba en favoritos'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error adding favorite product: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al agregar producto a favoritos',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_favorite_product(request, woocommerce_product_id):
    """
    Remove a product from user's favorites
    
    DELETE /api/favorites/products/{woocommerce_product_id}/
    """
    try:
        woocommerce_product_id = int(woocommerce_product_id)
        
        removed = FavoriteProduct.remove_favorite(request.user, woocommerce_product_id)
        
        if removed:
            return Response({
                'success': True,
                'message': 'Producto eliminado de favoritos exitosamente'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': 'El producto no está en tus favoritos'
            }, status=status.HTTP_404_NOT_FOUND)
    
    except ValueError:
        return Response({
            'success': False,
            'error': 'ID de producto inválido'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error removing favorite product: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al eliminar producto de favoritos',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_favorite_products(request):
    """
    Get all favorite products for the authenticated user
    Automatically refreshes product data from WooCommerce if cache is stale
    
    GET /api/favorites/products/
    
    Query params:
    - refresh: Set to 'true' to force refresh from WooCommerce (optional)
    """
    force_refresh = request.query_params.get('refresh', 'false').lower() == 'true'
    
    try:
        favorites = FavoriteProduct.get_user_favorites(request.user)
        
        # Refresh stale or missing product data
        updated_count = 0
        for favorite in favorites:
            should_refresh = force_refresh or favorite.needs_cache_refresh()
            
            if should_refresh:
                try:
                    wc_result = woocommerce_service.get_product_by_id(favorite.woocommerce_product_id)
                    
                    if wc_result['success']:
                        favorite.update_product_cache(wc_result['data'])
                        updated_count += 1
                    else:
                        logger.warning(
                            f"Failed to refresh product {favorite.woocommerce_product_id}: "
                            f"{wc_result.get('error')}"
                        )
                except Exception as e:
                    logger.error(
                        f"Error refreshing product {favorite.woocommerce_product_id}: {str(e)}"
                    )
        
        # Get currency from request (set by CurrencyMiddleware)
        currency = getattr(request, 'currency', 'COP')
        
        # Serialize with full product data
        serializer = FavoriteProductListSerializer(favorites, many=True)
        
        response_data = {
            'success': True,
            'message': 'Favoritos obtenidos exitosamente',
            'data': serializer.data,
            'meta': {
                'total_favorites': favorites.count(),
                'products_refreshed': updated_count
            }
        }
        
        # Convert prices to target currency
        from ..utils.price_helpers import convert_price_fields
        response_data = convert_price_fields(response_data, currency)
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error getting favorite products: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener favoritos',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_favorite_status(request, woocommerce_product_id):
    """
    Check if a product is in user's favorites
    
    GET /api/favorites/products/{woocommerce_product_id}/status/
    """
    try:
        woocommerce_product_id = int(woocommerce_product_id)
        
        is_favorited = FavoriteProduct.is_favorited(request.user, woocommerce_product_id)
        
        return Response({
            'success': True,
            'is_favorited': is_favorited,
            'woocommerce_product_id': woocommerce_product_id
        }, status=status.HTTP_200_OK)
    
    except ValueError:
        return Response({
            'success': False,
            'error': 'ID de producto inválido'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_favorite_product_ids(request):
    """
    Get list of WooCommerce product IDs that are in user's favorites
    Useful for frontend to quickly check which products are favorited
    
    GET /api/favorites/products/ids/
    """
    try:
        product_ids = FavoriteProduct.get_user_favorite_ids(request.user)
        
        return Response({
            'success': True,
            'product_ids': product_ids,
            'count': len(product_ids)
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error getting favorite product IDs: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener IDs de favoritos',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_favorite_products(request):
    """
    Force refresh all favorite products from WooCommerce
    Useful after bulk changes or to ensure fresh data
    
    POST /api/favorites/products/refresh/
    """
    try:
        favorites = FavoriteProduct.get_user_favorites(request.user)
        
        success_count = 0
        error_count = 0
        errors = []
        
        for favorite in favorites:
            try:
                wc_result = woocommerce_service.get_product_by_id(favorite.woocommerce_product_id)
                
                if wc_result['success']:
                    favorite.update_product_cache(wc_result['data'])
                    success_count += 1
                else:
                    error_count += 1
                    errors.append({
                        'product_id': favorite.woocommerce_product_id,
                        'error': wc_result.get('error')
                    })
            except Exception as e:
                error_count += 1
                errors.append({
                    'product_id': favorite.woocommerce_product_id,
                    'error': str(e)
                })
        
        return Response({
            'success': True,
            'message': 'Productos actualizados',
            'stats': {
                'total': favorites.count(),
                'updated': success_count,
                'errors': error_count
            },
            'errors': errors if errors else None
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error refreshing favorite products: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al actualizar favoritos',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_all_favorites(request):
    """
    Remove all favorite products for the authenticated user
    
    DELETE /api/favorites/products/clear/
    """
    try:
        count = FavoriteProduct.objects.filter(user=request.user).count()
        FavoriteProduct.objects.filter(user=request.user).delete()
        
        return Response({
            'success': True,
            'message': f'{count} productos eliminados de favoritos'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error clearing favorite products: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al limpiar favoritos',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


