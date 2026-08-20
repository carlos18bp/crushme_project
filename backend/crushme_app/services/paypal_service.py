"""
PayPal Payment Service
Handles PayPal Orders API integration for payment processing
"""
import requests
import base64
from decimal import Decimal, InvalidOperation
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Country name to ISO code mapping
COUNTRY_CODE_MAPPING = {
    # Colombia variations
    'COLOMBIA': 'CO',
    'Colombia': 'CO',
    'colombia': 'CO',
    'CO': 'CO',
    
    # Other common countries for WooCommerce
    'UNITED STATES': 'US',
    'United States': 'US',
    'USA': 'US',
    'US': 'US',
    
    'MEXICO': 'MX',
    'Mexico': 'MX',
    'MX': 'MX',
    
    'CANADA': 'CA',
    'Canada': 'CA',
    'CA': 'CA',
    
    'SPAIN': 'ES',
    'Spain': 'ES',
    'ES': 'ES',
    
    'PERU': 'PE',
    'Peru': 'PE',
    'PE': 'PE',
    
    'ECUADOR': 'EC',
    'Ecuador': 'EC',
    'EC': 'EC',
    
    'VENEZUELA': 'VE',
    'Venezuela': 'VE',
    'VE': 'VE',
    
    'ARGENTINA': 'AR',
    'Argentina': 'AR',
    'AR': 'AR',
    
    'CHILE': 'CL',
    'Chile': 'CL',
    'CL': 'CL',
    
    'BRAZIL': 'BR',
    'Brazil': 'BR',
    'BR': 'BR',
}


