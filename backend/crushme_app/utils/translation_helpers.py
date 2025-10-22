"""
Translation Helpers
Utility functions to easily get translated content and apply price margins
"""
from ..models import (
    WooCommerceProduct,
    WooCommerceCategory,
    TranslatedContent,
    CategoryPriceMargin,
    DefaultPriceMargin
)
from .currency_converter import CurrencyConverter


def get_translated_product(product, target_language='en'):
    """
    Get product with translated content.
    
    Args:
        product: WooCommerceProduct instance
        target_language: Target language code (default: 'en')
        
    Returns:
        dict: Product data with translations
    """
    if target_language == 'es':
        # Return original Spanish content
        return {
            'id': product.wc_id,
            'name': product.name,
            'short_description': product.short_description,
            'description': product.description,
        }
    
    # Get translations from cache
    try:
        name_trans = TranslatedContent.objects.get(
            content_type=TranslatedContent.CONTENT_TYPE_PRODUCT_NAME,
            object_id=product.wc_id,
            target_language=target_language
        )
        name = name_trans.translated_text
    except TranslatedContent.DoesNotExist:
        name = product.name
    
    try:
        short_desc_trans = TranslatedContent.objects.get(
            content_type=TranslatedContent.CONTENT_TYPE_PRODUCT_SHORT_DESC,
            object_id=product.wc_id,
            target_language=target_language
        )
        short_description = short_desc_trans.translated_text
    except TranslatedContent.DoesNotExist:
        short_description = product.short_description
    
    try:
        desc_trans = TranslatedContent.objects.get(
            content_type=TranslatedContent.CONTENT_TYPE_PRODUCT_DESC,
            object_id=product.wc_id,
            target_language=target_language
        )
        description = desc_trans.translated_text
    except TranslatedContent.DoesNotExist:
        description = product.description
    
    return {
        'id': product.wc_id,
        'name': name,
        'short_description': short_description,
        'description': description,
    }


def get_translated_category(category, target_language='en'):
    """
    Get category with translated content.
    
    Args:
        category: WooCommerceCategory instance
        target_language: Target language code
        
    Returns:
        dict: Category data with translations
    """
    if target_language == 'es':
        return {
            'id': category.wc_id,
            'name': category.name,
            'description': category.description,
        }
    
    # Get translations
    try:
        name_trans = TranslatedContent.objects.get(
            content_type=TranslatedContent.CONTENT_TYPE_CATEGORY_NAME,
            object_id=category.wc_id,
            target_language=target_language
        )
        name = name_trans.translated_text
    except TranslatedContent.DoesNotExist:
        name = category.name
    
    try:
        desc_trans = TranslatedContent.objects.get(
            content_type=TranslatedContent.CONTENT_TYPE_CATEGORY_DESC,
            object_id=category.wc_id,
            target_language=target_language
        )
        description = desc_trans.translated_text
    except TranslatedContent.DoesNotExist:
        description = category.description
    
    return {
        'id': category.wc_id,
        'name': name,
        'description': description,
    }


def calculate_product_price(product, target_currency='COP'):
    """
    Calculate product price with category margin and currency conversion.
    
    Args:
        product: WooCommerceProduct instance with base price
        target_currency: Target currency code ('COP' or 'USD')
        
    Returns:
        dict: Price information with margin applied and converted
    """
    base_price = product.price
    base_regular_price = product.regular_price
    base_sale_price = product.sale_price
    
    if not base_price:
        return {
            'price': None,
            'regular_price': None,
            'sale_price': None,
            'margin_applied': None,
            'on_sale': product.on_sale
        }
    
    # Get margin configuration
    margin = None
    
    # Try to get margin from product's first category
    first_category = product.categories.first()
    if first_category:
        try:
            margin = CategoryPriceMargin.objects.get(
                category=first_category,
                is_active=True
            )
        except CategoryPriceMargin.DoesNotExist:
            pass
    
    # Fallback to default margin
    if not margin:
        margin = DefaultPriceMargin.get_active()
    
    # Apply margin
    if margin:
        final_price = margin.calculate_price(base_price)
        final_regular_price = margin.calculate_price(base_regular_price) if base_regular_price else None
        final_sale_price = margin.calculate_price(base_sale_price) if base_sale_price else None
    else:
        # No margin configured, use original prices
        final_price = float(base_price)
        final_regular_price = float(base_regular_price) if base_regular_price else None
        final_sale_price = float(base_sale_price) if base_sale_price else None
    
    # Convert to target currency
    converted_price = CurrencyConverter.convert_price(final_price, target_currency)
    converted_regular_price = CurrencyConverter.convert_price(final_regular_price, target_currency) if final_regular_price else None
    converted_sale_price = CurrencyConverter.convert_price(final_sale_price, target_currency) if final_sale_price else None
    
    return {
        'price': round(converted_price, 2) if converted_price else None,
        'regular_price': round(converted_regular_price, 2) if converted_regular_price else None,
        'sale_price': round(converted_sale_price, 2) if converted_sale_price else None,
        'converted_price': round(converted_price, 2) if converted_price else None,
        'converted_regular_price': round(converted_regular_price, 2) if converted_regular_price else None,
        'margin_applied': str(margin) if margin else None,
        'currency': target_currency,
        'on_sale': product.on_sale
    }


