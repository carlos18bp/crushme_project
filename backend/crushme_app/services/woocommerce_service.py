"""
WooCommerce API integration service
Handles connection and data fetching from WooCommerce REST API
"""
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class WooCommerceService:
    """
    Service class to handle WooCommerce API integration
    """
    
    def __init__(self):
        self.base_url = "https://desarrollo.distrisex.com/wp-json/wc/v3"
        # Estas credenciales deberían venir de settings o variables de entorno
        # Por ahora las dejamos como placeholder
        self.consumer_key = getattr(settings, 'WOOCOMMERCE_CONSUMER_KEY', 'your_consumer_key_here')
        self.consumer_secret = getattr(settings, 'WOOCOMMERCE_CONSUMER_SECRET', 'your_consumer_secret_here')
        self.auth = HTTPBasicAuth(self.consumer_key, self.consumer_secret)
        self.timeout = 30
    
    def _make_request(self, endpoint, params=None):
        """
        Make a GET request to WooCommerce API
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(
                url,
                auth=self.auth,
                params=params,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            # Log de la respuesta para debugging
            logger.info(f"WooCommerce API request to: {url}")
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json(),
                    'status_code': response.status_code,
                    'headers': dict(response.headers)
                }
            else:
                logger.error(f"WooCommerce API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"API returned status {response.status_code}",
                    'status_code': response.status_code,
                    'response_text': response.text
                }
                
        except requests.exceptions.Timeout:
            logger.error("WooCommerce API request timeout")
            return {
                'success': False,
                'error': 'Request timeout',
                'status_code': None
            }
        except requests.exceptions.ConnectionError:
            logger.error("WooCommerce API connection error")
            return {
                'success': False,
                'error': 'Connection error',
                'status_code': None
            }
        except Exception as e:
            logger.error(f"WooCommerce API unexpected error: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'status_code': None
            }
    
    def get_products(self, category_id=None, per_page=100, page=1):
        """
        Get products from WooCommerce
        
        Args:
            category_id (int, optional): Category ID to filter products
            per_page (int): Number of products per page (max 100)
            page (int): Page number for pagination
        
        Returns:
            dict: API response with products data
        """
        params = {
            'per_page': min(per_page, 100),  # WooCommerce max is 100
            'page': page,
            'status': 'publish'  # Only published products
        }
        
        if category_id:
            params['category'] = category_id
        
        return self._make_request('products', params)
    
    def get_categories(self, per_page=100, page=1):
        """
        Get product categories from WooCommerce
        
        Args:
            per_page (int): Number of categories per page
            page (int): Page number for pagination
        
        Returns:
            dict: API response with categories data
        """
        params = {
            'per_page': per_page,
            'page': page,
            'hide_empty': False  # Include categories without products
        }
        
        return self._make_request('products/categories', params)
    
    def get_product_by_id(self, product_id):
        """
        Get a specific product by ID
        
        Args:
            product_id (int): Product ID
        
        Returns:
            dict: API response with product data
        """
        return self._make_request(f'products/{product_id}')
    
    def get_category_by_id(self, category_id):
        """
        Get a specific category by ID
        
        Args:
            category_id (int): Category ID
        
        Returns:
            dict: API response with category data
        """
        return self._make_request(f'products/categories/{category_id}')


# Singleton instance
woocommerce_service = WooCommerceService()

