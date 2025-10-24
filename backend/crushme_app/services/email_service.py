"""
Email Service - Central email management for CrushMe
Handles all email sending with HTML templates
"""
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from pathlib import Path

logger = logging.getLogger(__name__)


class EmailService:
    """
    Centralized email service for sending templated emails
    """
    
    @staticmethod
    def send_email(
        to_email,
        subject,
        template_name='index.html',
        context=None,
        from_email=None,
        lang='es'
    ):
        """
        Send an email using HTML template
        
        Args:
            to_email (str or list): Recipient email(s)
            subject (str): Email subject
            template_name (str): Template filename (default: index.html)
            context (dict): Template context variables
            from_email (str): Sender email (optional, uses DEFAULT_FROM_EMAIL)
            lang (str): Language code ('es' or 'en', default: 'es')
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Ensure to_email is a list
            if isinstance(to_email, str):
                to_email = [to_email]
            
            # Set default context
            if context is None:
                context = {}
            
            # Set from_email
            if from_email is None:
                from_email = settings.DEFAULT_FROM_EMAIL
            
            # Validate language
            if lang not in ['es', 'en']:
                lang = 'es'  # Default to Spanish
            
            # Load template with language folder
            template_path = Path(settings.BASE_DIR) / 'email_templates' / lang / template_name
            
            # Read template file
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Simple template rendering (replace {{ variables }})
            for key, value in context.items():
                html_content = html_content.replace(f'{{{{ {key} }}}}', str(value))
            
            # Remove unused template variables
            import re
            html_content = re.sub(r'\{\%.*?\%\}', '', html_content)
            html_content = re.sub(r'\{\{.*?\}\}', '', html_content)
            
            # Create plain text version (strip HTML tags)
            text_content = re.sub('<[^<]+?>', '', html_content)
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_email
            )
            
            # Attach HTML version
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send(fail_silently=False)
            
            logger.info(f"✅ Email sent successfully to {to_email}: {subject}")
            return True
            
        except FileNotFoundError:
            logger.error(f"❌ Email template not found: {template_name}")
            return False
        except Exception as e:
            logger.error(f"❌ Error sending email to {to_email}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def send_verification_code(to_email, code, username, lang='es'):
        """
        Send email verification code
        
        Args:
            to_email (str): Recipient email
            code (str): 4-digit verification code
            username (str): User's username (required)
            lang (str): Language code ('es' or 'en', default: 'es')
        """
        context = {
            'code': code,
            'username': username
        }
        
        # Set subject based on language
        subject = 'Verifica tu correo - CrushMe' if lang == 'es' else 'Verify your email - CrushMe'
        
        return EmailService.send_email(
            to_email=to_email,
            subject=subject,
            template_name='1-signup-verification.html',
            context=context,
            lang=lang
        )
    
    @staticmethod
    def send_password_reset_code(to_email, code, username, lang='es'):
        """
        Send password reset code
        
        Args:
            to_email (str): Recipient email
            code (str): 4-digit reset code
            username (str): User's username (required)
            lang (str): Language code ('es' or 'en', default: 'es')
        """
        context = {
            'code': code,
            'username': username
        }
        
        # Set subject based on language
        subject = 'Recupera tu contraseña - CrushMe' if lang == 'es' else 'Reset your password - CrushMe'
        
        return EmailService.send_email(
            to_email=to_email,
            subject=subject,
            template_name='3-password-recovery.html',
            context=context,
            lang=lang
        )
    
    @staticmethod
    def send_order_confirmation(to_email, order_number, total, items, username, lang='es'):
        """
        Send order confirmation email
        
        Args:
            to_email (str): Recipient email
            order_number (str): Order number
            total (float): Order total amount
            items (list): List of order items
            username (str): User's username (required)
            lang (str): Language code ('es' or 'en', default: 'es')
        """
        context = {
            'order_number': order_number,
            'username': username
        }
        
        # Set subject based on language
        subject = f'Confirmación de pedido #{order_number} - CrushMe' if lang == 'es' else f'Order confirmation #{order_number} - CrushMe'
        
        return EmailService.send_email(
            to_email=to_email,
            subject=subject,
            template_name='4-order-confirmation.html',
            context=context,
            lang=lang
        )
    
    @staticmethod
    def send_gift_received_notification(to_email, sender_username, gift_message, order_number, username, lang='es'):
        """
        Send notification when user receives a gift
        
        Args:
            to_email (str): Recipient email
            sender_username (str): Username of person who sent the gift
            gift_message (str): Personal message from sender (optional)
            order_number (str): Order number
            username (str): Recipient's username (required)
            lang (str): Language code ('es' or 'en', default: 'es')
        """
        context = {
            'sender_username': sender_username,
            'username': username
        }
        
        # Set subject based on language
        subject = '¡Has recibido un regalo! 🎁 - CrushMe' if lang == 'es' else 'You received a gift! 🎁 - CrushMe'
        
        return EmailService.send_email(
            to_email=to_email,
            subject=subject,
            template_name='5-gift-received.html',
            context=context,
            lang=lang
        )
    
    @staticmethod
    def send_gift_sent_confirmation(to_email, receiver_username, order_number, username, lang='es'):
        """
        Send confirmation when user sends a gift
        
        Args:
            to_email (str): Sender's email
            receiver_username (str): Username of gift recipient
            order_number (str): Order number
            username (str): Sender's username (required)
            lang (str): Language code ('es' or 'en', default: 'es')
        """
        context = {
            'receiver_username': receiver_username,
            'username': username
        }
        
        # Set subject based on language
        subject = f'Regalo enviado a @{receiver_username} - CrushMe' if lang == 'es' else f'Gift sent to @{receiver_username} - CrushMe'
        
        return EmailService.send_email(
            to_email=to_email,
            subject=subject,
            template_name='6-gift-sent-confirmation.html',
            context=context,
            lang=lang
        )


# Create singleton instance
email_service = EmailService()