def get_product_full_data(product, target_language='en', include_stock=True, target_currency='COP'):
    """
    Get complete product data with translations, prices with margin, and optionally fresh stock.
    
    Args:
        product: WooCommerceProduct instance or wc_id
        target_language: Language for translations
        include_stock: If True, fetch fresh stock from WooCommerce (slower)
        target_currency: Target currency code ('COP' or 'USD')
        
    Returns:
        dict: Complete product data
    """
    # Get product instance if ID was provided
    if isinstance(product, int):
        product = WooCommerceProduct.objects.get(wc_id=product)
    
    # Get translations
    translated = get_translated_product(product, target_language)
    
    # Calculate prices with margin and currency conversion
    prices = calculate_product_price(product, target_currency)
    
    # Get categories with translations
    categories = []
    for cat in product.categories.all():
        cat_translated = get_translated_category(cat, target_language)
        categories.append({
            'id': cat.wc_id,
            'name': cat_translated['name'],
            'slug': cat.slug
        })
    
    # Get images
    images = []
    for img in product.images.all():
        images.append({
            'id': img.wc_id,
            'src': img.src,
            'thumbnail': img.thumbnail,
            'alt': img.alt,
            'position': img.position
        })
    
    # Base data
    data = {
        'id': product.wc_id,
        'name': translated['name'],
        'slug': product.slug,
        'permalink': product.permalink,
        'type': product.product_type,
        'short_description': translated['short_description'],
        'description': translated['description'],
        'price': prices['price'],
        'regular_price': prices['regular_price'],
        'sale_price': prices['sale_price'],
        'on_sale': prices['on_sale'],
        'categories': categories,
        'images': images,
        'average_rating': float(product.average_rating),
        'rating_count': product.rating_count,
        'featured': product.featured,
        'status': product.status,
        # Stock info (always included, from local DB)
        # Can be overridden by real-time data in the view
        'stock_status': product.stock_status,
        'stock_quantity': product.stock_quantity,
        'manage_stock': product.manage_stock,
        'in_stock': product.stock_status == 'instock',
    }
    
    # Add product type info for frontend logic
    if product.is_variable:
        data['is_variable'] = True
        variations = product.variations.filter(status='publish')
        data['variations_count'] = variations.count()
        data['variations_endpoint'] = f'/api/products/woocommerce/products/{product.wc_id}/variations/'
        
        # Get margin info to apply to variations
        margin_applied = prices.get('margin_applied')
        
        # Extract margin percentage from string (e.g., "Default: +15%" -> 15)
        margin_percentage = None
        if margin_applied:
            try:
                import re
                match = re.search(r'[+-]?(\d+(?:\.\d+)?)', str(margin_applied))
                if match:
                    margin_percentage = float(match.group(1))
            except (ValueError, AttributeError):
                margin_percentage = None
        
        # Get all unique attributes and their options
        attributes_map = {}
        variations_summary = []
        
        for variation in variations:
            # Collect attributes
            for attr_key, attr_value in variation.attributes.items():
                if attr_key not in attributes_map:
                    attributes_map[attr_key] = set()
                attributes_map[attr_key].add(attr_value)
            
            # Apply margin to variation price (inherit from product parent)
            variation_price = float(variation.price) if variation.price else None
            if variation_price and margin_percentage:
                margin_multiplier = 1 + (margin_percentage / 100)
                variation_price = round(variation_price * margin_multiplier, 2)
            
            # Convert variation price to target currency
            converted_variation_price = CurrencyConverter.convert_price(variation_price, target_currency) if variation_price else None
            
            # Add variation summary (id + attributes for quick lookup)
            variations_summary.append({
                'id': variation.wc_id,
                'attributes': variation.attributes,
                'in_stock': variation.stock_status == 'instock',
                'stock_quantity': variation.stock_quantity,
                'price': round(converted_variation_price, 2) if converted_variation_price else None,
                'converted_price': round(converted_variation_price, 2) if converted_variation_price else None
            })
        
        # Convert attributes to list format
        attributes_list = []
        for attr_key, attr_values in attributes_map.items():
            # Clean attribute key (remove 'attribute_pa_' prefix if exists)
            clean_key = attr_key.replace('attribute_pa_', '').replace('attribute_', '')
            attributes_list.append({
                'name': clean_key,
                'slug': attr_key,
                'options': sorted(list(attr_values))
            })
        
        data['attributes'] = attributes_list
        data['available_variations'] = variations_summary
    else:
        data['is_variable'] = False
    
    return data


