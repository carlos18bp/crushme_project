"""
Batch Translation Service
Pre-translates all content for fast delivery
"""
import logging
from django.db import transaction
from django.db.models import Q

from ..models import (
    WooCommerceProduct,
    WooCommerceCategory,
    TranslatedContent
)
from ..utils.html_helpers import (
    strip_html_tags,
    should_strip_html,
    extract_text_from_html
)
from .translation_service import TranslationService

logger = logging.getLogger(__name__)


class TranslationBatchService:
    """
    Servicio para pre-traducir todo el contenido sincronizado.
    Traduce productos y categorías en batch para respuestas rápidas.
    """
    
    TARGET_LANGUAGES = ['en']  # Por ahora solo inglés, español es el original
    
    def __init__(self):
        self.stats = {
            'products_translated': 0,
            'categories_translated': 0,
            'fields_translated': 0,
            'errors': 0,
            'skipped': 0
        }
    
    def translate_all(self, force_retranslate=False):
        """
        Traducir todo el contenido disponible.
        
        Args:
            force_retranslate: Si True, re-traduce incluso contenido ya traducido
            
        Returns:
            dict: Estadísticas de la traducción
        """
        logger.info("🌐 Starting batch translation...")
        
        try:
            # Traducir categorías primero (son menos)
            self._translate_categories(force_retranslate)
            
            # Traducir productos
            self._translate_products(force_retranslate)
            
            logger.info(f"✅ Batch translation completed!")
            logger.info(f"   Products: {self.stats['products_translated']}")
            logger.info(f"   Categories: {self.stats['categories_translated']}")
            logger.info(f"   Total fields: {self.stats['fields_translated']}")
            logger.info(f"   Errors: {self.stats['errors']}")
            logger.info(f"   Skipped: {self.stats['skipped']}")
            
            return {
                'success': True,
                'stats': self.stats
            }
            
        except Exception as e:
            logger.error(f"❌ Batch translation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats
            }
    
    def _translate_categories(self, force_retranslate=False):
        """Traducir todas las categorías"""
        logger.info("📁 Translating categories...")
        
        categories = WooCommerceCategory.objects.all()
        total = categories.count()
        logger.info(f"   Found {total} categories")
        
        for idx, category in enumerate(categories, 1):
            try:
                # Mostrar progreso cada 10 categorías
                if idx % 10 == 0 or idx == total:
                    logger.info(f"   Progress: {idx}/{total} categories")
                
                # Traducir nombre
                self._translate_field(
                    content_type=TranslatedContent.CONTENT_TYPE_CATEGORY_NAME,
                    object_id=category.wc_id,
                    source_text=category.name,
                    force_retranslate=force_retranslate
                )
                
                # Traducir descripción si existe
                if category.description:
                    self._translate_field(
                        content_type=TranslatedContent.CONTENT_TYPE_CATEGORY_DESC,
                        object_id=category.wc_id,
                        source_text=category.description,
                        force_retranslate=force_retranslate
                    )
                
                self.stats['categories_translated'] += 1
                
            except Exception as e:
                logger.error(f"Error translating category {category.wc_id}: {str(e)}")
                self.stats['errors'] += 1
    
    def _translate_products(self, force_retranslate=False):
        """Traducir todos los productos"""
        logger.info("📦 Translating products...")
        
        # Solo productos publicados
        products = WooCommerceProduct.objects.filter(status='publish')
        total = products.count()
        logger.info(f"   Found {total} products")
        
        for idx, product in enumerate(products, 1):
            try:
                # Mostrar progreso cada 50 productos
                if idx % 50 == 0 or idx == total:
                    logger.info(f"   Progress: {idx}/{total} products ({(idx/total*100):.1f}%)")
                
                # Traducir nombre (siempre necesario)
                self._translate_field(
                    content_type=TranslatedContent.CONTENT_TYPE_PRODUCT_NAME,
                    object_id=product.wc_id,
                    source_text=product.name,
                    force_retranslate=force_retranslate
                )
                
                # Traducir descripción corta (importante para listados)
                if product.short_description:
                    self._translate_field(
                        content_type=TranslatedContent.CONTENT_TYPE_PRODUCT_SHORT_DESC,
                        object_id=product.wc_id,
                        source_text=product.short_description,
                        force_retranslate=force_retranslate
                    )
                
                # Traducir descripción completa (para detalle)
                # Solo si no es muy larga (para optimizar tiempo)
                if product.description and len(product.description) < 5000:
                    self._translate_field(
                        content_type=TranslatedContent.CONTENT_TYPE_PRODUCT_DESC,
                        object_id=product.wc_id,
                        source_text=product.description,
                        force_retranslate=force_retranslate
                    )
                elif product.description and len(product.description) >= 5000:
                    logger.debug(f"   Skipping long description for product {product.wc_id}")
                    self.stats['skipped'] += 1
                
                self.stats['products_translated'] += 1
                
            except Exception as e:
                logger.error(f"Error translating product {product.wc_id}: {str(e)}")
                self.stats['errors'] += 1
    
    @transaction.atomic
    def _translate_field(self, content_type, object_id, source_text, force_retranslate=False):
        """
        Traducir un campo específico a todos los idiomas objetivo.
        
        Args:
            content_type: Tipo de contenido
            object_id: ID del objeto (WooCommerce ID)
            source_text: Texto original en español
            force_retranslate: Re-traducir si ya existe
        """
        if not source_text or not source_text.strip():
            return
        
        # Limpiar HTML si es necesario
        text_to_translate = source_text
        if should_strip_html(content_type):
            # Para nombres, quitar TODO el HTML
            text_to_translate = strip_html_tags(source_text)
        else:
            # Para descripciones, extraer solo el texto pero mantener estructura
            clean_text, has_html = extract_text_from_html(source_text)
            if has_html:
                text_to_translate = clean_text
        
        # Si después de limpiar no hay texto, salir
        if not text_to_translate or not text_to_translate.strip():
            return
        
        for target_lang in self.TARGET_LANGUAGES:
            try:
                # Verificar si ya existe traducción
                existing = TranslatedContent.objects.filter(
                    content_type=content_type,
                    object_id=object_id,
                    target_language=target_lang
                ).first()
                
                if existing and not force_retranslate:
                    # Ya existe, saltar
                    continue
                
                # Traducir el texto limpio
                temp_translator = TranslationService(target_language=target_lang)
                translated_text = temp_translator.translate(text_to_translate, source_language='es')
                
                # Guardar o actualizar
                TranslatedContent.objects.update_or_create(
                    content_type=content_type,
                    object_id=object_id,
                    target_language=target_lang,
                    defaults={
                        'source_language': 'es',
                        'source_text': text_to_translate,  # Guardar el texto limpio
                        'translated_text': translated_text,
                        'translation_engine': 'argostranslate'
                    }
                )
                
                self.stats['fields_translated'] += 1
                
            except Exception as e:
                logger.error(f"Error translating field {content_type} #{object_id} to {target_lang}: {str(e)}")
                raise
    
    def translate_product(self, product_id, force_retranslate=False):
        """
        Traducir un producto específico.
        Útil para sincronizaciones incrementales.
        
        Args:
            product_id: WooCommerce product ID
            force_retranslate: Re-traducir si ya existe
        """
        try:
            product = WooCommerceProduct.objects.get(wc_id=product_id)
            
            # Traducir campos
            self._translate_field(
                TranslatedContent.CONTENT_TYPE_PRODUCT_NAME,
                product.wc_id,
                product.name,
                force_retranslate
            )
            
            if product.short_description:
                self._translate_field(
                    TranslatedContent.CONTENT_TYPE_PRODUCT_SHORT_DESC,
                    product.wc_id,
                    product.short_description,
                    force_retranslate
                )
            
            if product.description and len(product.description) < 5000:
                self._translate_field(
                    TranslatedContent.CONTENT_TYPE_PRODUCT_DESC,
                    product.wc_id,
                    product.description,
                    force_retranslate
                )
            
            logger.info(f"✅ Product {product_id} translated successfully")
            return True
            
        except WooCommerceProduct.DoesNotExist:
            logger.error(f"Product {product_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error translating product {product_id}: {str(e)}")
            return False
    
    def get_translated_text(self, content_type, object_id, target_language='en', fallback_text=''):
        """
        Obtener texto traducido desde el caché.
        
        Args:
            content_type: Tipo de contenido
            object_id: WooCommerce ID
            target_language: Idioma objetivo
            fallback_text: Texto a devolver si no existe traducción
            
        Returns:
            Texto traducido o fallback
        """
        try:
            translation = TranslatedContent.objects.get(
                content_type=content_type,
                object_id=object_id,
                target_language=target_language
            )
            return translation.translated_text
        except TranslatedContent.DoesNotExist:
            return fallback_text


# Singleton instance
translation_batch_service = TranslationBatchService()
