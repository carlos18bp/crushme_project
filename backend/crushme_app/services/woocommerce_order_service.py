"""
WooCommerce Order Integration Service
Handles sending orders to WooCommerce API with country-specific formatting
"""
import requests
import re
from requests.auth import HTTPBasicAuth
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ColombianAddressParser:
    """
    Parser for Colombian addresses
    Converts simple address string to WooCommerce Colombian format
    """
    
    # Tipos de vías en Colombia
    ADDRESS_TYPES = [
        'CALLE', 'CARRERA', 'AVENIDA', 'TRANSVERSAL', 'DIAGONAL', 
        'CIRCULAR', 'AUTOPISTA', 'KM', 'KILOMETRO'
    ]
    
    @staticmethod
    def parse(address_string):
        """
        Parse Colombian address string
        
        Examples:
        - "Carrera 80 #50-25 Apto 301" 
        - "Calle 10 # 20-30"
        - "Avenida 68 #45-23"
        
        Returns:
        {
            'type_address': 'Carrera',
            'street_1': '80',
            'street_2': '50',
            'street_3': '25',
            'unit_number': '301',
            'type_property': 'Apartamento'
        }
        """
        result = {
            'type_address': '',
            'street_1': '',
            'street_2': '',
            'street_3': '',
            'unit_number': '',
            'type_property': ''
        }
        
        if not address_string:
            return result
        
        address_upper = address_string.upper().strip()
        
        # 1. Detectar tipo de vía
        for addr_type in ColombianAddressParser.ADDRESS_TYPES:
            if address_upper.startswith(addr_type):
                result['type_address'] = addr_type.capitalize()
                address_upper = address_upper.replace(addr_type, '', 1).strip()
                break
        
        # 2. Extraer números principales (ej: "80 #50-25")
        # Patrón: número + # + número + - + número
        pattern = r'(\d+)\s*[#]?\s*(\d+)\s*[-]?\s*(\d+)?'
        match = re.search(pattern, address_upper)
        
        if match:
            result['street_1'] = match.group(1)  # 80
            result['street_2'] = match.group(2)  # 50
            if match.group(3):
                result['street_3'] = match.group(3)  # 25
        
        # 3. Detectar tipo de propiedad y número de unidad
        if 'APTO' in address_upper or 'APARTAMENTO' in address_upper:
            result['type_property'] = 'Apartamento'
            # Extraer número de apartamento
            apt_match = re.search(r'(?:APTO|APARTAMENTO)[.]?\s*(\d+[A-Z]?)', address_upper)
            if apt_match:
                result['unit_number'] = apt_match.group(1)
        
        elif 'CASA' in address_upper:
            result['type_property'] = 'Casa'
            casa_match = re.search(r'CASA\s*(\d+[A-Z]?)', address_upper)
            if casa_match:
                result['unit_number'] = casa_match.group(1)
        
        elif 'LOCAL' in address_upper:
            result['type_property'] = 'Local'
            local_match = re.search(r'LOCAL\s*(\d+[A-Z]?)', address_upper)
            if local_match:
                result['unit_number'] = local_match.group(1)
        
        elif 'OFICINA' in address_upper or 'OF' in address_upper:
            result['type_property'] = 'Oficina'
            of_match = re.search(r'(?:OFICINA|OF)[.]?\s*(\d+[A-Z]?)', address_upper)
            if of_match:
                result['unit_number'] = of_match.group(1)
        else:
            # Default
            result['type_property'] = 'Casa'
        
        return result


