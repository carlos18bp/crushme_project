"""
Product views for CrushMe e-commerce application
Handles product CRUD operations, search, and category management
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
import json
import logging
import os
from datetime import datetime
from django.conf import settings

from ..models import Product
from ..serializers.product_serializers import (
    ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer,
    ProductSearchSerializer, ProductCategorySerializer, ProductStockUpdateSerializer
)
from ..services.woocommerce_service import woocommerce_service
from ..services.translation_service import create_translator_from_request

logger = logging.getLogger(__name__)


def translate_woocommerce_product(product, translator, translate_full=False):
    """
    Traduce los campos de texto de un producto de WooCommerce al idioma objetivo.
    
    Args:
        product (dict): Producto de WooCommerce
        translator (TranslationService): Instancia del servicio de traducción
        translate_full (bool): Si True, traduce también description (pesado). Default False.
    
    Returns:
        dict: Producto con campos traducidos
    """
    if not product or not isinstance(product, dict):
        return product
    
    # Traducir solo campos esenciales para optimizar velocidad
    # name y short_description son suficientes para listados
    if product.get('name'):
        product['name'] = translator.translate_if_needed(product['name'], content_language='es')
    
    if product.get('short_description'):
        product['short_description'] = translator.translate_if_needed(product['short_description'], content_language='es')
    
    # Solo traducir description completa si es necesario (detalle de producto)
    # La description es HTML largo y ralentiza mucho
    if translate_full and product.get('description'):
        product['description'] = translator.translate_if_needed(product['description'], content_language='es')
    
    # Traducir solo primera categoría (la principal)
    # Traducir todas es innecesario y lento
    if product.get('categories') and isinstance(product['categories'], list) and len(product['categories']) > 0:
        if product['categories'][0].get('name'):
            product['categories'][0]['name'] = translator.translate_if_needed(
                product['categories'][0]['name'], 
                content_language='es'
            )
    
    # NO traducir atributos por ahora - son demasiados y ralentizan
    # Los atributos se pueden traducir en detalle de producto si es necesario
    
    return product


def translate_woocommerce_products(products, request, translate_full=False):
    """
    Traduce una lista de productos de WooCommerce según el idioma solicitado.
    
    Args:
        products (list): Lista de productos de WooCommerce
        request: Request object para obtener el idioma
        translate_full (bool): Si True, traduce campos completos incluyendo description
    
    Returns:
        list: Lista de productos traducidos
    """
    if not products or not isinstance(products, list):
        return products
    
    # Permitir desactivar traducción con query param translate=false
    if request.GET.get('translate', 'true').lower() == 'false':
        return products
    
    translator = create_translator_from_request(request)
    
    # Si el idioma objetivo es español, no traducir (ya están en español)
    if translator.target_language == 'es':
        return products
    
    # Traducir cada producto (solo campos esenciales por defecto)
    translated_products = []
    for product in products:
        translated_product = translate_woocommerce_product(
            product.copy(), 
            translator,
            translate_full=translate_full
        )
        translated_products.append(translated_product)
    
    return translated_products


def translate_woocommerce_categories(categories, request):
    """
    Traduce los nombres de categorías de WooCommerce según el idioma solicitado.
    
    Args:
        categories (list): Lista de categorías de WooCommerce
        request: Request object para obtener el idioma
    
    Returns:
        list: Lista de categorías traducidas
    """
    if not categories or not isinstance(categories, list):
        return categories
    
    translator = create_translator_from_request(request)
    
    # Si el idioma objetivo es español, no traducir (ya están en español)
    if translator.target_language == 'es':
        return categories
    
    # Traducir cada categoría
    translated_categories = []
    for category in categories:
        if isinstance(category, dict):
            category_copy = category.copy()
            if category_copy.get('name'):
                category_copy['name'] = translator.translate_if_needed(category_copy['name'], content_language='es')
            if category_copy.get('description'):
                category_copy['description'] = translator.translate_if_needed(category_copy['description'], content_language='es')
            translated_categories.append(category_copy)
        else:
            translated_categories.append(category)
    
    return translated_categories


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
@permission_classes([AllowAny])  # Endpoint público para obtener productos de WooCommerce
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
            # ===== LOG DE ESTRUCTURA DE DATOS EN ARCHIVO =====
            products_data = result['data']
            
            # Preparar log para archivo
            products_to_log = products_data[:9] if len(products_data) >= 9 else products_data
            
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "endpoint": "get_woocommerce_products",
                "params": {
                    "category_id": category_id,
                    "page": page,
                    "per_page": per_page
                },
                "total_products_received": len(products_data),
                "products_in_log": len(products_to_log),
                "products": products_to_log
            }
            
            # Guardar en archivo
            log_file_path = os.path.join(settings.BASE_DIR, 'woocommerce_products_log.json')
            try:
                with open(log_file_path, 'w', encoding='utf-8') as f:
                    json.dump(log_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Log de productos guardado en: {log_file_path}")
                print(f"✅ Log guardado en: {log_file_path} ({len(products_to_log)} productos)")
            except Exception as e:
                logger.error(f"Error al guardar log: {str(e)}")
            # ===== FIN DEL LOG =====
            
            # Traducir productos al idioma solicitado
            translated_products = translate_woocommerce_products(result['data'], request)
            
            return Response({
                'success': True,
                'message': 'Productos obtenidos exitosamente desde WooCommerce',
                'data': translated_products,
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
@permission_classes([AllowAny])  # Endpoint público para obtener categorías de WooCommerce
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
            # Traducir categorías al idioma solicitado
            translated_categories = translate_woocommerce_categories(result['data'], request)
            
            return Response({
                'success': True,
                'message': 'Categorías obtenidas exitosamente desde WooCommerce',
                'data': translated_categories,
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
@permission_classes([AllowAny])  # Endpoint público para obtener detalle de producto de WooCommerce
def get_woocommerce_product_detail(request, product_id):
    """
    Obtener un producto específico desde WooCommerce por ID
    """
    try:
        product_id = int(product_id)
        
        # Llamar al servicio de WooCommerce
        result = woocommerce_service.get_product_by_id(product_id)
        
        if result['success']:
            # Traducir producto al idioma solicitado (traducción completa para detalle)
            translator = create_translator_from_request(request)
            translated_product = translate_woocommerce_product(
                result['data'].copy(), 
                translator, 
                translate_full=True  # Traducción completa incluyendo description
            ) if translator.target_language != 'es' else result['data']
            
            return Response({
                'success': True,
                'message': f'Producto {product_id} obtenido exitosamente desde WooCommerce',
                'data': translated_product,
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


@api_view(['POST'])
@permission_classes([AllowAny])
def get_woocommerce_products_batch(request):
    """
    Obtener múltiples productos de WooCommerce por sus IDs
    Útil para mostrar wishlists con información actualizada de productos
    
    POST Body:
    {
        "product_ids": [123, 456, 789]
    }
    """
    try:
        product_ids = request.data.get('product_ids', [])
        
        if not isinstance(product_ids, list):
            return Response({
                'error': 'product_ids debe ser una lista'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not product_ids:
            return Response({
                'error': 'product_ids no puede estar vacía'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(product_ids) > 100:
            return Response({
                'error': 'Máximo 100 productos por consulta'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener productos de WooCommerce
        products = []
        errors = []
        
        for product_id in product_ids:
            try:
                product_id_int = int(product_id)
                result = woocommerce_service.get_product_by_id(product_id_int)
                
                if result['success']:
                    products.append(result['data'])
                else:
                    errors.append({
                        'product_id': product_id_int,
                        'error': result.get('error', 'Unknown error')
                    })
            except (ValueError, TypeError):
                errors.append({
                    'product_id': product_id,
                    'error': 'ID inválido'
                })
        
        # Traducir productos al idioma solicitado
        translated_products = translate_woocommerce_products(products, request)
        
        return Response({
            'success': True,
            'message': f'Obtenidos {len(translated_products)} productos ({len(errors)} errores)',
            'products': translated_products,
            'total_requested': len(product_ids),
            'total_found': len(translated_products),
            'total_errors': len(errors),
            'errors': errors if errors else None
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])  # Endpoint público para probar conexión con WooCommerce
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


@api_view(['GET'])
@permission_classes([AllowAny])  # Endpoint público para obtener productos en tendencia
def get_trending_products(request):
    """
    Obtener 8 productos en tendencia desde WooCommerce
    Los productos se ordenan por popularidad (más vendidos y mejor calificados)
    """
    try:
        # Obtener más productos de los necesarios para poder filtrar y ordenar
        result = woocommerce_service.get_products(
            per_page=50,
            page=1
        )
        
        if result['success']:
            products = result['data']
            
            # Filtrar solo productos con stock disponible
            in_stock_products = []
            for p in products:
                stock_qty = p.get('stock_quantity')
                stock_status = p.get('stock_status')
                
                # Incluir si tiene stock "instock" o si stock_quantity es None (productos variables)
                if stock_status == 'instock':
                    if stock_qty is None or stock_qty > 0:
                        in_stock_products.append(p)
            
            # Ordenar por popularidad (combinación de ventas y rating)
            # Prioridad: total_sales > average_rating > rating_count
            def get_popularity_score(product):
                try:
                    total_sales = int(product.get('total_sales', 0) or 0)
                    average_rating_str = product.get('average_rating', '0') or '0'
                    average_rating = float(average_rating_str)
                    rating_count = int(product.get('rating_count', 0) or 0)
                    
                    # Fórmula de popularidad: ventas * 10 + rating * 5 + número de reseñas
                    return (total_sales * 10) + (average_rating * 5) + rating_count
                except (ValueError, TypeError):
                    return 0
            
            # Ordenar por popularidad descendente
            sorted_products = sorted(
                in_stock_products,
                key=get_popularity_score,
                reverse=True
            )
            
            # Tomar solo los 8 primeros
            trending_products = sorted_products[:8]
            
            # Traducir productos al idioma solicitado
            translated_products = translate_woocommerce_products(trending_products, request)
            
            return Response({
                'success': True,
                'message': f'{len(translated_products)} productos en tendencia obtenidos exitosamente',
                'data': translated_products,
                'total_products': len(translated_products),
                'api_info': {
                    'status_code': result['status_code'],
                    'source': 'woocommerce',
                    'cached': result.get('cached', False)
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result['error'],
                'status_code': result.get('status_code'),
                'details': result.get('response_text')
            }, status=status.HTTP_502_BAD_GATEWAY)
            
    except Exception as e:
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_variations(request, product_id):
    """
    Obtener todas las variaciones de un producto variable desde WooCommerce
    Query params:
    - per_page: Variaciones por página (máx 100, default 100)
    - page: Número de página (default 1)
    - translate: Si es 'false', no traduce el contenido (default 'true')
    
    Headers:
    - Accept-Language: Idioma destino (ej: 'en', 'es'). Si es 'es' no traduce.
    """
    per_page = int(request.query_params.get('per_page', 100))
    page = int(request.query_params.get('page', 1))
    
    try:
        product_id = int(product_id)
        
        # Llamar al servicio de WooCommerce
        result = woocommerce_service.get_product_variations(
            product_id=product_id,
            per_page=per_page,
            page=page
        )
        
        if result['success']:
            # Traducir variaciones al idioma solicitado (traducción completa para variaciones)
            translated_variations = translate_woocommerce_products(
                result['data'], 
                request, 
                translate_full=True
            )
            
            return Response({
                'success': True,
                'message': f'Variaciones del producto {product_id} obtenidas exitosamente',
                'data': translated_variations,
                'total_variations': len(translated_variations),
                'pagination_info': {
                    'page': page,
                    'per_page': per_page,
                    'product_id': product_id
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
@permission_classes([AllowAny])
def get_product_variation_detail(request, product_id, variation_id):
    """
    Obtener una variación específica de un producto desde WooCommerce
    Query params:
    - translate: Si es 'false', no traduce el contenido (default 'true')
    """
    try:
        product_id = int(product_id)
        variation_id = int(variation_id)
        
        # Llamar al servicio de WooCommerce
        result = woocommerce_service.get_product_variation_by_id(product_id, variation_id)
        
        if result['success']:
            variation_data = result['data']
            
            # Verificar si se debe traducir
            should_translate = request.GET.get('translate', 'true').lower() != 'false'
            
            if should_translate:
                # Traducir variación al idioma solicitado (traducción completa para detalle)
                translator = create_translator_from_request(request)
                if translator.target_language != 'es':
                    variation_data = translate_woocommerce_product(
                        variation_data.copy(), 
                        translator, 
                        translate_full=True  # Traducción completa incluyendo description
                    )
            
            return Response({
                'success': True,
                'message': f'Variación {variation_id} del producto {product_id} obtenida exitosamente',
                'data': variation_data,
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
            'error': 'IDs de producto o variación inválidos'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
