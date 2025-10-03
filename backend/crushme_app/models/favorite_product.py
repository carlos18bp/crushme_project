"""
Favorite Products Model
Allows users to save individual WooCommerce products as favorites
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class FavoriteProduct(models.Model):
    """
    Model to track user's favorite products from WooCommerce.
    Stores only the WooCommerce product ID and caches product data for performance.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_products',
        verbose_name="User"
    )
    
    # WooCommerce product ID (external reference)
    woocommerce_product_id = models.IntegerField(
        verbose_name="WooCommerce Product ID",
        help_text="ID del producto en WooCommerce",
        db_index=True
    )
    
    # Cache product data from WooCommerce (for performance)
    product_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Product Data Cache",
        help_text="Cached product information from WooCommerce (name, price, image, etc.)"
    )
    
    # Timestamp when cache was last updated
    cache_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Cache Updated At",
        help_text="Last time product data was fetched from WooCommerce"
    )
    
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Created At"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )
    
    class Meta:
        verbose_name = "Favorite Product"
        verbose_name_plural = "Favorite Products"
        unique_together = ['user', 'woocommerce_product_id']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['woocommerce_product_id']),
        ]
    
    def __str__(self):
        product_name = self.product_data.get('name', f'Product {self.woocommerce_product_id}')
        return f"{self.user.email} - {product_name}"
    
    @classmethod
    def add_favorite(cls, user, woocommerce_product_id, product_data=None):
        """
        Add a product to user's favorites
        
        Args:
            user: User instance
            woocommerce_product_id: ID of the product in WooCommerce
            product_data: Optional cached product data from WooCommerce
        
        Returns:
            tuple: (favorite, created) - FavoriteProduct instance and boolean
        """
        defaults = {}
        if product_data:
            defaults['product_data'] = product_data
            defaults['cache_updated_at'] = timezone.now()
        
        favorite, created = cls.objects.get_or_create(
            user=user,
            woocommerce_product_id=woocommerce_product_id,
            defaults=defaults
        )
        
        # If not created but product_data was provided, update it
        if not created and product_data:
            favorite.product_data = product_data
            favorite.cache_updated_at = timezone.now()
            favorite.save(update_fields=['product_data', 'cache_updated_at', 'updated_at'])
        
        return favorite, created
    
    @classmethod
    def remove_favorite(cls, user, woocommerce_product_id):
        """
        Remove a product from user's favorites
        
        Args:
            user: User instance
            woocommerce_product_id: ID of the product in WooCommerce
        
        Returns:
            bool: True if removed, False if not found
        """
        try:
            favorite = cls.objects.get(user=user, woocommerce_product_id=woocommerce_product_id)
            favorite.delete()
            return True
        except cls.DoesNotExist:
            return False
    
    @classmethod
    def is_favorited(cls, user, woocommerce_product_id):
        """
        Check if user has favorited a product
        
        Args:
            user: User instance
            woocommerce_product_id: ID of the product in WooCommerce
        
        Returns:
            bool: True if favorited, False otherwise
        """
        if not user.is_authenticated:
            return False
        return cls.objects.filter(user=user, woocommerce_product_id=woocommerce_product_id).exists()
    
    @classmethod
    def get_user_favorites(cls, user):
        """
        Get all products favorited by a user
        
        Args:
            user: User instance
        
        Returns:
            QuerySet: FavoriteProduct queryset
        """
        return cls.objects.filter(user=user).select_related('user')
    
    @classmethod
    def get_user_favorite_ids(cls, user):
        """
        Get list of WooCommerce product IDs favorited by a user
        
        Args:
            user: User instance
        
        Returns:
            list: List of product IDs
        """
        return list(cls.objects.filter(user=user).values_list('woocommerce_product_id', flat=True))
    
    def update_product_cache(self, product_data):
        """
        Update cached product data
        
        Args:
            product_data: Product data dict from WooCommerce
        """
        self.product_data = product_data
        self.cache_updated_at = timezone.now()
        self.save(update_fields=['product_data', 'cache_updated_at', 'updated_at'])
    
    def needs_cache_refresh(self, max_age_hours=24):
        """
        Check if cached product data needs refreshing
        
        Args:
            max_age_hours: Maximum age of cache in hours (default 24)
        
        Returns:
            bool: True if cache is stale or missing
        """
        if not self.cache_updated_at:
            return True
        
        age = timezone.now() - self.cache_updated_at
        return age.total_seconds() > (max_age_hours * 3600)


