"""
Price conversion helpers for API responses
"""
from .currency_converter import CurrencyConverter


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
