"""
Wompi Payment Service
Handles Wompi payment integration for Colombian market (COP only)
API Documentation: https://docs.wompi.co/
"""
import requests
import hashlib
import hmac
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class WompiService:
    """
    Service to handle Wompi payment processing
    Wompi is a Colombian payment gateway that supports local payment methods
    """
    
    def __init__(self):
        self.public_key = getattr(settings, 'WOMPI_PUBLIC_KEY', '')
        self.private_key = getattr(settings, 'WOMPI_PRIVATE_KEY', '')
        self.events_secret = getattr(settings, 'WOMPI_EVENTS_SECRET', '')
        self.integrity_key = getattr(settings, 'WOMPI_INTEGRITY_KEY', '')  # Para firmar transacciones
        self.base_url = getattr(settings, 'WOMPI_BASE_URL', 'https://production.wompi.co/v1')
        self.checkout_url = getattr(settings, 'WOMPI_CHECKOUT_URL', 'https://checkout.wompi.co')
        self.timeout = 30
    
    def create_transaction(self, amount_in_cents, reference, customer_email, 
                          customer_name, redirect_url, phone_number='', currency='COP'):
        """
        Create Wompi Widget transaction data (no longer creates payment link)
        
        Args:
            amount_in_cents: Amount in cents (e.g., 10000 = $100.00 COP)
            reference: Unique reference for this transaction (e.g., order number)
            customer_email: Customer email address
            customer_name: Customer full name
            redirect_url: URL to redirect after payment
            phone_number: Customer phone number (optional for widget)
            currency: Currency code (default: COP)
        
        Returns:
            dict: Widget configuration data with integrity signature
        """
        try:
            # Generate integrity signature
            # Format: reference + amount_in_cents + currency + integrity_key
            # Documentación: https://docs.wompi.co/docs/en/widgets-checkout#firma-de-integridad
            integrity_string = f"{reference}{amount_in_cents}{currency}{self.integrity_key}"
            integrity_signature = hashlib.sha256(integrity_string.encode()).hexdigest()
            
            logger.info(f"🔐 [WOMPI] Integrity string: {reference}{amount_in_cents}{currency}[INTEGRITY_KEY]")
            logger.info(f"🔗 [WOMPI] Redirect URL: {redirect_url}")
            
            # Return widget configuration data
            # El frontend usará estos datos para inicializar el widget de Wompi
            # Documentación: https://docs.wompi.co/en/docs/colombia/widget-checkout-web/
            
            # Separar phone_number en prefix y number
            # Formato esperado: "+57 300 1234567" o "300 1234567"
            phone_prefix = '+57'
            phone_only = phone_number
            
            if phone_number:
                # Si tiene +, extraer el prefijo
                if phone_number.startswith('+'):
                    parts = phone_number.split(' ', 1)
                    if len(parts) == 2:
                        phone_prefix = parts[0]
                        phone_only = parts[1].replace(' ', '')
                    else:
                        phone_only = phone_number[3:].replace(' ', '')  # Remover +57 y espacios
                else:
                    phone_only = phone_number.replace(' ', '')
            
            widget_data = {
                'public_key': self.public_key,
                'currency': currency,
                'amount_in_cents': int(amount_in_cents),
                'reference': reference,
                'signature': integrity_signature,
                'redirect_url': redirect_url,
                'customer_data': {
                    'email': customer_email,
                    'full_name': customer_name,
                    'phone_number': phone_only,
                    'phone_number_prefix': phone_prefix,
                }
            }
            
            logger.info(f"✅ [WOMPI] Widget data prepared for reference: {reference}")
            logger.info(f"💰 [WOMPI] Amount: {amount_in_cents} cents ({amount_in_cents/100} {currency})")
            
            return {
                'success': True,
                'widget_data': widget_data,
                'reference': reference,
                'status': 'PENDING'
            }
        
        except Exception:
            logger.exception('[WOMPI] Transaction preparation failed')
            return {
                'success': False,
                'error': 'Transaction preparation failed'
            }
    
    def get_transaction(self, transaction_id):
        """
        Get transaction details and status
        
        Args:
            transaction_id: Wompi transaction ID
        
        Returns:
            dict: Transaction details with status
        """
        try:
            url = f"{self.base_url}/transactions/{transaction_id}"
            headers = {
                'Authorization': f'Bearer {self.public_key}'
            }
            
            logger.info(f"🔵 [WOMPI] Getting transaction: {transaction_id}")
            
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                transaction_data = response.json()
                data = transaction_data.get('data', {})
                
                logger.info(f"✅ [WOMPI] Transaction retrieved: {transaction_id} - Status: {data.get('status')}")
                
                return {
                    'success': True,
                    'transaction_id': data.get('id'),
                    'status': data.get('status'),  # APPROVED, DECLINED, PENDING, etc.
                    'amount_in_cents': data.get('amount_in_cents'),
                    'currency': data.get('currency'),
                    'reference': data.get('reference'),
                    'customer_email': data.get('customer_email'),
                    'payment_method': data.get('payment_method_type'),
                    'data': transaction_data
                }
            else:
                logger.error(
                    '[WOMPI] Transaction lookup failed with status %s',
                    response.status_code,
                )
                return {
                    'success': False,
                    'error': f"Get transaction failed: {response.status_code}",
                }
        
        except Exception:
            logger.exception('[WOMPI] Transaction lookup request failed')
            return {
                'success': False,
                'error': 'Transaction lookup request failed'
            }
    
    @staticmethod
    def _resolve_signature_property(data, property_path):
        """Resolve a Wompi signature property relative to the event data object."""
        value = data
        for segment in property_path.split('.'):
            if not isinstance(value, dict) or segment not in value:
                raise ValueError('Signature property is missing from event data')
            value = value[segment]

        if value is None or isinstance(value, (dict, list)):
            raise ValueError('Signature properties must resolve to scalar values')
        if isinstance(value, bool):
            return 'true' if value else 'false'
        return str(value)

    def verify_signature(self, event_data, signature=None):
        """
        Verify webhook signature from Wompi
        
        Args:
            event_data: Event data from webhook
            signature: Optional checksum from the X-Event-Checksum header
        
        Returns:
            bool: True if signature is valid
        """
        try:
            if not self.events_secret or not isinstance(event_data, dict):
                return False

            signature_data = event_data.get('signature')
            data = event_data.get('data')
            timestamp = event_data.get('timestamp')
            if not isinstance(signature_data, dict) or not isinstance(data, dict):
                return False
            if timestamp is None or isinstance(timestamp, bool):
                return False

            properties = signature_data.get('properties')
            payload_checksum = signature_data.get('checksum')
            if not isinstance(properties, list) or not properties:
                return False
            if not all(isinstance(path, str) and path for path in properties):
                return False

            provided_checksum = signature or payload_checksum
            if not isinstance(provided_checksum, str) or not provided_checksum:
                return False
            if signature and payload_checksum and not hmac.compare_digest(
                signature.lower(), str(payload_checksum).lower()
            ):
                return False

            signed_values = ''.join(
                self._resolve_signature_property(data, path)
                for path in properties
            )
            verification_string = f'{signed_values}{timestamp}{self.events_secret}'
            calculated_checksum = hashlib.sha256(
                verification_string.encode('utf-8')
            ).hexdigest()

            is_valid = hmac.compare_digest(
                calculated_checksum.lower(), provided_checksum.lower()
            )
            if not is_valid:
                logger.warning('[WOMPI] Rejected webhook with invalid checksum')
            return is_valid
        except (TypeError, ValueError):
            logger.warning('[WOMPI] Rejected malformed webhook signature payload')
            return False


# Singleton instance
wompi_service = WompiService()