class PayPalService:
    """
    Service to handle PayPal payment processing
    Uses PayPal Orders API v2
    """
    
    def __init__(self):
        self.client_id = getattr(settings, 'PAYPAL_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'PAYPAL_CLIENT_SECRET', '')
        self.mode = getattr(settings, 'PAYPAL_MODE', 'sandbox')

        # Set API URL based on mode
        if self.mode == 'live':
            self.base_url = 'https://api-m.paypal.com'
        else:
            self.base_url = 'https://api-m.sandbox.paypal.com'
        
        self.timeout = 30
    
    def _normalize_country_code(self, country):
        """
        Convert country name to 2-letter ISO code for PayPal
        
        Args:
            country: Country name or code (e.g., "COLOMBIA", "Colombia", "CO")
        
        Returns:
            str: 2-letter ISO country code (e.g., "CO")
        """
        if not country:
            return 'US'  # Default fallback
        
        # Strip whitespace and get from mapping
        country_clean = country.strip()
        country_code = COUNTRY_CODE_MAPPING.get(country_clean)
        
        if country_code:
            logger.debug(f"Country mapping: '{country}' -> '{country_code}'")
            return country_code
        
        # If not found in mapping, assume it's already a 2-letter code
        if len(country_clean) == 2 and country_clean.isalpha():
            logger.debug(f"Using country code as-is: '{country_clean}'")
            return country_clean.upper()
        
        # Fallback for unknown countries
        logger.warning(f"Unknown country '{country}', using default 'US'")
        return 'US'
    
    def _get_access_token(self):
        """
        Get OAuth 2.0 access token from PayPal
        """
        try:
            url = f"{self.base_url}/v1/oauth2/token"
            
            # Create basic auth header
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_base64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_base64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(
                url,
                headers=headers,
                data=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return {
                    'success': True,
                    'access_token': token_data.get('access_token')
                }
            else:
                logger.error('PayPal authentication failed with status %s', response.status_code)
                return {
                    'success': False,
                    'error': f"Authentication failed: {response.status_code}"
                }
        
        except Exception:
            logger.exception('PayPal authentication request failed')
            return {
                'success': False,
                'error': 'Authentication request failed'
            }
    
    def create_order(self, cart_items, shipping_info, total_amount, shipping_cost=0, discount_amount=0):
        """
        Create a PayPal order
        
        Args:
            cart_items: List of items from cart
            shipping_info: Dict with shipping address
            total_amount: Decimal total amount (items + shipping - discount)
            shipping_cost: Decimal shipping cost
            discount_amount: Decimal discount amount
        
        Returns:
            dict: PayPal order response with order_id
        """
        try:
            # Get access token
            auth_result = self._get_access_token()
            if not auth_result['success']:
                return auth_result
            
            access_token = auth_result['access_token']
            
            # Build order payload
            payload = self._build_order_payload(cart_items, shipping_info, total_amount, shipping_cost, discount_amount)
            
            # Create order
            url = f"{self.base_url}/v2/checkout/orders"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            
            logger.info("Creating PayPal order...")
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 201:
                order_data = response.json()
                logger.info(f"✅ PayPal order created: {order_data.get('id')}")
                return {
                    'success': True,
                    'order_id': order_data.get('id'),
                    'status': order_data.get('status'),
                    'data': order_data
                }
            else:
                logger.error(
                    'PayPal order creation failed with status %s',
                    response.status_code,
                )
                return {
                    'success': False,
                    'error': f"Order creation failed: {response.status_code}",
                }
        
        except Exception:
            logger.exception('PayPal order creation request failed')
            return {
                'success': False,
                'error': 'Order creation request failed'
            }
    
    def capture_order(self, order_id):
        """
        Capture/complete a PayPal order after customer approval
        
        Args:
            order_id: PayPal order ID to capture
        
        Returns:
            dict: Capture response with payment details
        """
        try:
            # Get access token
            auth_result = self._get_access_token()
            if not auth_result['success']:
                return auth_result
            
            access_token = auth_result['access_token']
            
            # Capture order
            url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'PayPal-Request-Id': f'crushme-capture-{order_id}',
            }
            
            logger.info(f"Capturing PayPal order: {order_id}")
            
            response = requests.post(
                url,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code in {200, 201}:
                return self._extract_capture_result(response.json(), order_id)

            # A retry can arrive after PayPal captured the order but before the
            # application persisted it. Reading the order makes that path safe.
            order_result = self.get_order(order_id, access_token=access_token)
            if order_result['success']:
                return order_result

            logger.error('PayPal capture failed with status %s', response.status_code)
            return {
                'success': False,
                'error': f'Payment capture failed: {response.status_code}',
            }

        except Exception:
            logger.exception('PayPal capture request failed')
            return {
                'success': False,
                'error': 'Payment capture request failed'
            }

    def get_order(self, order_id, access_token=None):
        """Retrieve an order and return its completed capture details."""
        try:
            if not access_token:
                auth_result = self._get_access_token()
                if not auth_result['success']:
                    return auth_result
                access_token = auth_result['access_token']

            response = requests.get(
                f'{self.base_url}/v2/checkout/orders/{order_id}',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=self.timeout,
            )
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Order lookup failed: {response.status_code}',
                }
            return self._extract_capture_result(response.json(), order_id)
        except Exception as exc:
            logger.error('PayPal order lookup error: %s', exc)
            return {'success': False, 'error': 'Order lookup failed'}

    @staticmethod
    def _extract_capture_result(capture_data, order_id):
        captures = []
        for purchase_unit in capture_data.get('purchase_units', []):
            captures.extend(
                purchase_unit.get('payments', {}).get('captures', [])
            )

        if (
            capture_data.get('status') != 'COMPLETED'
            or not captures
            or any(capture.get('status') != 'COMPLETED' for capture in captures)
        ):
            return {
                'success': False,
                'error': 'PayPal order is not fully captured',
                'status': capture_data.get('status'),
            }

        currencies = {
            capture.get('amount', {}).get('currency_code')
            for capture in captures
        }
        if None in currencies or len(currencies) != 1:
            return {'success': False, 'error': 'Invalid PayPal capture currency'}

        try:
            captured_amount = sum(
                Decimal(capture['amount']['value'])
                for capture in captures
            ).quantize(Decimal('0.01'))
        except (InvalidOperation, KeyError, TypeError):
            return {'success': False, 'error': 'Invalid PayPal capture amount'}

        payer = capture_data.get('payer', {})
        payer_name = ' '.join(filter(None, [
            payer.get('name', {}).get('given_name'),
            payer.get('name', {}).get('surname'),
        ]))
        return {
            'success': True,
            'order_id': order_id,
            'capture_id': captures[0].get('id'),
            'status': capture_data.get('status'),
            'captured_amount': str(captured_amount),
            'currency': currencies.pop(),
            'payer_email': payer.get('email_address'),
            'payer_name': payer_name,
            'data': capture_data,
        }
    
    def _build_order_payload(self, cart_items, shipping_info, total_amount, shipping_cost=0, discount_amount=0):
        """
        Build PayPal order payload with shipping and discount
        
        Args:
            cart_items: List of items from cart
            shipping_info: Dict with shipping address
            total_amount: Total amount (items + shipping - discount)
            shipping_cost: Shipping cost
            discount_amount: Discount amount
        """
        # Build purchase units with items
        items = []
        for item in cart_items:
            unit_price = round(float(item['unit_price']), 2)
            items.append({
                'name': item['product_name'],
                'quantity': str(item['quantity']),
                'unit_amount': {
                    'currency_code': 'USD',  # PayPal requiere USD
                    'value': f"{unit_price:.2f}"
                }
            })
        
        # Calculate breakdown
        items_total = sum(float(item['unit_price']) * item['quantity'] for item in cart_items)
        items_total = round(items_total, 2)
        
        # Normalize country code for PayPal API
        country_code = self._normalize_country_code(shipping_info.get('country', 'US'))
        
        # Build breakdown with shipping
        # NOTA: Los precios de productos YA INCLUYEN IVA del 19% (impuesto incluido en Colombia)
        # Por lo tanto, NO agregamos 'tax' como campo separado en el breakdown
        
        # Round shipping and total to 2 decimals
        shipping_cost = round(float(shipping_cost), 2) if shipping_cost else 0
        total_amount = round(float(total_amount), 2)
        
        breakdown = {
            'item_total': {
                'currency_code': 'USD',
                'value': f"{items_total:.2f}"  # IVA 19% ya incluido
            }
        }
        
        # Add shipping to breakdown if present
        if shipping_cost and shipping_cost > 0:
            breakdown['shipping'] = {
                'currency_code': 'USD',
                'value': f"{shipping_cost:.2f}"
            }
            logger.info(f"💰 [PAYPAL PAYLOAD] Including shipping in breakdown: {shipping_cost}")
        
        # Add discount to breakdown if present
        discount_amount = round(float(discount_amount), 2) if discount_amount else 0
        if discount_amount and discount_amount > 0:
            breakdown['discount'] = {
                'currency_code': 'USD',
                'value': f"{discount_amount:.2f}"
            }
            logger.info(f"💰 [PAYPAL PAYLOAD] Including discount in breakdown: {discount_amount}")
        
        # Build purchase unit
        purchase_unit = {
            'amount': {
                'currency_code': 'USD',
                'value': f"{total_amount:.2f}",
                'breakdown': breakdown
            },
            'items': items,
            'shipping': {
                'name': {
                    'full_name': shipping_info.get('name', 'Customer')
                },
                'address': {
                    'address_line_1': shipping_info.get('address_line_1', ''),
                    'admin_area_2': shipping_info.get('city', ''),
                    'admin_area_1': shipping_info.get('state', ''),
                    'postal_code': shipping_info.get('zipcode', ''),
                    'country_code': country_code
                }
            }
        }
        
        payload = {
            'intent': 'CAPTURE',
            'purchase_units': [purchase_unit],
            'application_context': {
                'brand_name': 'CrushMe Store',
                'landing_page': 'NO_PREFERENCE',
                'user_action': 'PAY_NOW',
                'return_url': f'{settings.FRONTEND_URL}/checkout/success',
                'cancel_url': f'{settings.FRONTEND_URL}/checkout/cancel'
            }
        }
        
        return payload


# Singleton instance
paypal_service = PayPalService()
