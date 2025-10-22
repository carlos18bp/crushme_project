"""
Middleware to handle currency selection from request headers
"""


class CurrencyMiddleware:
    """
    Middleware to extract and store currency preference from request headers.
    
    Reads the X-Currency header and makes it available throughout the request lifecycle.
    Supported currencies: COP (default), USD
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extract currency from header
        currency = request.headers.get('X-Currency', 'COP').upper()
        
        # Validate currency
        if currency not in ['COP', 'USD']:
            currency = 'COP'  # Default to COP if invalid
        
        # Store in request for easy access
        request.currency = currency
        
        response = self.get_response(request)
        
        # Optionally add currency to response headers for debugging
        response['X-Currency-Used'] = currency
        
        return response
