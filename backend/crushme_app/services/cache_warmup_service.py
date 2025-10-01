"""
Cache Warmup Service for WooCommerce Integration
Automatically refreshes cache before expiration to prevent slow responses
"""
import logging
from django.core.cache import cache
from .woocommerce_service import woocommerce_service

logger = logging.getLogger(__name__)


def warmup_categories_cache():
    """
    Pre-calentar caché de categorías
    Se ejecuta automáticamente cada 50 minutos (antes de que expire el caché de 1 hora)
    """
    try:
        logger.info("🔥 Starting cache warmup for categories...")
        
        # Obtener categorías frescas de WooCommerce (sin usar caché)
        result = woocommerce_service.get_categories(per_page=100, use_cache=False)
        
        if result['success']:
            # Guardar en caché manualmente
            cache_key = 'woocommerce_categories_100_1'
            cache.set(cache_key, result, timeout=3600)
            
            logger.info(f"✅ Categories cache warmed up successfully ({len(result['data'])} categories)")
            return True
        else:
            logger.error(f"❌ Failed to warmup categories cache: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error warming up categories cache: {str(e)}")
        return False


def warmup_organized_categories_cache():
    """
    Pre-calentar caché de categorías organizadas
    """
    try:
        logger.info("🔥 Starting cache warmup for organized categories...")
        
        # Importar aquí para evitar circular imports
        from ..views.category_views import organize_categories_by_theme
        
        # Obtener categorías
        result = woocommerce_service.get_categories(per_page=100, use_cache=True)
        
        if result['success']:
            categories = result['data']
            
            # Organizar por temas
            organized = organize_categories_by_theme(categories)
            
            # Preparar respuesta
            response_data = {
                'success': True,
                'message': 'Categorías organizadas exitosamente',
                'data': organized,
                'total_categories': len(categories),
                'cached': False
            }
            
            # Guardar en caché
            cache_key = 'woocommerce_organized_categories'
            cache.set(cache_key, response_data, timeout=3600)
            
            logger.info("✅ Organized categories cache warmed up successfully")
            return True
        else:
            logger.error(f"❌ Failed to warmup organized categories: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error warming up organized categories cache: {str(e)}")
        return False


def warmup_stats_cache():
    """
    Pre-calentar caché de estadísticas
    """
    try:
        logger.info("🔥 Starting cache warmup for stats...")
        
        # Importar aquí para evitar circular imports
        from ..views.category_views import organize_categories_by_theme
        
        # Obtener categorías
        result = woocommerce_service.get_categories(per_page=100, use_cache=True)
        
        if result['success']:
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
                },
                'cached': False
            }
            
            # Guardar en caché
            cache_key = 'woocommerce_stats'
            cache.set(cache_key, response_data, timeout=3600)
            
            logger.info("✅ Stats cache warmed up successfully")
            return True
        else:
            logger.error(f"❌ Failed to warmup stats: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error warming up stats cache: {str(e)}")
        return False


def warmup_products_cache():
    """
    Pre-calentar caché de productos - ESCENARIO 1
    
    Configuración:
    - 3 categorías top
    - 20 productos por categoría
    - Total: 60 productos
    - Memoria: ~1.2 MB
    """
    try:
        logger.info("🔥 Starting cache warmup for products...")
        
        # Top 3 categorías más visitadas
        popular_categories = [134, 246, 352]  # Juguetes, Lencería Para Ella, Lencería
        products_per_category = 20  # Escenario 1: 20 productos por categoría
        
        for cat_id in popular_categories:
            result = woocommerce_service.get_products(
                category_id=cat_id,
                per_page=products_per_category,
                page=1
            )
            
            if result['success']:
                # Guardar en caché manualmente
                cache_key = f'woocommerce_products_{cat_id}_{products_per_category}_1'
                cache.set(cache_key, result, timeout=3600)
                logger.info(f"  ✅ Products cached for category {cat_id} ({products_per_category} products)")
            else:
                logger.error(f"  ❌ Failed to cache products for category {cat_id}")
        
        total_products = len(popular_categories) * products_per_category
        logger.info(f"✅ Products cache warmup completed: {len(popular_categories)} categories × {products_per_category} = {total_products} products")
        logger.info(f"   Memory usage: ~1.2 MB")
        return True
            
    except Exception as e:
        logger.error(f"❌ Error warming up products cache: {str(e)}")
        return False


def warmup_all_cache():
    """
    Pre-calentar TODO el caché
    Esta función se ejecuta automáticamente cada 50 minutos
    """
    logger.info("=" * 80)
    logger.info("🔥 STARTING AUTOMATIC CACHE WARMUP")
    logger.info("=" * 80)
    
    results = {
        'categories': warmup_categories_cache(),
        'organized_categories': warmup_organized_categories_cache(),
        'stats': warmup_stats_cache(),
        'products': warmup_products_cache()
    }
    
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    logger.info("=" * 80)
    logger.info(f"✅ CACHE WARMUP COMPLETED: {success_count}/{total_count} successful")
    logger.info("=" * 80)
    
    return results

