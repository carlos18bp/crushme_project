"""
Utils package for CrushMe app
"""
# Import from base.py (existing utils functions)
from .base import calculate_shipping_cost, generate_auth_tokens

# Import from translation_helpers (new functions)
from .translation_helpers import (
    get_translated_product,
    get_translated_category,
    calculate_product_price,
    get_product_full_data,
    get_products_list
)

# Import from html_helpers
from .html_helpers import (
    strip_html_tags,
    should_strip_html,
    extract_text_from_html,
    clean_malformed_html_translation
)

__all__ = [
    # Existing utils
    'calculate_shipping_cost',
    'generate_auth_tokens',
    # Translation helpers
    'get_translated_product',
    'get_translated_category',
    'calculate_product_price',
    'get_product_full_data',
    'get_products_list',
    # HTML helpers
    'strip_html_tags',
    'should_strip_html',
    'extract_text_from_html',
    'clean_malformed_html_translation',
]
