"""
Product views for CrushMe e-commerce application
Handles product CRUD operations, search, and category management
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from ..models import Product
from ..serializers.product_serializers import (
    ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer,
    ProductSearchSerializer, ProductCategorySerializer, ProductStockUpdateSerializer
)
from ..services.woocommerce_service import woocommerce_service


@api_view(['GET'])
@permission_classes([AllowAny])
def get_products(request):
    """
    Get list of all active products
    """
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    serializer = ProductListSerializer(products, many=True, context={'request': request})
    
    return Response({
        'products': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product(request, product_id):
    """
    Get detailed information about a specific product
    """
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProductDetailSerializer(product, context={'request': request})
    
    return Response({
        'product': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_products_by_category(request):
    """
    Get products filtered by category
    """
    category = request.query_params.get('category')
    
    if not category:
        return Response({
            'error': 'Category parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate category exists
    valid_categories = [choice[0] for choice in Product.CATEGORY_CHOICES]
    if category not in valid_categories:
        return Response({
            'error': 'Invalid category',
            'valid_categories': valid_categories
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get products
    products = Product.objects.filter(category=category, is_active=True).order_by('-created_at')
    serializer = ProductListSerializer(products, many=True, context={'request': request})
    
    return Response({
        'products': serializer.data,
        'category': category,
        'category_display': dict(Product.CATEGORY_CHOICES).get(category)
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_products(request):
    """
    Search products by name or description
    """
    query = request.query_params.get('q', '').strip()
    
    if not query:
        return Response({
            'error': 'Search query is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if len(query) < 2:
        return Response({
            'error': 'Search query must be at least 2 characters long'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Search products
    products = Product.search_products(query)
    serializer = ProductListSerializer(products, many=True, context={'request': request})
    
    return Response({
        'products': serializer.data,
        'query': query
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    """
    Get all product categories with product counts
    """
    categories = ProductCategorySerializer.get_categories_with_counts()
    
    return Response({
        'categories': categories
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_product(request):
    """
    Create a new product (Admin only)
    """
    serializer = ProductCreateUpdateSerializer(data=request.data)
    
    if serializer.is_valid():
        product = serializer.save()
        detail_serializer = ProductDetailSerializer(product, context={'request': request})
        
        return Response({
            'message': 'Product created successfully',
            'product': detail_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_product(request, product_id):
    """
    Update an existing product (Admin only)
    """
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProductCreateUpdateSerializer(product, data=request.data, partial=True)
    
    if serializer.is_valid():
        product = serializer.save()
        detail_serializer = ProductDetailSerializer(product, context={'request': request})
        
        return Response({
            'message': 'Product updated successfully',
            'product': detail_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_product(request, product_id):
    """
    Delete a product (Admin only)
    Soft delete by setting is_active to False
    """
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Soft delete
    product.is_active = False
    product.save()
    
    return Response({
        'message': 'Product deleted successfully'
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_product_stock(request, product_id):
    """
    Update product stock quantity (Admin only)
    """
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProductStockUpdateSerializer(data=request.data)
    
    if serializer.is_valid():
        new_stock = serializer.validated_data['stock_quantity']
        product.stock_quantity = new_stock
        product.save()
        
        return Response({
            'message': 'Stock updated successfully',
            'product_id': product.id,
            'new_stock': new_stock,
            'is_in_stock': product.is_in_stock
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_featured_products(request):
    """
    Get featured products (latest products or high-rated ones)
    """
    # For now, return latest products
    # In future, this could be based on ratings, sales, or admin selection
    products = Product.objects.filter(
        is_active=True,
        stock_quantity__gt=0
    ).order_by('-created_at')[:12]
    
    serializer = ProductListSerializer(products, many=True, context={'request': request})
    
    return Response({
        'featured_products': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_recommendations(request, product_id):
    """
    Get product recommendations based on category
    """
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get similar products from same category
    similar_products = Product.objects.filter(
        category=product.category,
        is_active=True,
        stock_quantity__gt=0
    ).exclude(id=product.id).order_by('?')[:8]  # Random order
    
    serializer = ProductListSerializer(similar_products, many=True, context={'request': request})
    
    return Response({
        'recommendations': serializer.data,
        'based_on': {
            'product_id': product.id,
            'product_name': product.name,
            'category': product.category
        }
    }, status=status.HTTP_200_OK)


# ========== WOOCOMMERCE INTEGRATION ENDPOINTS ==========

@api_view(['GET'])
@permission_classes([IsAdminUser])  # Solo administradores pueden ver la estructura de WooCommerce
def get_woocommerce_products(request):
    """
    Obtener productos desde WooCommerce para ver su estructura
    Query params:
    - category_id: ID de categoría (opcional)
    - per_page: Productos por página (máx 100, default 10)
    - page: Número de página (default 1)
    """
    category_id = request.query_params.get('category_id')
    per_page = int(request.query_params.get('per_page', 10))
    page = int(request.query_params.get('page', 1))
    
    try:
        # Validar category_id si se proporciona
        if category_id:
            category_id = int(category_id)
        
        # Llamar al servicio de WooCommerce
        result = woocommerce_service.get_products(
            category_id=category_id,
            per_page=per_page,
            page=page
        )
        
        if result['success']:
            return Response({
                'success': True,
                'message': 'Productos obtenidos exitosamente desde WooCommerce',
                'data': result['data'],
                'pagination_info': {
                    'page': page,
                    'per_page': per_page,
                    'category_id': category_id
                },
                'api_info': {
                    'status_code': result['status_code'],
                    'headers': result.get('headers', {})
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result['error'],
                'status_code': result.get('status_code'),
                'details': result.get('response_text')
            }, status=status.HTTP_502_BAD_GATEWAY)
            
    except ValueError as e:
        return Response({
            'error': 'Parámetros inválidos',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])  # Solo administradores pueden ver la estructura de WooCommerce
def get_woocommerce_categories(request):
    """
    Obtener categorías desde WooCommerce para ver su estructura
    Query params:
    - per_page: Categorías por página (default 100)
    - page: Número de página (default 1)
    """
    per_page = int(request.query_params.get('per_page', 100))
    page = int(request.query_params.get('page', 1))
    
    try:
        # Llamar al servicio de WooCommerce
        result = woocommerce_service.get_categories(
            per_page=per_page,
            page=page
        )
        
        if result['success']:
            return Response({
                'success': True,
                'message': 'Categorías obtenidas exitosamente desde WooCommerce',
                'data': result['data'],
                'pagination_info': {
                    'page': page,
                    'per_page': per_page
                },
                'api_info': {
                    'status_code': result['status_code'],
                    'headers': result.get('headers', {})
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result['error'],
                'status_code': result.get('status_code'),
                'details': result.get('response_text')
            }, status=status.HTTP_502_BAD_GATEWAY)
            
    except ValueError as e:
        return Response({
            'error': 'Parámetros inválidos',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_woocommerce_product_detail(request, product_id):
    """
    Obtener un producto específico desde WooCommerce por ID
    """
    try:
        product_id = int(product_id)
        
        # Llamar al servicio de WooCommerce
        result = woocommerce_service.get_product_by_id(product_id)
        
        if result['success']:
            return Response({
                'success': True,
                'message': f'Producto {product_id} obtenido exitosamente desde WooCommerce',
                'data': result['data'],
                'api_info': {
                    'status_code': result['status_code'],
                    'headers': result.get('headers', {})
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result['error'],
                'status_code': result.get('status_code'),
                'details': result.get('response_text')
            }, status=status.HTTP_502_BAD_GATEWAY)
            
    except ValueError:
        return Response({
            'error': 'ID de producto inválido'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def test_woocommerce_connection(request):
    """
    Endpoint para probar la conexión con WooCommerce
    """
    try:
        # Intentar obtener solo 1 producto para probar la conexión
        result = woocommerce_service.get_products(per_page=1, page=1)
        
        if result['success']:
            return Response({
                'success': True,
                'message': 'Conexión con WooCommerce exitosa',
                'connection_status': 'OK',
                'api_response_headers': result.get('headers', {}),
                'sample_data_structure': {
                    'products_count': len(result['data']) if result['data'] else 0,
                    'first_product_keys': list(result['data'][0].keys()) if result['data'] and len(result['data']) > 0 else []
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Error en conexión con WooCommerce',
                'connection_status': 'FAILED',
                'error': result['error'],
                'status_code': result.get('status_code'),
                'details': result.get('response_text')
            }, status=status.HTTP_502_BAD_GATEWAY)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Error interno en prueba de conexión',
            'connection_status': 'ERROR',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
