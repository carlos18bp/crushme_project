"""
HTML cleaning utilities for translations
"""
import re
from html import unescape


def strip_html_tags(text):
    """
    Remove all HTML tags from text but keep the content.
    
    Args:
        text: Text with HTML tags
        
    Returns:
        str: Clean text without HTML tags
    """
    if not text:
        return text
    
    # Unescape HTML entities first
    text = unescape(text)
    
    # Remove HTML tags
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text


def should_strip_html(content_type):
    """
    Determine if HTML should be stripped for this content type.
    
    Args:
        content_type: Type of content
        
    Returns:
        bool: True if HTML should be stripped
    """
    # Para nombres, siempre limpiar HTML
    # Para descripciones, mantener HTML pero traducir solo el texto
    from ..models import TranslatedContent
    
    strip_types = [
        TranslatedContent.CONTENT_TYPE_PRODUCT_NAME,
        TranslatedContent.CONTENT_TYPE_CATEGORY_NAME,
    ]
    
    return content_type in strip_types


def extract_text_from_html(html_text):
    """
    Extract plain text from HTML for translation, preserving structure.
    
    Args:
        html_text: HTML content
        
    Returns:
        tuple: (plain_text, has_html)
    """
    if not html_text:
        return html_text, False
    
    # Check if it has HTML tags
    has_html = bool(re.search(r'<[^>]+>', html_text))
    
    if not has_html:
        return html_text, False
    
    # Extract text from HTML
    clean_text = strip_html_tags(html_text)
    return clean_text, True


def clean_malformed_html_translation(text):
    """
    Clean malformed HTML that was translated (with spaces in tags).
    
    Examples:
        '< h5 >' -> '<h5>'
        '< / h5 >' -> '</h5>'
        '< strong >' -> '<strong>'
    
    Args:
        text: Text with malformed HTML tags
        
    Returns:
        str: Text with fixed HTML tags
    """
    if not text:
        return text
    
    # Fix opening tags: < tag > -> <tag>
    text = re.sub(r'<\s+([a-zA-Z][a-zA-Z0-9]*)\s+>', r'<\1>', text)
    
    # Fix closing tags: < / tag > -> </tag>
    text = re.sub(r'<\s+/\s+([a-zA-Z][a-zA-Z0-9]*)\s+>', r'</\1>', text)
    
    # Fix self-closing tags: < tag / > -> <tag/>
    text = re.sub(r'<\s+([a-zA-Z][a-zA-Z0-9]*)\s+/\s+>', r'<\1/>', text)
    
    # Fix tags with attributes: < tag attr = "value" > -> <tag attr="value">
    text = re.sub(r'<\s+([a-zA-Z][a-zA-Z0-9]*)\s+([^>]+)>', r'<\1 \2>', text)
    
    # Fix spaces around = in attributes
    text = re.sub(r'\s*=\s*', '=', text)
    
    # Fix spaces in color codes: # 333333 -> #333333
    text = re.sub(r'#\s+([0-9a-fA-F]{3,6})', r'#\1', text)
    
    return text
