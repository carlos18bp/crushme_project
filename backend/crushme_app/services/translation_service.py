"""
Translation Service using argostranslate (100% offline)
Translates text between Spanish and English based on Accept-Language header
"""

import argostranslate.translate
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Service to handle text translation between Spanish and English.
    
    Usage:
        translator = TranslationService(target_language='en')
        translated_text = translator.translate('Hola mundo')
    """
    
    # Supported languages
    SPANISH = 'es'
    ENGLISH = 'en'
    SUPPORTED_LANGUAGES = [SPANISH, ENGLISH]
    
    def __init__(self, target_language: str = 'es'):
        """
        Initialize translator with target language.
        
        Args:
            target_language (str): Target language code ('es' or 'en')
        """
        self.target_language = target_language if target_language in self.SUPPORTED_LANGUAGES else self.SPANISH
    
    def translate(self, text: Optional[str], source_language: str = 'auto') -> Optional[str]:
        """
        Translate text to target language using argostranslate (offline).
        
        Args:
            text (str): Text to translate
            source_language (str): Source language code ('es', 'en', or 'auto' for auto-detection)
        
        Returns:
            str: Translated text, or original text if translation fails or text is empty
        """
        if not text or not text.strip():
            return text
        
        # Si el texto es muy corto (< 2 caracteres), no traducir
        if len(text.strip()) < 2:
            return text
        
        try:
            # Si ya está en el idioma objetivo, no traducir
            if source_language == self.target_language and source_language != 'auto':
                return text
            
            # Detectar idioma si es 'auto' (heurística mejorada)
            if source_language == 'auto':
                # Caracteres y palabras típicas del español
                spanish_indicators = ['ñ', 'á', 'é', 'í', 'ó', 'ú', 'ü', '¿', '¡']
                spanish_words = [' el ', ' la ', ' los ', ' las ', ' de ', ' del ', ' con ', ' para ', ' por ', ' que ', ' una ', ' uno ', ' es ', ' son ']
                
                # Palabras comunes en inglés
                english_words = [' the ', ' and ', ' or ', ' of ', ' to ', ' in ', ' for ', ' with ', ' on ', ' at ', ' by ', ' from ', ' is ', ' are ']
                
                text_lower = f' {text.lower()} '
                
                # Contar caracteres especiales españoles
                spanish_char_count = sum(1 for char in spanish_indicators if char in text_lower)
                
                # Contar palabras
                spanish_word_count = sum(1 for word in spanish_words if word in text_lower)
                english_word_count = sum(1 for word in english_words if word in text_lower)
                
                # Si tiene caracteres españoles, es español
                if spanish_char_count > 0:
                    source_language = 'es'
                # Si no, comparar palabras
                elif spanish_word_count > english_word_count:
                    source_language = 'es'
                elif english_word_count > spanish_word_count:
                    source_language = 'en'
                else:
                    # Por defecto, asumir que es español (WooCommerce está en español)
                    source_language = 'es'
            
            # Si el idioma detectado es el mismo que el objetivo, no traducir
            if source_language == self.target_language:
                return text
            
            # Traducir usando argostranslate (offline)
            translated = argostranslate.translate.translate(text, source_language, self.target_language)
            
            return translated if translated else text
            
        except Exception as e:
            # En caso de error, retornar el texto original
            logger.warning(f"Translation failed for text '{text[:50]}...': {str(e)}")
            return text
    
    def translate_if_needed(self, text: Optional[str], content_language: str = 'es') -> Optional[str]:
        """
        Translate text only if the target language is different from content language.
        
        This is useful for WooCommerce content which we know is in Spanish.
        
        Args:
            text (str): Text to translate
            content_language (str): Known language of the content ('es' or 'en')
        
        Returns:
            str: Translated text if needed, or original text
        """
        if not text or not text.strip():
            return text
        
        # Si el idioma objetivo es el mismo que el del contenido, no traducir
        if self.target_language == content_language:
            return text
        
        # Traducir desde el idioma conocido al objetivo
        return self.translate(text, source_language=content_language)
    
    def translate_user_content(self, text: Optional[str]) -> Optional[str]:
        """
        Translate user-generated content (unknown source language).
        Uses auto-detection to translate to target language.
        
        This is for user profiles, notes, etc. where we don't know the original language.
        
        Args:
            text (str): User-generated text
        
        Returns:
            str: Translated text
        """
        if not text or not text.strip():
            return text
        
        return self.translate(text, source_language='auto')


def get_language_from_request(request) -> str:
    """
    Extract target language from request headers.
    Looks for 'Accept-Language' header or 'lang' query parameter.
    
    Args:
        request: Django/DRF request object
    
    Returns:
        str: Language code ('es' or 'en'), defaults to 'es'
    """
    # Primero intentar desde el query parameter 'lang' (GET requests)
    lang = request.GET.get('lang', '').lower()
    if lang in TranslationService.SUPPORTED_LANGUAGES:
        return lang
    
    # Luego desde el header 'Accept-Language'
    accept_language = request.headers.get('Accept-Language', '').lower()
    
    # Parsear el header (puede venir como 'en-US', 'en', 'es', etc.)
    if accept_language:
        # Tomar los primeros 2 caracteres del código de idioma
        lang_code = accept_language.split('-')[0].split(',')[0].strip()[:2]
        if lang_code in TranslationService.SUPPORTED_LANGUAGES:
            return lang_code
    
    # Default: español
    return 'es'


def create_translator_from_request(request) -> TranslationService:
    """
    Create a TranslationService instance from request.
    
    Args:
        request: Django/DRF request object
    
    Returns:
        TranslationService: Configured translator
    """
    target_lang = get_language_from_request(request)
    return TranslationService(target_language=target_lang)


