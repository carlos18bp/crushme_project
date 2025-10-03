"""
Contact model for handling contact form submissions
Stores user inquiries and messages
"""
from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator


class Contact(models.Model):
    """
    Contact form model for user inquiries
    Stores contact information and message details
    """
    
    # Contact information
    email = models.EmailField(
        validators=[EmailValidator()],
        verbose_name="Email",
        help_text="Email del contacto"
    )
    
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre",
        help_text="Nombre completo del contacto"
    )
    
    numero = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Número de Teléfono",
        help_text="Número de teléfono del contacto (opcional)"
    )
    
    asunto = models.CharField(
        max_length=200,
        verbose_name="Asunto",
        help_text="Asunto del mensaje"
    )
    
    texto = models.TextField(
        verbose_name="Mensaje",
        help_text="Contenido del mensaje"
    )
    
    # Status tracking
    is_read = models.BooleanField(
        default=False,
        verbose_name="Leído",
        help_text="Si el mensaje ha sido leído por el administrador"
    )
    
    is_responded = models.BooleanField(
        default=False,
        verbose_name="Respondido",
        help_text="Si el mensaje ha sido respondido"
    )
    
    # Admin notes
    admin_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notas del Administrador",
        help_text="Notas internas del administrador"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de Creación"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    
    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_read']),
            models.Index(fields=['is_responded']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"Contacto de {self.nombre} - {self.asunto}"
    
    def mark_as_read(self):
        """Mark the contact message as read"""
        self.is_read = True
        self.save(update_fields=['is_read', 'updated_at'])
    
    def mark_as_responded(self):
        """Mark the contact message as responded"""
        self.is_responded = True
        self.save(update_fields=['is_responded', 'updated_at'])



