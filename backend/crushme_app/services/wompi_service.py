"""
Wompi Payment Service
Handles Wompi payment integration for Colombian market (COP only)
API Documentation: https://docs.wompi.co/
"""
import requests
import hashlib
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
        self.timeout = 30
    
    def create_transaction(self, amount_in_cents, reference, customer_email, 
                          customer_name, redirect_url, phone_number='', currency='COP'):
        """
        Create a Wompi payment transaction
        
        Args:
            amount_in_cents: Amount in cents (e.g., 10000 = $100.00 COP)
            reference: Unique reference for this transaction (e.g., order number)
            customer_email: Customer email address
            customer_name: Customer full name
            redirect_url: URL to redirect after payment
            phone_number: Customer phone number (required by Wompi)
            currency: Currency code (default: COP)
        
        Returns:
            dict: Transaction response with transaction_id and payment URL
        """
        try:
            # Generate integrity signature
            # Format: reference + amount_in_cents + currency + integrity_key
            # Documentación: https://docs.wompi.co/docs/en/widgets-checkout#firma-de-integridad
            integrity_string = f"{reference}{amount_in_cents}{currency}{self.integrity_key}"
            integrity_signature = hashlib.sha256(integrity_string.encode()).hexdigest()
            
            logger.info(f"🔐 [WOMPI] Integrity string: {reference}{amount_in_cents}{currency}[INTEGRITY_KEY]")
            logger.info(f"🔐 [WOMPI] Integrity signature: {integrity_signature}")
            
            # Build payment link payload
            payload = {
                'name': f'Orden {reference}',  # Required
                'description': 'Compra en CrushMe',  # Required
                'single_use': True,  # Required - Link solo se puede usar una vez
                'collect_shipping': False,  # Required - Ya tenemos la dirección
                'amount_in_cents': int(amount_in_cents),
                'currency': currency,
                'reference': reference,
                'redirect_url': redirect_url,
                'customer_data': {
                    'email': customer_email,
                    'full_name': customer_name,
                    'phone_number': phone_number,
                }
            }
            
            # Create payment link (allows user to select payment method)
            url = f"{self.base_url}/payment_links"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.private_key}'  # Payment links use private key
            }
            
            logger.info(f"🔵 [WOMPI] Creating payment link for reference: {reference}")
            logger.debug(f"Payload: {payload}")
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201]:
                payment_link_data = response.json()
                data = payment_link_data.get('data', {})
                
                # Log completo para debugging
                logger.info(f"✅ [WOMPI] Payment link created: {data.get('id')}")
                logger.info(f"🔍 [WOMPI] Full response data: {data}")
                
                # Construir URL del checkout manualmente
                # Wompi no retorna la URL, se construye con el ID del payment link
                payment_link_id = data.get('id')
                payment_url = f"https://checkout.wompi.co/l/{payment_link_id}"
                
                logger.info(f"🔗 [WOMPI] Payment URL constructed: {payment_url}")
                
                return {
                    'success': True,
                    'transaction_id': payment_link_id,
                    'payment_url': payment_url,
                    'status': 'PENDING',
                    'data': payment_link_data
                }
            else:
                logger.error(f"❌ [WOMPI] Transaction creation failed: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"Transaction creation failed: {response.status_code}",
                    'details': response.text
                }
        
        except Exception as e:
            logger.error(f"❌ [WOMPI] Transaction creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
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
                logger.error(f"❌ [WOMPI] Get transaction failed: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"Get transaction failed: {response.status_code}",
                    'details': response.text
                }
        
        except Exception as e:
            logger.error(f"❌ [WOMPI] Get transaction error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_signature(self, event_data, signature):
        """
        Verify webhook signature from Wompi
        
        Args:
            event_data: Event data from webhook
            signature: Signature from webhook headers
        
        Returns:
            bool: True if signature is valid
        """
        try:
            # Wompi sends signature in format: timestamp.signature
            # We need to verify using events_secret
            # Format: timestamp.event_id.status.amount_in_cents
            
            timestamp = event_data.get('timestamp')
            event_id = event_data.get('event', {}).get('id')
            status = event_data.get('data', {}).get('status')
            amount = event_data.get('data', {}).get('amount_in_cents')
            
            verification_string = f"{timestamp}.{event_id}.{status}.{amount}.{self.events_secret}"
            calculated_signature = hashlib.sha256(verification_string.encode()).hexdigest()
            
            is_valid = calculated_signature == signature
            
            if is_valid:
                logger.info(f"✅ [WOMPI] Webhook signature verified")
            else:
                logger.warning(f"⚠️ [WOMPI] Invalid webhook signature")
            
            return is_valid
        
        except Exception as e:
            logger.error(f"❌ [WOMPI] Signature verification error: {str(e)}")
            return False


# Singleton instance
wompi_service = WompiService()
