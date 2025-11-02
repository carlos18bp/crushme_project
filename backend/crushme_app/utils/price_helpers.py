"""
Price conversion helpers for API responses
"""
from .currency_converter import CurrencyConverter


def apply_category_margin_to_product(product):
    """
    Aplica el margen de categoría a un producto WooCommerce.
    
    Args:
        product: Instancia de WooCommerceProduct o WooCommerceProductVariation
        
    Returns:
        Diccionario con precios con margen aplicado:
        {
            'price': precio_con_margen,
            'regular_price': precio_regular_con_margen,
            'sale_price': precio_oferta_con_margen (si existe)
        }
    """
    result = {}
    
    # Aplicar margen al precio actual
    if hasattr(product, 'get_price_with_margin'):
        result['price'] = product.get_price_with_margin()
        result['regular_price'] = product.get_regular_price_with_margin()
        sale_price = product.get_sale_price_with_margin()
        if sale_price:
            result['sale_price'] = sale_price
    else:
        # Fallback si el producto no tiene los métodos
        result['price'] = float(product.price) if product.price else None
        result['regular_price'] = float(product.regular_price) if product.regular_price else None
        if product.sale_price:
            result['sale_price'] = float(product.sale_price)
    
    return result


def apply_margin_and_convert_price(product, currency='COP'):
    """
    Aplica margen de categoría Y convierte a la moneda solicitada.
    
    Args:
        product: Instancia de WooCommerceProduct o WooCommerceProductVariation
        currency: Moneda destino ('COP' o 'USD')
        
    Returns:
        Diccionario con precios con margen aplicado y convertidos:
        {
            'price': precio_final,
            'regular_price': precio_regular_final,
            'sale_price': precio_oferta_final (si existe),
            'currency': 'COP' o 'USD'
        }
    """
    # Primero aplicar margen
    prices = apply_category_margin_to_product(product)
    
    # Luego convertir a la moneda solicitada
    result = {}
    for key, value in prices.items():
        if value is not None:
            result[key] = CurrencyConverter.convert_price(value, currency)
        else:
            result[key] = None
    
    result['currency'] = currency.upper()
    return result


def convert_price_fields(data, currency, fields=None):
    """
    Convert price fields in a dictionary to target currency.
    
    Args:
        data: Dictionary or list containing price fields
        currency: Target currency ('COP' or 'USD')
        fields: List of field names to convert. If None, uses common price fields.
        
    Returns:
        Modified data with converted prices and currency field added
    """
    if fields is None:
        # Common price field names
        fields = [
            'price', 'unit_price', 'subtotal', 'total', 'total_price',
            'shipping', 'shipping_cost', 'regular_price', 'sale_price',
            'amount', 'total_amount', 'total_revenue', 'total_spent',
            'product_price', 'total_value'  # Wishlist fields
        ]
    
    if isinstance(data, dict):
        # Convert dictionary
        for field in fields:
            if field in data and data[field] is not None:
                # Handle both string and numeric values
                try:
                    value = float(data[field]) if isinstance(data[field], str) else data[field]
                    data[field] = CurrencyConverter.convert_price(value, currency)
                except (ValueError, TypeError):
                    pass  # Skip if conversion fails
        
        # Add currency indicator
        data['currency'] = currency.upper()
        
        # Recursively convert nested dictionaries
        for key, value in data.items():
            if isinstance(value, dict) and key not in ['currency']:
                convert_price_fields(value, currency, fields)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        convert_price_fields(item, currency, fields)
    
    elif isinstance(data, list):
        # Convert list of dictionaries
        for item in data:
            if isinstance(item, dict):
                convert_price_fields(item, currency, fields)
    
    return data


def convert_cart_response(cart_data, currency):
    """
    Convert cart response data to target currency.
    
    Args:
        cart_data: Cart data dictionary
        currency: Target currency ('COP' or 'USD')
        
    Returns:
        Cart data with converted prices
    """
    return convert_price_fields(cart_data, currency, [
        'unit_price', 'subtotal', 'total_price', 'price'
    ])


def convert_order_response(order_data, currency):
    """
    Convert order response data to target currency.
    
    Args:
        order_data: Order data dictionary
        currency: Target currency ('COP' or 'USD')
        
    Returns:
        Order data with converted prices
    """
    return convert_price_fields(order_data, currency, [
        'unit_price', 'subtotal', 'total', 'shipping', 'shipping_cost',
        'total_amount', 'price'
    ])


def convert_statistics_response(stats_data, currency):
    """
    Convert statistics response data to target currency.
    
    Args:
        stats_data: Statistics data dictionary
        currency: Target currency ('COP' or 'USD')
        
    Returns:
        Statistics data with converted prices
    """
    return convert_price_fields(stats_data, currency, [
        'total_revenue', 'total_spent', 'total_amount', 'average_order_value'
    ])
