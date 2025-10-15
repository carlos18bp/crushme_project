"""
Category organization views for WooCommerce integration
Provides organized category structure for frontend
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import logging

from ..services.woocommerce_service import woocommerce_service
from ..services.translation_service import create_translator_from_request

logger = logging.getLogger(__name__)


def translate_category_names(data, translator):
    """Traduce nombres de categorías recursivamente"""
    if not data:
        return data
    
    if isinstance(data, dict):
        if 'name' in data:
            data['name'] = translator.translate_if_needed(data['name'], content_language='es')
        for key, value in data.items():
            data[key] = translate_category_names(value, translator)
    elif isinstance(data, list):
        return [translate_category_names(item, translator) for item in data]
    
    return data


@api_view(['GET'])
@permission_classes([AllowAny])
def get_organized_categories(request):
    """
    Obtener categorías organizadas por temas para el frontend
    
    Devuelve las categorías agrupadas en 6 temas principales:
    - Juguetes
    - Lencería
    - Lubricantes
    - Bondage
    - Bienestar
    - Marcas
    - Ofertas
    """
    try:
        logger.info("🔄 Organizing categories from WooCommerce...")
        
        # Obtener todas las categorías de WooCommerce
        result = woocommerce_service.get_categories(per_page=100)
        
        if not result['success']:
            return Response({
                'success': False,
                'error': 'Error obteniendo categorías de WooCommerce',
                'details': result.get('error')
            }, status=status.HTTP_502_BAD_GATEWAY)
        
        all_categories = result['data']
        
        # Organizar por temas
        organized = organize_categories_by_theme(all_categories)
        
        # Traducir nombres de categorías y temas
        translator = create_translator_from_request(request)
        if translator.target_language != 'es':
            organized = translate_category_names(organized, translator)
        
        # Preparar respuesta
        response_data = {
            'success': True,
            'message': 'Categorías organizadas exitosamente',
            'data': organized,
            'total_categories': len(all_categories)
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error organizing categories: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def organize_categories_by_theme(categories):
    """
    Organiza las categorías en temas predefinidos
    """
    
    # Definir las categorías por tema
    themes = {
        'juguetes': {
            'name': 'Juguetes',
            'icon': '🎮',
            'slug': 'juguetes',
            'main_categories': [134],  # Juguetes principal
            'related_categories': [223, 329, 222, 215, 195, 378, 200, 239],
            'categories': []
        },
        'lenceria': {
            'name': 'Lencería',
            'icon': '👗',
            'slug': 'lenceria',
            'main_categories': [246, 352],  # Lencería Para Ella, Lencería
            'related_categories': [402, 214, 359],
            'categories': []
        },
        'lubricantes': {
            'name': 'Lubricantes y Cosmética',
            'icon': '💧',
            'slug': 'lubricantes',
            'main_categories': [136],  # Lubricantes y cosmética
            'related_categories': [250, 255, 256, 249, 389, 251],
            'categories': []
        },
        'bondage': {
            'name': 'Bondage',
            'icon': '⛓️',
            'slug': 'bondage',
            'main_categories': [137],  # Bondage
            'related_categories': [190, 383],
            'categories': []
        },
        'bienestar': {
            'name': 'Bienestar Sexual',
            'icon': '🌿',
            'slug': 'bienestar',
            'main_categories': [531],  # Bienestar Sexual
            'related_categories': [193, 227],
            'categories': []
        },
        'marcas': {
            'name': 'Marcas',
            'icon': '🏷️',
            'slug': 'marcas',
            'main_categories': [546, 539, 550],  # CamToyz, DistriSex, Lerot
            'related_categories': [553, 542, 555, 612, 547],
            'categories': []
        },
        'ofertas': {
            'name': 'Ofertas y Descuentos',
            'icon': '💰',
            'slug': 'ofertas',
            'main_categories': [695],  # Liquidacion
            'related_categories': [],
            'categories': [],
            'has_subcategories': True
        }
    }
    
    # Crear un diccionario para búsqueda rápida
    category_map = {cat['id']: cat for cat in categories}
    
    # Organizar categorías en temas
    for theme_key, theme_data in themes.items():
        all_category_ids = theme_data['main_categories'] + theme_data['related_categories']
        
        for cat_id in all_category_ids:
            if cat_id in category_map:
                cat = category_map[cat_id]
                
                # Buscar subcategorías si las tiene
                subcategories = [
                    {
                        'id': sub['id'],
                        'name': sub['name'],
                        'slug': sub['slug'],
                        'count': sub['count']
                    }
                    for sub in categories if sub['parent'] == cat_id
                ]
                
                theme_data['categories'].append({
                    'id': cat['id'],
                    'name': cat['name'],
                    'slug': cat['slug'],
                    'count': cat['count'],
                    'is_main': cat_id in theme_data['main_categories'],
                    'has_subcategories': len(subcategories) > 0,
                    'subcategories': subcategories if subcategories else []
                })
    
    # Calcular totales por tema
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
    
    return result


@api_view(['GET'])
@permission_classes([AllowAny])
def get_category_tree(request):
    """
    Obtener árbol completo de categorías con jerarquía
    """
    try:
        # Obtener todas las categorías
        result = woocommerce_service.get_categories(per_page=100)
        
        if not result['success']:
            return Response({
                'success': False,
                'error': 'Error obteniendo categorías'
            }, status=status.HTTP_502_BAD_GATEWAY)
        
        categories = result['data']
        
        # Construir árbol
        tree = build_category_tree(categories)
        
        # Traducir nombres de categorías
        translator = create_translator_from_request(request)
        if translator.target_language != 'es':
            tree = translate_category_names(tree, translator)
        
        return Response({
            'success': True,
            'data': tree,
            'total': len(categories)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def build_category_tree(categories):
    """
    Construye un árbol jerárquico de categorías
    """
    # Crear mapa de categorías
    category_map = {}
    for cat in categories:
        category_map[cat['id']] = {
            'id': cat['id'],
            'name': cat['name'],
            'slug': cat['slug'],
            'count': cat['count'],
            'parent': cat['parent'],
            'children': []
        }
    
    # Construir árbol
    tree = []
    for cat in categories:
        if cat['parent'] == 0:
            # Es categoría principal
            tree.append(category_map[cat['id']])
        else:
            # Es subcategoría, agregarla a su padre
            parent_id = cat['parent']
            if parent_id in category_map:
                category_map[parent_id]['children'].append(category_map[cat['id']])
    
    return tree


@api_view(['GET'])
@permission_classes([AllowAny])
def get_products_stats(request):
    """
    Obtener estadísticas generales de productos
    
    Devuelve:
    - Total de productos en WooCommerce
    - Total por categoría
    - Total por tema
    - Categorías más populares
    """
    try:
        logger.info("🔄 Calculating stats from WooCommerce...")
        
        # Obtener categorías
        result = woocommerce_service.get_categories(per_page=100)
        
        if not result['success']:
            return Response({
                'success': False,
                'error': 'Error obteniendo categorías'
            }, status=status.HTTP_502_BAD_GATEWAY)
        
        categories = result['data']
        
        # Calcular totales
        total_products = sum(cat['count'] for cat in categories)
        total_categories = len(categories)
        
        # Organizar por temas
        organized = organize_categories_by_theme(categories)
        
        # Calcular stats por tema
        theme_stats = []
        for theme in organized:
            theme_stats.append({
                'theme': theme['theme'],
                'name': theme['name'],
                'icon': theme['icon'],
                'total_products': theme['total_products'],
                'total_categories': theme['total_categories']
            })
        
        # Top categorías
        top_categories = sorted(categories, key=lambda x: x['count'], reverse=True)[:10]
        top_categories_list = [
            {
                'id': cat['id'],
                'name': cat['name'],
                'slug': cat['slug'],
                'count': cat['count']
            }
            for cat in top_categories
        ]
        
        # Traducir nombres de categorías
        translator = create_translator_from_request(request)
        if translator.target_language != 'es':
            theme_stats = translate_category_names(theme_stats, translator)
            top_categories_list = translate_category_names(top_categories_list, translator)
        
        response_data = {
            'success': True,
            'data': {
                'totals': {
                    'products': total_products,
                    'categories': total_categories,
                    'themes': len(theme_stats)
                },
                'by_theme': theme_stats,
                'top_categories': top_categories_list
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error calculating stats: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_category_stats(request, category_id):
    """
    Obtener estadísticas de una categoría específica

    Devuelve:
    - Información de la categoría
    - Total de productos
    - Subcategorías (si tiene)
    """
    try:
        result = woocommerce_service.get_categories(per_page=100)

        if not result['success']:
            return Response({
                'success': False,
                'error': 'Error obteniendo categorías'
            }, status=status.HTTP_502_BAD_GATEWAY)

        categories = result['data']

        # Buscar la categoría
        category = next((cat for cat in categories if cat['id'] == category_id), None)

        if not category:
            return Response({
                'success': False,
                'error': f'Categoría {category_id} no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)

        # Buscar subcategorías
        subcategories = [cat for cat in categories if cat['parent'] == category_id]

        # Calcular total incluyendo subcategorías
        total_with_subcategories = category['count']
        if subcategories:
            total_with_subcategories += sum(sub['count'] for sub in subcategories)

        # Traducir nombres
        translator = create_translator_from_request(request)
        category_data = {
            'id': category['id'],
            'name': category['name'],
            'slug': category['slug'],
            'count': category['count'],
            'parent': category['parent']
        }
        subcategories_data = [
            {
                'id': sub['id'],
                'name': sub['name'],
                'slug': sub['slug'],
                'count': sub['count']
            }
            for sub in subcategories
        ]

        if translator.target_language != 'es':
            category_data = translate_category_names(category_data, translator)
            subcategories_data = translate_category_names(subcategories_data, translator)

        return Response({
            'success': True,
            'data': {
                'category': category_data,
                'products_count': category['count'],
                'has_subcategories': len(subcategories) > 0,
                'subcategories_count': len(subcategories),
                'total_with_subcategories': total_with_subcategories,
                'subcategories': subcategories_data
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_random_featured_categories(request):
    """
    Obtener 4 categorías aleatorias de las categorías principales con la imagen del primer producto.

    Devuelve:
    - 4 categorías seleccionadas aleatoriamente de las principales.
    - Para cada categoría: nombre, slug, ID y la imagen del primer producto disponible.
    - El slug se puede usar para consultar el endpoint existente: /api/products/category/?category=<slug>
    """
    try:
        # Definir las categorías principales (igual que en organize_categories_by_theme)
        main_themes = [
            {'name': 'Juguetes', 'slug': 'juguetes', 'icon': '🎮', 'main_categories': [134]},
            {'name': 'Lencería', 'slug': 'lenceria', 'icon': '👗', 'main_categories': [246, 352]},
            {'name': 'Lubricantes y Cosmética', 'slug': 'lubricantes', 'icon': '💧', 'main_categories': [136]},
            {'name': 'Bondage', 'slug': 'bondage', 'icon': '⛓️', 'main_categories': [137]},
            {'name': 'Bienestar Sexual', 'slug': 'bienestar', 'icon': '🌿', 'main_categories': [531]},
            {'name': 'Marcas', 'slug': 'marcas', 'icon': '🏷️', 'main_categories': [546, 539, 550]},
            {'name': 'Ofertas y Descuentos', 'slug': 'ofertas', 'icon': '💰', 'main_categories': [695]}
        ]

        # Seleccionar 4 categorías aleatorias
        import random
        selected_themes = random.sample(main_themes, min(4, len(main_themes)))

        featured_categories = []

        for theme in selected_themes:
            # Obtener productos de la primera categoría principal de este tema
            category_id = theme['main_categories'][0]
            products_result = woocommerce_service.get_products(category_id=category_id, per_page=1, page=1)

            # Extraer la imagen del primer producto si está disponible
            first_product_image = None
            if products_result['success'] and products_result['data']:
                first_product = products_result['data'][0]
                images = first_product.get('images', [])
                if images:
                    first_product_image = images[0].get('src', '')  # URL de la imagen principal

            # Construir el objeto de la categoría
            category_data = {
                'name': theme['name'],
                'slug': theme['slug'],  # Este slug se usa para el endpoint existente
                'icon': theme['icon'],
                'category_id': category_id,  # ID de la categoría en WooCommerce
                'first_product_image': first_product_image  # Imagen del primer producto
            }

            featured_categories.append(category_data)

        # Traducir nombres si es necesario (reutilizando la lógica existente)
        translator = create_translator_from_request(request)
        if translator.target_language != 'es':
            for cat in featured_categories:
                cat['name'] = translator.translate_if_needed(cat['name'], content_language='es')

        return Response({
            'success': True,
            'message': '4 categorías destacadas obtenidas exitosamente',
            'data': featured_categories,
            'total_selected': len(featured_categories)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error obteniendo categorías destacadas: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
