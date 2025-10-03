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
    Each feed entry contains text content, a color theme, and timestamp.
    
    Attributes:
        user (ForeignKey): The user who created this feed post.
        text (TextField): The text content of the feed post.
        color (CharField): Hex color code for the feed post theme.
        created_at (DateTimeField): Timestamp when the post was created.
        updated_at (DateTimeField): Timestamp of last update.
    """
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
    
    color = models.CharField(
        max_length=7,
        default="#000000",
        verbose_name="Color",
        help_text="Código hexadecimal del color (ej: #FF5733)",
        validators=[RegexValidator(
            regex=r'^#[0-9A-Fa-f]{6}$',
            message="El color debe ser un código hexadecimal válido (ej: #FF5733)"
        )]
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

    class Meta:
        verbose_name = "Feed Post"
        verbose_name_plural = "Feed Posts"
        ordering = ['-created_at']  # Más recientes primero
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]