def get_products_list(queryset, target_language='en', include_stock=False, target_currency='COP'):
    """
    Get list of products with translations and prices.
    Optimized for list views (no full descriptions).
    
    Args:
        queryset: WooCommerceProduct queryset
        target_language: Language for translations
        include_stock: Include stock info (makes it slower)
        target_currency: Target currency code ('COP' or 'USD')
        
    Returns:
        list: List of product data
    """
    products = []
    
    for product in queryset:
        # Get basic translations (name and short description only)
        try:
            name_trans = TranslatedContent.objects.get(
                content_type=TranslatedContent.CONTENT_TYPE_PRODUCT_NAME,
                object_id=product.wc_id,
                target_language=target_language
            ) if target_language != 'es' else None
            name = name_trans.translated_text if name_trans else product.name
        except TranslatedContent.DoesNotExist:
            name = product.name
        
        try:
            short_desc_trans = TranslatedContent.objects.get(
                content_type=TranslatedContent.CONTENT_TYPE_PRODUCT_SHORT_DESC,
                object_id=product.wc_id,
                target_language=target_language
            ) if target_language != 'es' else None
            short_description = short_desc_trans.translated_text if short_desc_trans else product.short_description
        except TranslatedContent.DoesNotExist:
            short_description = product.short_description
        
        # Calculate prices with currency conversion
        prices = calculate_product_price(product, target_currency)
        
        # Get primary image (single URL for simple display)
        primary_image = product.primary_image
        image_url = primary_image.src if primary_image else None
        
        # Get all images in WooCommerce format
        images_data = []
        for img in product.images.all().order_by('position'):
            images_data.append({
                'id': img.wc_id,
                'src': img.src,
                'name': img.name or '',
                'alt': img.alt or '',
                'thumbnail': img.thumbnail or img.src  # Use thumbnail or fallback to src
            })
        
        # Get first category
        first_category = product.categories.first()
        category_name = first_category.name if first_category else None
        
        if first_category and target_language != 'es':
            try:
                cat_trans = TranslatedContent.objects.get(
                    content_type=TranslatedContent.CONTENT_TYPE_CATEGORY_NAME,
                    object_id=first_category.wc_id,
                    target_language=target_language
                )
                category_name = cat_trans.translated_text
            except TranslatedContent.DoesNotExist:
                pass
        
        product_data = {
            'id': product.wc_id,
            'name': name,
            'slug': product.slug,
            'type': product.product_type,  # 'simple', 'variable', 'grouped'
            'short_description': short_description,
            'price': prices['price'],
            'regular_price': prices['regular_price'],
            'sale_price': prices['sale_price'],
            'converted_price': prices.get('converted_price'),
            'converted_regular_price': prices.get('converted_regular_price'),
            'currency': prices.get('currency', target_currency),
            'on_sale': prices['on_sale'],
            'image': image_url,  # Primary image URL (for backward compatibility)
            'images': images_data,  # Full images array in WooCommerce format
            'category': category_name,
            'featured': product.featured,
            'average_rating': float(product.average_rating),
            'rating_count': product.rating_count,
        }
        
        # Add product type info for frontend logic
        if product.is_variable:
            product_data['is_variable'] = True
            product_data['variations_count'] = product.variations.filter(status='publish').count()
        else:
            product_data['is_variable'] = False
        
        if include_stock:
            # For variable products, don't include direct stock (it's in variations)
            if not product.is_variable:
                product_data['stock_status'] = product.stock_status
                product_data['in_stock'] = product.stock_status == 'instock'
        
        products.append(product_data)
    
    return products
