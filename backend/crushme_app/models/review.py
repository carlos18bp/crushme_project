"""
Review model for WooCommerce products
Reviews are tied to WooCommerce product IDs, not local Product model
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from .user import User


class Review(models.Model):
    """
    Product review model for WooCommerce products only
    Uses WooCommerce product ID as the reference (not local Product model)
    """
    
    # WooCommerce product ID (external reference)
    woocommerce_product_id = models.IntegerField(
        verbose_name="WooCommerce Product ID",
        help_text="ID del producto en WooCommerce",
        db_index=True
    )
    
    # User who made the review (optional - can be anonymous)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
        verbose_name="Usuario",
        help_text="Usuario que hizo la reseña (opcional para anónimos)"
    )
    
    # Anonymous user information (if user is not logged in)
    anonymous_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Nombre Anónimo",
        help_text="Nombre del usuario anónimo"
    )
    
    anonymous_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email Anónimo",
        help_text="Email del usuario anónimo"
    )
    
    # Review content
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Calificación",
        help_text="Calificación del producto (1-5 estrellas)"
    )
    
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Título",
        help_text="Título de la reseña"
    )
    
    comment = models.TextField(
        verbose_name="Comentario",
        help_text="Comentario detallado de la reseña"
    )
    
    # Moderation
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activa",
        help_text="Si la reseña está aprobada y visible"
    )
    
    is_verified_purchase = models.BooleanField(
        default=False,
        verbose_name="Compra Verificada",
        help_text="Si es una reseña de una compra verificada"
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
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['woocommerce_product_id', '-created_at']),
            models.Index(fields=['is_active']),
            models.Index(fields=['rating']),
            models.Index(fields=['user']),
        ]
        # Un usuario solo puede hacer una review por producto
        unique_together = [['user', 'woocommerce_product_id']]
    
    def __str__(self):
        user_display = self.user.email if self.user else self.anonymous_name or "Anónimo"
        return f"Review de {user_display} - Producto {self.woocommerce_product_id} ({self.rating}★)"
    
    @property
    def reviewer_name(self):
        """Get the username of the reviewer (user or anonymous)"""
        if self.user:
            return self.user.username
        return self.anonymous_name or "Usuario Anónimo"
    
    @property
    def reviewer_email(self):
        """Get the email of the reviewer"""
        if self.user:
            return self.user.email
        return self.anonymous_email
    
    @classmethod
    def get_product_reviews(cls, woocommerce_product_id, active_only=True):
        """Get all reviews for a specific WooCommerce product"""
        queryset = cls.objects.filter(woocommerce_product_id=woocommerce_product_id)
        if active_only:
            queryset = queryset.filter(is_active=True)
        return queryset
    
    @classmethod
    def get_product_average_rating(cls, woocommerce_product_id):
        """Calculate average rating for a WooCommerce product"""
        from django.db.models import Avg
        result = cls.objects.filter(
            woocommerce_product_id=woocommerce_product_id,
            is_active=True
        ).aggregate(avg_rating=Avg('rating'))
        return result['avg_rating'] or 0
    
    @classmethod
    def get_product_stats(cls, woocommerce_product_id):
        """Get review statistics for a WooCommerce product"""
        from django.db.models import Count, Avg
        reviews = cls.objects.filter(
            woocommerce_product_id=woocommerce_product_id,
            is_active=True
        )
        
        stats = reviews.aggregate(
            total_reviews=Count('id'),
            average_rating=Avg('rating')
        )
        
        # Count by rating (1-5 stars)
        rating_counts = {}
        for i in range(1, 6):
            rating_counts[f'stars_{i}'] = reviews.filter(rating=i).count()
        
        return {
            'total_reviews': stats['total_reviews'] or 0,
            'average_rating': round(stats['average_rating'] or 0, 2),
            'rating_distribution': rating_counts
        }



