"""
Optimized WooCommerce Views - Local Database
Uses locally synchronized data with pre-translated content and price margins
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q, Prefetch
import logging
import random

from ..models import (
    WooCommerceProduct,
    WooCommerceCategory,
    WooCommerceProductVariation,
    TranslatedContent
)
from ..utils.translation_helpers import (
    get_products_list,
    get_product_full_data,
    get_translated_category
)
from ..services.translation_service import get_language_from_request

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_woocommerce_products(request):
    """
    Buscar productos por nombre en español o inglés con paginación.
    
    Query params:
    - q: Query de búsqueda (requerido)
    - page: Número de página (default: 1)
    - per_page: Productos por página (default: 9, máx: 50)
    - lang: Idioma (es/en, también soporta Accept-Language header)
    
    Retorna productos paginados con:
    - Traducciones según idioma
    - Precios con margen aplicado
    - Conversión de currency
    """
    try:
        # Obtener query de búsqueda
        search_query = request.query_params.get('q', '').strip()
        
        if not search_query:
            return Response({
                'error': 'Query de búsqueda requerido',
                'message': 'Debe proporcionar el parámetro "q" con el término de búsqueda'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener parámetros de paginación
        page = int(request.query_params.get('page', 1))
        per_page = min(int(request.query_params.get('per_page', 9)), 50)  # Máximo 50
        
        # Obtener idioma y currency
        target_lang = get_language_from_request(request)
        target_currency = getattr(request, 'currency', 'COP')
        
        logger.info(f"🔍 Búsqueda de productos: '{search_query}' (lang={target_lang}, currency={target_currency}, page={page})")
        
        # Buscar según idioma
        if target_lang == 'es':
            # Buscar en español (campo original name)
            queryset = WooCommerceProduct.objects.filter(
                status='publish',
                name__icontains=search_query
            ).prefetch_related('categories', 'images').select_related()
            
            logger.info(f"📝 Búsqueda en español: {queryset.count()} resultados totales")
            
        else:
            # Buscar en inglés (traducciones)
            # Obtener IDs de productos con traducciones que coincidan
            translated_products = TranslatedContent.objects.filter(
                content_type=TranslatedContent.CONTENT_TYPE_PRODUCT_NAME,
                target_language=target_lang,
                translated_text__icontains=search_query
            ).values_list('object_id', flat=True)
            
            # Si no hay traducciones, buscar en el nombre original como fallback
            if not translated_products:
                logger.info(f"⚠️ No se encontraron traducciones, buscando en nombres originales")
                queryset = WooCommerceProduct.objects.filter(
                    status='publish',
                    name__icontains=search_query
                ).prefetch_related('categories', 'images').select_related()
            else:
                # Obtener productos por IDs encontrados
                queryset = WooCommerceProduct.objects.filter(
                    wc_id__in=list(translated_products),
                    status='publish'
                ).prefetch_related('categories', 'images').select_related()
            
            logger.info(f"📝 Búsqueda en inglés: {queryset.count()} resultados totales")
        
        # Aplicar paginación
        total_count = queryset.count()
        start = (page - 1) * per_page
        end = start + per_page
        products_page = queryset[start:end]
        
        # Convertir a lista con traducciones y conversión de moneda
        products_data = get_products_list(
            queryset=products_page,
            target_language=target_lang,
            include_stock=False,
            target_currency=target_currency
        )
        
        # Calcular información de paginación
        total_pages = (total_count + per_page - 1) // per_page
        
        return Response({
            'success': True,
            'message': f'Se encontraron {total_count} productos',
            'data': products_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_results': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1
            },
            'search': {
                'query': search_query,
                'language': target_lang,
                'currency': target_currency,
                'results_count': len(products_data)
            },
            'source': 'local_db_search'
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({
            'error': 'Parámetros inválidos',
            'details': 'Los parámetros page y per_page deben ser números enteros'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"❌ Error en búsqueda de productos: {str(e)}")
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_woocommerce_products_local(request):
    """
    Obtener productos desde la base de datos local (OPTIMIZADO).
    
    Query params:
    - category_id: ID de categoría WooCommerce (opcional)
    - per_page: Productos por página (máx 100, default 20)
    - page: Número de página (default 1)
    - lang: Idioma (es/en, también soporta Accept-Language header)
    
    Retorna productos con:
    - Traducciones pre-calculadas
    - Precios con margen aplicado
    - Datos locales (ultra rápido)
    """
    try:
        # Obtener parámetros
        category_id = request.query_params.get('category_id')
        per_page = min(int(request.query_params.get('per_page', 20)), 100)
        page = int(request.query_params.get('page', 1))
        target_lang = get_language_from_request(request)
        
        # Base queryset: solo productos publicados
        queryset = WooCommerceProduct.objects.filter(
            status='publish'
        ).prefetch_related('categories', 'images').select_related()
        
        # Filtrar por categoría si se especifica
        if category_id:
            category_id = int(category_id)
            queryset = queryset.filter(categories__wc_id=category_id)
        
        # Paginación
        total_count = queryset.count()
        start = (page - 1) * per_page
        end = start + per_page
        products_page = queryset[start:end]
        
        # Get currency from request (set by CurrencyMiddleware)
        target_currency = getattr(request, 'currency', 'COP')
        
        # Convertir a lista optimizada con traducciones y conversión de moneda
        products_data = get_products_list(
            queryset=products_page,
            target_language=target_lang,
            include_stock=False,  # Stock se consulta aparte cuando se necesita
            target_currency=target_currency
        )
        
        # Calcular paginación
        total_pages = (total_count + per_page - 1) // per_page
        
        return Response({
            'success': True,
            'message': 'Productos obtenidos desde base de datos local',
            'data': products_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_products': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1
            },
            'filters': {
                'category_id': category_id,
                'language': target_lang
            },
            'source': 'local_db'  # Indicador de que viene de DB local
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({
            'error': 'Parámetros inválidos',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error getting local products: {str(e)}")
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_woocommerce_product_detail_local(request, product_id):
    """
    Obtener detalle completo de un producto desde la base de datos local.
    
    Args:
        product_id: WooCommerce product ID
        
    Query params:
        lang: Idioma (es/en)
        real_time_stock: Si debe consultar stock real de WooCommerce (default: true)
    """
    try:
        target_lang = get_language_from_request(request)
        target_currency = getattr(request, 'currency', 'COP')
        # Por defecto, SÍ consultar stock real en detalle del producto
        real_time_stock = request.query_params.get('real_time_stock', 'true').lower() == 'true'
        
        # Obtener el objeto producto
        product = WooCommerceProduct.objects.filter(wc_id=product_id).first()
        
        # Si el producto no existe localmente, intentar obtenerlo de WooCommerce (dropshipping)
        if not product:
            logger.warning(f"⚠️ Product {product_id} not found locally, fetching from WooCommerce...")
            
            try:
                from ..services.woocommerce_service import woocommerce_service
                from ..utils.currency_converter import CurrencyConverter
                
                # Obtener producto de WooCommerce
                wc_result = woocommerce_service.get_product_by_id(product_id)
                
                if not wc_result.get('success'):
                    return Response({
                        'error': 'Producto no encontrado en WooCommerce',
                        'product_id': product_id,
                        'details': wc_result.get('error')
                    }, status=status.HTTP_404_NOT_FOUND)
                
                wc_product = wc_result.get('data', {})
                
                # Construir respuesta básica desde datos de WooCommerce
                # Aplicar margen si existe (usar default margin)
                from ..models import DefaultPriceMargin
                default_margin = DefaultPriceMargin.get_active()
                
                base_price = float(wc_product.get('price', 0))
                if default_margin and base_price > 0:
                    margin_multiplier = 1 + (default_margin.margin_percentage / 100)
                    final_price = round(base_price * margin_multiplier, 2)
                    margin_applied = f"Default: +{default_margin.margin_percentage:.2f}%"
                else:
                    final_price = base_price
                    margin_applied = None
                
                # Convertir a moneda solicitada
                final_price = CurrencyConverter.convert_price(final_price, target_currency)
                
                product_data = {
                    'id': wc_product.get('id'),
                    'name': wc_product.get('name'),
                    'slug': wc_product.get('slug'),
                    'type': wc_product.get('type'),
                    'description': wc_product.get('description', ''),
                    'short_description': wc_product.get('short_description', ''),
                    'price': final_price,
                    'regular_price': final_price,
                    'sale_price': None,
                    'converted_price': final_price,
                    'converted_regular_price': final_price,
                    'currency': target_currency,
                    'on_sale': False,
                    'stock_status': wc_product.get('stock_status', 'instock'),
                    'stock_quantity': wc_product.get('stock_quantity'),
                    'in_stock': wc_product.get('stock_status') == 'instock',
                    'images': wc_product.get('images', []),
                    'categories': wc_product.get('categories', []),
                    'is_dropshipping': True,  # Indicador de que es dropshipping
                    'margin_applied': margin_applied,
                    'source': 'woocommerce_direct'  # Indicador de origen
                }
                
                logger.info(f"✅ Dropshipping product {product_id} fetched from WooCommerce")
                
                return Response({
                    'success': True,
                    'data': product_data,
                    'source': 'woocommerce_direct'
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                logger.error(f"❌ Error fetching dropshipping product {product_id}: {str(e)}")
                return Response({
                    'error': 'Producto no encontrado',
                    'product_id': product_id,
                    'details': str(e)
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener producto completo con traducciones y conversión de moneda
        product_data = get_product_full_data(
            product=product_id,
            target_language=target_lang,
            include_stock=False,  # Siempre false aquí, lo consultamos aparte
            target_currency=target_currency
        )
        
        # Si se requiere stock en tiempo real, consultarlo de WooCommerce
        if real_time_stock:
            try:
                from ..services.woocommerce_service import woocommerce_service
                
                # Para productos VARIABLES, actualizar stock de CADA VARIACIÓN
                if product.is_variable and 'available_variations' in product_data:
                    for variation_data in product_data['available_variations']:
                        try:
                            stock_result = woocommerce_service.get_product_variation_by_id(
                                product_id,
                                variation_data['id']
                            )
                            
                            if stock_result.get('success') and stock_result.get('data'):
                                stock = stock_result['data']
                                variation_data['stock_status'] = stock.get('stock_status', 'outofstock')
                                variation_data['stock_quantity'] = stock.get('stock_quantity')
                                variation_data['in_stock'] = stock.get('stock_status') == 'instock'
                        except Exception as e:
                            logger.error(f"Error fetching stock for variation {variation_data['id']}: {str(e)}")
                    
                    product_data['real_time_stock'] = True
                    
                # Para productos SIMPLES, actualizar stock del producto
                else:
                    stock_result = woocommerce_service.get_product_by_id(product_id)
                    
                    if stock_result.get('success') and stock_result.get('data'):
                        stock_data = stock_result['data']
                        product_data['stock_status'] = stock_data.get('stock_status', 'outofstock')
                        product_data['stock_quantity'] = stock_data.get('stock_quantity')
                        product_data['manage_stock'] = stock_data.get('manage_stock', False)
                        product_data['in_stock'] = stock_data.get('stock_status') == 'instock'
                        product_data['real_time_stock'] = True
                    else:
                        product_data['real_time_stock'] = False
                        logger.warning(f"Failed to get real-time stock for product {product_id}, using cached data")
                        
            except Exception as e:
                logger.error(f"Error fetching real-time stock for product {product_id}: {str(e)}")
                product_data['real_time_stock'] = False
        else:
            product_data['real_time_stock'] = False
        
        return Response({
            'success': True,
            'data': product_data,
            'language': target_lang,
            'source': 'local_db_with_realtime_stock' if real_time_stock else 'local_db'
        }, status=status.HTTP_200_OK)
        
    except WooCommerceProduct.DoesNotExist:
        return Response({
            'error': 'Producto no encontrado',
            'product_id': product_id
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting product detail: {str(e)}")
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_stock_local(request, product_id):
    """
    Obtener SOLO el stock de un producto en tiempo real desde WooCommerce.
    Endpoint ligero y rápido para verificar disponibilidad.
    
    Args:
        product_id: WooCommerce product ID
        
    Query params:
        real_time: Consultar WooCommerce (default: true) o usar datos locales (false)
    """
    try:
        # Verificar que el producto existe
        product = WooCommerceProduct.objects.filter(wc_id=product_id).first()
        if not product:
            return Response({
                'error': 'Producto no encontrado',
                'product_id': product_id
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Si es producto variable, retornar info de que debe consultar variaciones
        if product.is_variable:
            variations_count = product.variations.filter(status='publish').count()
            return Response({
                'success': True,
                'product_id': product_id,
                'product_type': 'variable',
                'message': 'Este producto tiene variaciones. Consulta el stock de cada variación.',
                'variations_count': variations_count,
                'variations_endpoint': f'/api/products/woocommerce/products/{product_id}/variations/',
                'stock': {
                    'status': 'variable',
                    'requires_variation_selection': True,
                    'manage_stock': False,
                    'available': variations_count > 0,
                }
            }, status=status.HTTP_200_OK)
        
        # Por defecto, consultar stock real para productos simples
        real_time = request.query_params.get('real_time', 'true').lower() == 'true'
        
        if real_time:
            # Consultar stock en tiempo real de WooCommerce
            try:
                from ..services.woocommerce_service import woocommerce_service
                stock_result = woocommerce_service.get_product_by_id(product_id)
                
                if stock_result.get('success') and stock_result.get('data'):
                    stock_data = stock_result['data']
                    return Response({
                        'success': True,
                        'product_id': product_id,
                        'stock': {
                            'status': stock_data.get('stock_status', 'outofstock'),
                            'quantity': stock_data.get('stock_quantity'),
                            'manage_stock': stock_data.get('manage_stock', False),
                            'in_stock': stock_data.get('stock_status') == 'instock',
                            'backorders_allowed': stock_data.get('backorders_allowed', False),
                            'available': stock_data.get('stock_status') == 'instock',
                        },
                        'source': 'woocommerce_realtime',
                        'timestamp': stock_result.get('timestamp')
                    }, status=status.HTTP_200_OK)
                else:
                    # Si falla, usar datos locales
                    logger.warning(f"Failed to get real-time stock for product {product_id}, using cached data")
                    return Response({
                        'success': True,
                        'product_id': product_id,
                        'stock': {
                            'status': product.stock_status,
                            'quantity': product.stock_quantity,
                            'manage_stock': product.manage_stock,
                            'in_stock': product.stock_status == 'instock',
                            'backorders_allowed': False,
                            'available': product.stock_status == 'instock',
                        },
                        'source': 'local_db_fallback',
                        'warning': 'Could not fetch real-time stock, using cached data'
                    }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error fetching real-time stock for product {product_id}: {str(e)}")
                # Fallback a datos locales
                return Response({
                    'success': True,
                    'product_id': product_id,
                    'stock': {
                        'status': product.stock_status,
                        'quantity': product.stock_quantity,
                        'manage_stock': product.manage_stock,
                        'in_stock': product.stock_status == 'instock',
                        'backorders_allowed': False,
                        'available': product.stock_status == 'instock',
                    },
                    'source': 'local_db_fallback',
                    'error': str(e)
                }, status=status.HTTP_200_OK)
        else:
            # Usar datos locales (más rápido)
            return Response({
                'success': True,
                'product_id': product_id,
                'stock': {
                    'status': product.stock_status,
                    'quantity': product.stock_quantity,
                    'manage_stock': product.manage_stock,
                    'in_stock': product.stock_status == 'instock',
                    'backorders_allowed': False,
                    'available': product.stock_status == 'instock',
                },
                'source': 'local_db'
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Error getting product stock: {str(e)}")
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_trending_products_local(request):
    """
    Obtener productos en tendencia (top 8 con mejor rating y más reviews).
    Usa base de datos local.
    """
    try:
        target_lang = get_language_from_request(request)
        target_currency = getattr(request, 'currency', 'COP')
        
        # Obtener productos publicados ordenados por rating y reviews
        queryset = WooCommerceProduct.objects.filter(
            status='publish',
            stock_status='instock'  # Solo con stock
        ).order_by('-rating_count', '-average_rating')[:8]
        
        products_data = get_products_list(
            queryset=queryset,
            target_language=target_lang,
            include_stock=False,
            target_currency=target_currency
        )
        
        return Response({
            'success': True,
            'data': products_data,
            'count': len(products_data),
            'currency': target_currency,
            'source': 'local_db'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting trending products: {str(e)}")
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_variations_local(request, product_id):
    """
    Obtener variaciones de un producto desde la base de datos local.
    
    Args:
        product_id: WooCommerce product ID
        
    Query params:
        per_page: Variaciones por página (máx 100, default 20)
        page: Número de página (default 1)
    """
    try:
        per_page = min(int(request.query_params.get('per_page', 20)), 100)
        page = int(request.query_params.get('page', 1))
        target_lang = get_language_from_request(request)
        
        # Verificar que el producto existe
        product = WooCommerceProduct.objects.filter(wc_id=product_id).first()
        if not product:
            return Response({
                'error': 'Producto no encontrado',
                'product_id': product_id
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener variaciones
        variations_qs = WooCommerceProductVariation.objects.filter(
            wc_product_id=product_id,
            status='publish'
        ).order_by('id')
        
        total_count = variations_qs.count()
        start = (page - 1) * per_page
        end = start + per_page
        variations = variations_qs[start:end]
        
        # Formatear variaciones
        variations_data = []
        for var in variations:
            # Aplicar margen de precio
            from ..utils.translation_helpers import calculate_product_price
            prices = calculate_product_price(product)  # Usar precios del producto padre
            
            variations_data.append({
                'id': var.wc_id,
                'product_id': var.wc_product_id,
                'permalink': var.permalink,
                'price': float(var.price) if var.price else None,
                'regular_price': float(var.regular_price) if var.regular_price else None,
                'sale_price': float(var.sale_price) if var.sale_price else None,
                'on_sale': var.on_sale,
                'stock_status': var.stock_status,
                'stock_quantity': var.stock_quantity,
                'manage_stock': var.manage_stock,
                'attributes': var.attributes,
                'image': var.image_url if var.image_url else None,
                'weight': var.weight,
                'dimensions': {
                    'length': var.length,
                    'width': var.width,
                    'height': var.height
                }
            })
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return Response({
            'success': True,
            'data': variations_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_variations': total_count,
                'total_pages': total_pages
            },
            'source': 'local_db'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting product variations: {str(e)}")
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_variation_detail_local(request, product_id, variation_id):
    """
    Obtener detalle de una variación específica de un producto.
    
    Args:
        product_id: WooCommerce product ID
        variation_id: WooCommerce variation ID
        
    Query params:
        lang: Idioma (es/en)
        real_time_stock: Consultar stock real de WooCommerce (default: true)
    """
    try:
        target_lang = get_language_from_request(request)
        real_time_stock = request.query_params.get('real_time_stock', 'true').lower() == 'true'
        
        # Verificar que el producto padre existe
        product = WooCommerceProduct.objects.filter(wc_id=product_id).first()
        if not product:
            return Response({
                'error': 'Producto no encontrado',
                'product_id': product_id
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener la variación
        variation = WooCommerceProductVariation.objects.filter(
            wc_id=variation_id,
            wc_product_id=product_id
        ).first()
        
        if not variation:
            return Response({
                'error': 'Variación no encontrada',
                'product_id': product_id,
                'variation_id': variation_id
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener información traducida del producto padre
        from ..utils.translation_helpers import get_translated_product, calculate_product_price
        product_translated = get_translated_product(product, target_lang)
        
        # Get currency from request
        target_currency = getattr(request, 'currency', 'COP')
        
        # Calcular margen del producto padre (se aplica a la variación)
        # Las variaciones heredan el margen de la categoría del producto padre
        margin_info = calculate_product_price(product, target_currency)
        
        # Aplicar el margen a los precios de la variación
        def apply_margin_to_variation_price(base_price, margin_info):
            """Aplica el mismo margen del producto padre al precio de la variación"""
            if not base_price:
                return None
            
            # Extract margin percentage from string (e.g., "Aceites Para Masajes: +30.00%" -> 30.0)
            margin_percentage = None
            if margin_info.get('margin_applied'):
                try:
                    import re
                    match = re.search(r'[+-]?(\d+(?:\.\d+)?)', str(margin_info['margin_applied']))
                    if match:
                        margin_percentage = float(match.group(1))
                except (ValueError, AttributeError):
                    margin_percentage = None
            
            # Apply margin if exists
            if margin_percentage:
                margin_multiplier = 1 + (margin_percentage / 100)
                final_price = round(float(base_price) * margin_multiplier, 2)
            else:
                final_price = float(base_price)
            
            # Convert to target currency
            from ..utils.currency_converter import CurrencyConverter
            converted_price = CurrencyConverter.convert_price(final_price, target_currency)
            return converted_price
        
        # Obtener categorías del producto padre (traducidas)
        categories = []
        for cat in product.categories.all():
            from ..utils.translation_helpers import get_translated_category
            cat_translated = get_translated_category(cat, target_lang)
            categories.append({
                'id': cat.wc_id,
                'name': cat_translated['name'],
                'slug': cat.slug
            })
        
        # Obtener imágenes (prioritizar imagen de variación, luego imágenes del producto)
        images = []
        
        # Si la variación tiene imagen específica, usarla primero
        if variation.image_url:
            images.append({
                'id': variation.wc_id,
                'src': variation.image_url,
                'name': f"{product.name} - {variation.get_attribute_description()}",
                'alt': product_translated['name'],
                'thumbnail': variation.image_url,
                'is_variation_image': True
            })
        
        # Agregar imágenes del producto padre
        for img in product.images.all().order_by('position'):
            images.append({
                'id': img.wc_id,
                'src': img.src,
                'name': img.name or '',
                'alt': img.alt or product_translated['name'],
                'thumbnail': img.thumbnail or img.src,
                'is_variation_image': False
            })
        
        # Construir respuesta completa con datos locales
        converted_price = apply_margin_to_variation_price(variation.price, margin_info)
        converted_regular_price = apply_margin_to_variation_price(variation.regular_price, margin_info)
        converted_sale_price = apply_margin_to_variation_price(variation.sale_price, margin_info)
        
        variation_data = {
            'id': variation.wc_id,
            'product_id': variation.wc_product_id,
            'product_name': product_translated['name'],
            'product_slug': product.slug,
            'permalink': variation.permalink,
            'description': product_translated['description'],  # Del producto padre
            'short_description': product_translated['short_description'],  # Del producto padre
            'price': converted_price,
            'regular_price': converted_regular_price,
            'sale_price': converted_sale_price,
            'converted_price': converted_price,
            'converted_regular_price': converted_regular_price,
            'currency': target_currency,
            'on_sale': variation.on_sale,
            'margin_applied': margin_info.get('margin_applied'),  # Indicador del margen aplicado
            'stock_status': variation.stock_status,
            'stock_quantity': variation.stock_quantity,
            'manage_stock': variation.manage_stock,
            'in_stock': variation.stock_status == 'instock',
            'attributes': variation.attributes,
            'attribute_summary': variation.get_attribute_description(),  # "Color: Rojo, Tamaño: M"
            'image': variation.image_url if variation.image_url else (images[0]['src'] if images else None),
            'images': images,  # Array completo de imágenes
            'categories': categories,
            'weight': variation.weight,
            'dimensions': {
                'length': variation.length,
                'width': variation.width,
                'height': variation.height
            },
            'average_rating': float(product.average_rating),
            'rating_count': product.rating_count,
            'featured': product.featured
        }
        
        # Si se requiere stock en tiempo real, consultarlo
        if real_time_stock:
            try:
                from ..services.woocommerce_service import woocommerce_service
                stock_result = woocommerce_service.get_product_variation_by_id(
                    product_id,
                    variation_id
                )
                
                if stock_result.get('success') and stock_result.get('data'):
                    stock_data = stock_result['data']
                    # Actualizar con stock real
                    variation_data['stock_status'] = stock_data.get('stock_status', 'outofstock')
                    variation_data['stock_quantity'] = stock_data.get('stock_quantity')
                    variation_data['manage_stock'] = stock_data.get('manage_stock', False)
                    variation_data['in_stock'] = stock_data.get('stock_status') == 'instock'
                    variation_data['real_time_stock'] = True
                else:
                    variation_data['real_time_stock'] = False
                    logger.warning(f"Failed to get real-time stock for variation {variation_id}")
            except Exception as e:
                logger.error(f"Error fetching real-time stock for variation {variation_id}: {str(e)}")
                variation_data['real_time_stock'] = False
        else:
            variation_data['real_time_stock'] = False
        
        return Response({
            'success': True,
            'data': variation_data,
            'language': target_lang,
            'source': 'local_db_with_realtime_stock' if real_time_stock else 'local_db'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting variation detail: {str(e)}")
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_woocommerce_categories_local(request):
    """
    Obtener categorías desde la base de datos local con traducciones.
    
    Query params:
        per_page: Categorías por página (default 100)
        page: Número de página (default 1)
        parent: ID del padre (0 para raíz, opcional)
        lang: Idioma (es/en)
    """
    try:
        per_page = min(int(request.query_params.get('per_page', 100)), 100)
        page = int(request.query_params.get('page', 1))
        parent_id = request.query_params.get('parent')
        target_lang = get_language_from_request(request)
        
        # Base queryset
        queryset = WooCommerceCategory.objects.all()
        
        # Filtrar por parent si se especifica
        if parent_id is not None:
            parent_id = int(parent_id)
            queryset = queryset.filter(wc_parent_id=parent_id)
        
        # Ordenar por nombre
        queryset = queryset.order_by('name')
        
        # Paginación
        total_count = queryset.count()
        start = (page - 1) * per_page
        end = start + per_page
        categories_page = queryset[start:end]
        
        # Formatear categorías con traducciones
        categories_data = []
        for category in categories_page:
            cat_translated = get_translated_category(category, target_lang)
            
            categories_data.append({
                'id': category.wc_id,
                'name': cat_translated['name'],
                'slug': category.slug,
                'parent': category.wc_parent_id,
                'description': cat_translated['description'],
                'count': category.product_count,
                'image': category.image_url if category.image_url else None
            })
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return Response({
            'success': True,
            'data': categories_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_categories': total_count,
                'total_pages': total_pages
            },
            'language': target_lang,
            'source': 'local_db'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting local categories: {str(e)}")
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_woocommerce_stats_local(request):
    """
    Obtener estadísticas globales de productos y categorías.
    Usa base de datos local para respuestas rápidas.
    """
    try:
        target_lang = get_language_from_request(request)
        
        # Contar productos y categorías
        total_products = WooCommerceProduct.objects.filter(status='publish').count()
        total_categories = WooCommerceCategory.objects.count()
        products_in_stock = WooCommerceProduct.objects.filter(
            status='publish',
            stock_status='instock'
        ).count()
        products_on_sale = WooCommerceProduct.objects.filter(
            status='publish',
            on_sale=True
        ).count()
        
        # Top categorías por cantidad de productos
        top_categories = WooCommerceCategory.objects.filter(
            product_count__gt=0
        ).order_by('-product_count')[:10]
        
        top_categories_data = []
        for cat in top_categories:
            cat_translated = get_translated_category(cat, target_lang)
            top_categories_data.append({
                'id': cat.wc_id,
                'name': cat_translated['name'],
                'slug': cat.slug,
                'product_count': cat.product_count
            })
        
        return Response({
            'success': True,
            'data': {
                'total_products': total_products,
                'total_categories': total_categories,
                'products_in_stock': products_in_stock,
                'products_on_sale': products_on_sale,
                'top_categories': top_categories_data
            },
            'language': target_lang,
            'source': 'local_db'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return Response({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_organized_categories_local(request):
    """
    Obtener categorías organizadas por temas desde la base de datos local.
    
    Devuelve las categorías agrupadas en 7 temas principales:
    - 🎮 Juguetes
    - 👗 Lencería
    - 💧 Lubricantes
    - ⛓️ Bondage
    - 🌿 Bienestar
    - 🏷️ Marcas
    - 💰 Ofertas
    """
    try:
        target_lang = get_language_from_request(request)
        
        # Obtener todas las categorías de la DB local
        all_categories = WooCommerceCategory.objects.all()
        
        # Definir las categorías por tema
        themes = {
            'juguetes': {
                'name': 'Juguetes',
                'icon': '🎮',
                'slug': 'juguetes',
                'main_categories': [134],
                'related_categories': [223, 329, 222, 215, 195, 378, 200, 239],
                'categories': []
            },
            'lenceria': {
                'name': 'Lencería',
                'icon': '👗',
                'slug': 'lenceria',
                'main_categories': [246, 352],
                'related_categories': [402, 214, 359],
                'categories': []
            },
            'lubricantes': {
                'name': 'Lubricantes y Cosmética',
                'icon': '💧',
                'slug': 'lubricantes',
                'main_categories': [136],
                'related_categories': [250, 255, 256, 249, 389, 251],
                'categories': []
            },
            'bondage': {
                'name': 'Bondage',
                'icon': '⛓️',
                'slug': 'bondage',
                'main_categories': [137],
                'related_categories': [190, 383],
                'categories': []
            },
            'bienestar': {
                'name': 'Bienestar Sexual',
                'icon': '🌿',
                'slug': 'bienestar',
                'main_categories': [531],
                'related_categories': [193, 227],
                'categories': []
            },
            'marcas': {
                'name': 'Marcas',
                'icon': '🏷️',
                'slug': 'marcas',
                'main_categories': [546, 539, 550],
                'related_categories': [553, 542, 555, 612, 547],
                'categories': []
            },
            'ofertas': {
                'name': 'Ofertas y Descuentos',
                'icon': '💰',
                'slug': 'ofertas',
                'main_categories': [695],
                'related_categories': [],
                'categories': [],
                'has_subcategories': True
            }
        }
        
        # Crear diccionario para búsqueda rápida
        category_map = {cat.wc_id: cat for cat in all_categories}
        
        # Organizar categorías en temas
        for theme_key, theme_data in themes.items():
            all_category_ids = theme_data['main_categories'] + theme_data['related_categories']
            
            for cat_id in all_category_ids:
                if cat_id in category_map:
                    cat = category_map[cat_id]
                    cat_translated = get_translated_category(cat, target_lang)
                    
                    # Buscar subcategorías
                    subcategories = []
                    for sub in all_categories:
                        if sub.wc_parent_id == cat_id:
                            sub_translated = get_translated_category(sub, target_lang)
                            subcategories.append({
                                'id': sub.wc_id,
                                'name': sub_translated['name'],
                                'slug': sub.slug,
                                'count': sub.product_count
                            })
                    
                    theme_data['categories'].append({
                        'id': cat.wc_id,
                        'name': cat_translated['name'],
                        'slug': cat.slug,
                        'count': cat.product_count,
                        'is_main': cat_id in theme_data['main_categories'],
                        'has_subcategories': len(subcategories) > 0,
                        'subcategories': subcategories
                    })
        
        # Preparar respuesta con totales
        result = []
        for theme_key, theme_data in themes.items():
            total_products = sum(cat['count'] for cat in theme_data['categories'])
            
            result.append({
                'theme': theme_key,
                'name': theme_data['name'],
                'icon': theme_data['icon'],
                'slug': theme_data['slug'],
                'total_products': total_products,
                'total_categories': len(theme_data['categories']),
                'has_subcategories': theme_data.get('has_subcategories', False),
                'categories': theme_data['categories']
            })
        
        return Response({
            'success': True,
            'message': 'Categorías organizadas exitosamente',
            'data': result,
            'total_categories': all_categories.count(),
            'language': target_lang,
            'source': 'local_db'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error organizing categories: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_category_tree_local(request):
    """
    Obtener árbol completo de categorías con jerarquía desde la base de datos local.
    """
    try:
        target_lang = get_language_from_request(request)
        
        # Obtener todas las categorías
        all_categories = WooCommerceCategory.objects.all().order_by('display_order', 'name')
        
        # Crear mapa de categorías
        category_map = {}
        for cat in all_categories:
            cat_translated = get_translated_category(cat, target_lang)
            category_map[cat.wc_id] = {
                'id': cat.wc_id,
                'name': cat_translated['name'],
                'slug': cat.slug,
                'count': cat.product_count,
                'parent': cat.wc_parent_id,
                'children': []
            }
        
        # Construir árbol
        tree = []
        for cat in all_categories:
            if cat.wc_parent_id == 0:
                # Es categoría principal
                tree.append(category_map[cat.wc_id])
            else:
                # Es subcategoría
                if cat.wc_parent_id in category_map:
                    category_map[cat.wc_parent_id]['children'].append(category_map[cat.wc_id])
        
        return Response({
            'success': True,
            'data': tree,
            'total': all_categories.count(),
            'language': target_lang,
            'source': 'local_db'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error building category tree: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_random_featured_categories_local(request):
    """
    Obtener 4 categorías destacadas aleatorias con imagen del primer producto.
    Usa base de datos local para respuestas rápidas.
    """
    try:
        target_lang = get_language_from_request(request)
        
        # Definir las categorías principales
        main_themes = [
            {'name': 'Juguetes', 'slug': 'juguetes', 'icon': '🎮', 'category_id': 134},
            {'name': 'Lencería', 'slug': 'lenceria', 'icon': '👗', 'category_id': 246},
            {'name': 'Lubricantes y Cosmética', 'slug': 'lubricantes', 'icon': '💧', 'category_id': 136},
            {'name': 'Bondage', 'slug': 'bondage', 'icon': '⛓️', 'category_id': 137},
            {'name': 'Bienestar Sexual', 'slug': 'bienestar', 'icon': '🌿', 'category_id': 531},
            {'name': 'Marcas', 'slug': 'marcas', 'icon': '🏷️', 'category_id': 546},
            {'name': 'Ofertas y Descuentos', 'slug': 'ofertas', 'icon': '💰', 'category_id': 695}
        ]
        
        # Seleccionar 4 aleatorias
        selected_themes = random.sample(main_themes, min(4, len(main_themes)))
        
        featured_categories = []
        
        for theme in selected_themes:
            # Obtener primer producto de la categoría
            first_product = WooCommerceProduct.objects.filter(
                categories__wc_id=theme['category_id'],
                status='publish'
            ).prefetch_related('images').first()
            
            # Obtener imagen del producto
            first_product_image = None
            if first_product and first_product.images.exists():
                first_product_image = first_product.images.first().src
            
            # Traducir nombre si es necesario
            theme_name = theme['name']
            if target_lang != 'es':
                try:
                    # Intentar obtener traducción del caché
                    category = WooCommerceCategory.objects.filter(wc_id=theme['category_id']).first()
                    if category:
                        cat_translated = get_translated_category(category, target_lang)
                        theme_name = cat_translated['name']
                except:
                    pass
            
            featured_categories.append({
                'name': theme_name,
                'slug': theme['slug'],
                'icon': theme['icon'],
                'category_id': theme['category_id'],
                'first_product_image': first_product_image
            })
        
        return Response({
            'success': True,
            'message': '4 categorías destacadas obtenidas exitosamente',
            'data': featured_categories,
            'total_selected': len(featured_categories),
            'language': target_lang,
            'source': 'local_db'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting featured categories: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
