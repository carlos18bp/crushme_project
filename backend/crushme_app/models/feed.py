"""
Feed model for user posts/updates
Allows users to share text updates with color themes
"""
from django.db import models
from django.core.validators import RegexValidator
from .user import User


class Feed(models.Model):
    """
    Model to store user feed posts/updates.
    Each feed entry contains text content, action type, and timeline style.
    
    Attributes:
        user (ForeignKey): The user who created this feed post.
        text (TextField): The text content of the feed post.
        action (CharField): Action type that triggered this feed entry.
        style (CharField): Timeline style theme for the post.
        created_at (DateTimeField): Timestamp when the post was created.
        updated_at (DateTimeField): Timestamp of last update.
    """
    
    # Action choices - events that trigger feed entries
    ACTION_CHOICES = [
        ('signup', 'User Signup'),
        ('password_reset', 'Password Reset'),
        ('order_confirmation', 'Order Confirmation'),
        ('gift_sent', 'Gift Sent'),
        ('gift_received', 'Gift Received'),
        ('general', 'General Post'),
    ]
    
    # Style choices for timeline themes (mapped to actions)
    STYLE_CHOICES = [
        ('timeline-pink-dream', 'Pink Dream'),
        ('timeline-purple-passion', 'Purple Passion'),
        ('timeline-rose-blush', 'Rose Blush'),
        ('timeline-ocean-blue', 'Ocean Blue'),
        ('timeline-coral-sunset', 'Coral Sunset'),
        ('timeline-midnight-rose', 'Midnight Rose'),
    ]
    
    # Action to Style mapping
    ACTION_STYLE_MAP = {
        'signup': 'timeline-pink-dream',
        'password_reset': 'timeline-purple-passion',
        'order_confirmation': 'timeline-rose-blush',
        'gift_sent': 'timeline-ocean-blue',
        'gift_received': 'timeline-coral-sunset',
        'general': 'timeline-midnight-rose',
    }
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='feeds',
        verbose_name="Usuario"
    )
    
    text = models.TextField(
        max_length=1000,
        verbose_name="Texto",
        help_text="Contenido del post (máximo 1000 caracteres)"
    )
    
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        default='general',
        verbose_name="Acción",
        help_text="Tipo de acción que generó este post"
    )
    
    style = models.CharField(
        max_length=50,
        choices=STYLE_CHOICES,
        default='timeline-midnight-rose',
        verbose_name="Estilo",
        help_text="Tema visual del post en el timeline"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )

    def __str__(self):
        """
        String representation of the Feed instance.
        
        Returns:
            str: Username and truncated text.
        """
        text_preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"{self.user.username or self.user.email} - {text_preview}"
    
    @staticmethod
    def get_message_for_action(action, lang='es', **kwargs):
        """
        Get predefined message for each action type in specified language.
        
        Args:
            action (str): Action type (signup, password_reset, etc.)
            lang (str): Language code ('es' or 'en')
            **kwargs: Additional parameters like username, receiver_username, etc.
        
        Returns:
            str: Formatted message with emoji
        """
        username = kwargs.get('username', '')
        receiver_username = kwargs.get('receiver_username', '')
        sender_username = kwargs.get('sender_username', '')
        
        messages = {
            'signup': {
                'es': f'🎉 ¡Bienvenido a CrushMe, @{username}! Tu aventura comienza ahora',
                'en': f'🎉 Welcome to CrushMe, @{username}! Your adventure starts now'
            },
            'password_reset': {
                'es': f'🔐 @{username} cambió su contraseña exitosamente',
                'en': f'🔐 @{username} successfully changed their password'
            },
            'order_confirmation': {
                'es': f'🛍️ @{username} realizó una compra. ¡Disfruta tus productos!',
                'en': f'🛍️ @{username} made a purchase. Enjoy your products!'
            },
            'gift_sent': {
                'es': f'🎁 @{username} envió un regalo a @{receiver_username}',
                'en': f'🎁 @{username} sent a gift to @{receiver_username}'
            },
            'gift_received': {
                'es': f'💝 @{username} recibió un regalo de @{sender_username}',
                'en': f'💝 @{username} received a gift from @{sender_username}'
            },
            'general': {
                'es': f'📝 @{username} publicó una actualización',
                'en': f'📝 @{username} posted an update'
            }
        }
        
        return messages.get(action, messages['general']).get(lang, messages[action]['es'])
    
    @staticmethod
    def create_feed_entry(user, action, lang='es', **kwargs):
        """
        Create a feed entry automatically for an action.
        
        Args:
            user (User): User instance
            action (str): Action type
            lang (str): Language code ('es' or 'en')
            **kwargs: Additional parameters for message formatting
        
        Returns:
            Feed: Created feed instance
        """
        # Get predefined message
        kwargs['username'] = user.username
        message = Feed.get_message_for_action(action, lang, **kwargs)
        
        # Get style for this action
        style = Feed.ACTION_STYLE_MAP.get(action, 'timeline-midnight-rose')
        
        # Create feed entry
        feed = Feed.objects.create(
            user=user,
            text=message,
            action=action,
            style=style
        )
        
        return feed

    class Meta:
        verbose_name = "Feed Post"
        verbose_name_plural = "Feed Posts"
        ordering = ['-created_at']  # Más recientes primero
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]