class WooCommerceOrderService:
    """
    Service to send orders to WooCommerce API
    """
    
    # Fixed customer_id for your store
    STORE_CUSTOMER_ID = 659
    
    def __init__(self):
        self.base_url = getattr(settings, 'WOOCOMMERCE_API_URL',
                                'https://distrisexcolombia.com/wp-json/wc/v3')
        self.consumer_key = getattr(settings, 'WOOCOMMERCE_CONSUMER_KEY', '')
        self.consumer_secret = getattr(settings, 'WOOCOMMERCE_CONSUMER_SECRET', '')
        self.auth = HTTPBasicAuth(self.consumer_key, self.consumer_secret)
        self.timeout = 30
    
    def send_order(self, order, shipping_cost=None):
        """
        Send order to WooCommerce API

        Args:
            order: Order model instance
            shipping_cost: Optional shipping cost in Colombian pesos

        Returns:
            dict: Response from WooCommerce API
        """
        try:
            # Build WooCommerce order payload
            payload = self._build_order_payload(order, shipping_cost)
            
            # Log request
            logger.info(f"Sending order {order.order_number} to WooCommerce")
            logger.debug(f"Payload: {payload}")
            
            # Make request
            url = f"{self.base_url}/orders"
            response = requests.post(
                url,
                auth=self.auth,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            # Handle response
            if response.status_code in [200, 201]:
                wc_order = response.json()
                logger.info(f"✅ Order {order.order_number} created in WooCommerce with ID: {wc_order.get('id')}")
                
                return {
                    'success': True,
                    'woocommerce_order_id': wc_order.get('id'),
                    'woocommerce_order_number': wc_order.get('number'),
                    'data': wc_order
                }
            else:
                logger.error(f"❌ WooCommerce order creation failed: {response.status_code} - {response.text}")
                
                return {
                    'success': False,
                    'error': f"API returned status {response.status_code}",
                    'status_code': response.status_code,
                    'response_text': response.text
                }
        
        except Exception as e:
            logger.error(f"❌ Error sending order to WooCommerce: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_order_payload(self, order, shipping_cost=None):
        """
        Build WooCommerce API payload from Order model
        Adapts structure based on country

        Args:
            order: Order model instance
            shipping_cost: Optional shipping cost in Colombian pesos
        """
        # Determine shipping recipient based on order type
        if order.is_gift and order.receiver_username:
            # For gift orders, get receiver's shipping info from their profile
            shipping_name, shipping_phone, shipping_address = self._get_receiver_shipping_info(order.receiver_username)
        else:
            # For normal orders, use order's shipping info
            shipping_name = order.name
            shipping_phone = order.phone
            shipping_address = {
                'address_line_1': order.address_line_1,
                'address_line_2': order.address_line_2 if order.address_line_2 else '',
                'city': order.city,
                'state': order.state,
                'zipcode': order.zipcode if order.zipcode else '',
                'country': order.country,
                'additional_details': order.notes if order.notes else ''  # Use notes as additional details for normal orders
            }
        
        # Split shipping name into first_name and last_name
        name_parts = shipping_name.split(' ', 1)
        shipping_first_name = name_parts[0] if name_parts else ''
        shipping_last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Build line items (only from actual order items, no additional products)
        line_items = []
        for item in order.items.all():
            line_item = {
                'product_id': item.woocommerce_product_id,
                'quantity': item.quantity
            }
            # Add variation_id if present
            if item.woocommerce_variation_id:
                line_item['variation_id'] = item.woocommerce_variation_id

            line_items.append(line_item)
        
        # Fixed billing (your store info)
        billing = {
            'first_name': 'Doll',
            'last_name': 'House',
            'company': 'ITTE S.A.S',
            'address_1': 'CRA 69C 31 36 SUR ED GRIS PISO 4',
            'city': 'Bogotá, D.C.',
            'state': 'BOG',
            'postcode': '110110',
            'country': 'CO',
            'email': 'ittesas@gmail.com',
            'phone': '3123902346'
        }
        
        # Build shipping (recipient info - either customer or gift receiver)
        # Combine address_line_2 and additional_details if both exist
        address_2_combined = shipping_address['address_line_2']
        if shipping_address.get('additional_details'):
            if address_2_combined:
                address_2_combined += ' - ' + shipping_address['additional_details']
            else:
                address_2_combined = shipping_address['additional_details']
        
        shipping = {
            'first_name': shipping_first_name,
            'last_name': shipping_last_name,
            'company': '',
            'address_1': shipping_address['address_line_1'],
            'address_2': address_2_combined,
            'city': shipping_address['city'],
            'state': self._get_state_code(shipping_address['state']),
            'postcode': shipping_address['zipcode'],
            'country': shipping_address['country'],
            'phone': shipping_phone
        }
        
        # Base payload
        customer_note = order.notes if order.notes else ''
        if order.gift_message:
            if customer_note:
                customer_note += '\n\n' + order.gift_message
            else:
                customer_note = order.gift_message

        # Base payload
        payload = {
            'customer_id': self.STORE_CUSTOMER_ID,
            'status': 'on-hold',
            'set_paid': False,
            'billing': billing,
            'payment_method': 'bacs',
            'payment_method_title': 'Transferencia Bancaria',
            'line_items': line_items,
            'customer_note': customer_note
        }

        # Always add shipping address (recipient info)
        payload['shipping'] = shipping
        
        # Add shipping cost if provided
        if shipping_cost and shipping_cost > 0:
            # Use shipping cost directly (frontend sends Colombian pesos)
            payload['shipping_lines'] = [
                {
                    'method_id': 'flat_rate',
                    'method_title': 'Transportadora Servientrega',
                    'total': str(shipping_cost)
                }
            ]
            logger.info(f"📦 Added shipping_lines: {shipping_cost} for order {order.order_number}")
        
        # Add country-specific metadata
        if shipping_address['country'] == 'CO':
            payload['meta_data'] = self._build_colombian_metadata(order, shipping_address)
        
        return payload
    
    def _build_colombian_metadata(self, order, shipping_address):
        """
        Build Colombian-specific metadata
        Parses address and adds required fields
        
        Args:
            order: Order model instance
            shipping_address: Dictionary with shipping address info (recipient's address)
        """
        # Parse billing address (fixed store address: "CRA 69C 31 36 SUR ED GRIS PISO 4")
        billing_parsed = ColombianAddressParser.parse('CRA 69C 31 36 SUR ED GRIS PISO 4')
        
        # Parse shipping address (recipient's address - either customer or gift receiver)
        shipping_parsed = ColombianAddressParser.parse(shipping_address['address_line_1'])
        
        # Extract neighborhood from address_line_2 or use city
        shipping_neighborhood = shipping_address['address_line_2'] if shipping_address['address_line_2'] else shipping_address['city']
        
        meta_data = [
            # Billing metadata (fixed for your store - parsed from "CRA 69C 31 36 SUR ED GRIS PISO 4")
            {'key': '_billing_neighborhood', 'value': 'Centro'},  # Fixed neighborhood for store
            {'key': '_billing_street_1', 'value': billing_parsed['street_1']},
            {'key': '_billing_street_2', 'value': billing_parsed['street_2']},
            {'key': '_billing_street_3', 'value': billing_parsed['street_3']},
            {'key': '_billing_type_address', 'value': billing_parsed['type_address'] or 'Carrera'},
            {'key': '_billing_type_property', 'value': 'Oficina'},
            {'key': '_billing_unit_number', 'value': ''},
            
            # Cédula (empty for now, can be added to Order model later)
            {'key': '_cedula_', 'value': ''},
            
            # VAT exempt
            {'key': '_is_vat_exempt', 'value': 'no'},
            
            # Shipping metadata (customer - parsed from address)
            {'key': '_shipping_neighborhood', 'value': shipping_neighborhood},
            {'key': '_shipping_street_1', 'value': shipping_parsed['street_1']},
            {'key': '_shipping_street_2', 'value': shipping_parsed['street_2']},
            {'key': '_shipping_street_3', 'value': shipping_parsed['street_3']},
            {'key': '_shipping_type_address', 'value': shipping_parsed['type_address'] or 'Calle'},
            {'key': '_shipping_type_property', 'value': shipping_parsed['type_property'] or 'Casa'},
            {'key': '_shipping_unit_number', 'value': shipping_parsed['unit_number']},
            
            # WooCommerce B2B Sales Agent fields
            {'key': '_wcb2bsa_sales_agent', 'value': '4372'},
            {'key': '_wcb2bsa_created_by', 'value': 'customer'}
        ]
        
        return meta_data
    
    def _get_receiver_shipping_info(self, receiver_username):
        """
        Get shipping information for gift receiver from their user profile
        
        Args:
            receiver_username: Username of the gift receiver
            
        Returns:
            tuple: (name, phone, shipping_address_dict)
        """
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        try:
            receiver = User.objects.get(username=receiver_username)
            
            # Get receiver's name
            receiver_name = receiver.get_full_name() or receiver.username
            
            # Get receiver's phone (from profile)
            receiver_phone = receiver.phone or ''
            
            # Try to get receiver's default shipping address from UserAddress model
            default_address = receiver.addresses.filter(is_default_shipping=True).first()
            
            if not default_address:
                # If no default, get the most recent address
                default_address = receiver.addresses.order_by('-created_at').first()
            
            if default_address:
                shipping_address = {
                    'address_line_1': default_address.address_line_1,
                    'address_line_2': default_address.address_line_2 or '',
                    'city': default_address.city,
                    'state': default_address.state,
                    'zipcode': default_address.zip_code,
                    'country': default_address.country,
                    'additional_details': default_address.additional_details or ''
                }
                logger.info(f"🎁 Retrieved shipping address for gift receiver: {receiver_username}")
            else:
                # No address found for receiver
                logger.warning(f"⚠️ No address found for gift receiver {receiver_username}, using empty address")
                shipping_address = {
                    'address_line_1': '',
                    'address_line_2': '',
                    'city': '',
                    'state': '',
                    'zipcode': '',
                    'country': 'CO',
                    'additional_details': ''
                }
            
            return receiver_name, receiver_phone, shipping_address
            
        except User.DoesNotExist:
            logger.warning(f"⚠️ Gift receiver {receiver_username} not found, using empty address as fallback")
            # Fallback to empty/default values if receiver not found
            return receiver_username, '', {
                'address_line_1': '',
                'address_line_2': '',
                'city': '',
                'state': '',
                'zipcode': '',
                'country': 'CO',
                'additional_details': ''
            }
    
    def _get_state_code(self, state_name):
        """
        Convert state name to code (for Colombia)
        """
        colombian_states = {
            'ANTIOQUIA': 'ANT',
            'ATLANTICO': 'ATL',
            'BOGOTA': 'DC',
            'BOLIVAR': 'BOL',
            'BOYACA': 'BOY',
            'CALDAS': 'CAL',
            'CAQUETA': 'CAQ',
            'CAUCA': 'CAU',
            'CESAR': 'CES',
            'CORDOBA': 'COR',
            'CUNDINAMARCA': 'CUN',
            'CHOCO': 'CHO',
            'HUILA': 'HUI',
            'GUAJIRA': 'LAG',
            'MAGDALENA': 'MAG',
            'META': 'MET',
            'NARIÑO': 'NAR',
            'NORTE DE SANTANDER': 'NSA',
            'QUINDIO': 'QUI',
            'RISARALDA': 'RIS',
            'SANTANDER': 'SAN',
            'SUCRE': 'SUC',
            'TOLIMA': 'TOL',
            'VALLE DEL CAUCA': 'VAC',
            'ARAUCA': 'ARA',
            'CASANARE': 'CAS',
            'PUTUMAYO': 'PUT',
            'ARCHIPIELAGO DE SAN ANDRES': 'SAP',
            'AMAZONAS': 'AMA',
            'GUAINIA': 'GUA',
            'GUAVIARE': 'GUV',
            'VAUPES': 'VAU',
            'VICHADA': 'VID'
        }
        
        state_upper = state_name.upper()
        return colombian_states.get(state_upper, state_upper[:3])


# Singleton instance
woocommerce_order_service = WooCommerceOrderService()









