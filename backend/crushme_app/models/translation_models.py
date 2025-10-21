"""
Translation Cache Models
Pre-translated content for fast delivery
"""
from django.db import models
from django.utils import timezone


class TranslatedContent(models.Model):
    """
    Cache de traducciones pre-calculadas para productos y categorías.
    Permite respuestas ultra rápidas sin traducir en tiempo real.
    """
    
    # Content type
    CONTENT_TYPE_PRODUCT_NAME = 'product_name'
    CONTENT_TYPE_PRODUCT_SHORT_DESC = 'product_short_desc'
    CONTENT_TYPE_PRODUCT_DESC = 'product_desc'
    CONTENT_TYPE_CATEGORY_NAME = 'category_name'
    CONTENT_TYPE_CATEGORY_DESC = 'category_desc'
    CONTENT_TYPE_VARIATION_ATTRIBUTE = 'variation_attribute'
    
    CONTENT_TYPE_CHOICES = [
        (CONTENT_TYPE_PRODUCT_NAME, 'Product Name'),
        (CONTENT_TYPE_PRODUCT_SHORT_DESC, 'Product Short Description'),
        (CONTENT_TYPE_PRODUCT_DESC, 'Product Description'),
        (CONTENT_TYPE_CATEGORY_NAME, 'Category Name'),
        (CONTENT_TYPE_CATEGORY_DESC, 'Category Description'),
        (CONTENT_TYPE_VARIATION_ATTRIBUTE, 'Variation Attribute'),
    ]
    
    # Identificación del contenido
    content_type = models.CharField(
        max_length=30,
        choices=CONTENT_TYPE_CHOICES,
        db_index=True,
        verbose_name="Content Type"
    )
    object_id = models.IntegerField(db_index=True, verbose_name="WooCommerce ID")
    
    # Idiomas
    source_language = models.CharField(max_length=5, default='es', verbose_name="Source Language")
    target_language = models.CharField(max_length=5, db_index=True, verbose_name="Target Language")
    
    # Contenido
    source_text = models.TextField(verbose_name="Original Text")
    translated_text = models.TextField(verbose_name="Translated Text")
    
    # Metadata
    translation_engine = models.CharField(max_length=50, default='argostranslate', verbose_name="Translation Engine")
    is_verified = models.BooleanField(default=False, verbose_name="Manually Verified")
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    class Meta:
        verbose_name = "Translated Content"
        verbose_name_plural = "Translated Contents"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id', 'target_language']),
            models.Index(fields=['object_id', 'content_type']),
            models.Index(fields=['target_language']),
        ]
        # Cada combinación debe ser única
        unique_together = [['content_type', 'object_id', 'target_language']]
    
    def __str__(self):
        return f"{self.get_content_type_display()} #{self.object_id} → {self.target_language}"


class CategoryPriceMargin(models.Model):
    """
    Márgenes de precio por categoría.
    Los precios finales se calculan aplicando este margen sobre el precio base de WooCommerce.
    """
    
    # Categoría (relación con WooCommerceCategory)
    category = models.OneToOneField(
        'WooCommerceCategory',
        on_delete=models.CASCADE,
        related_name='price_margin',
        verbose_name="Category"
    )
    
    # Margen de ganancia (porcentaje)
    margin_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Porcentaje de margen (ej: 30.00 para 30%)",
        verbose_name="Margin Percentage"
    )
    
    # Opción: usar precio fijo en lugar de margen
    use_fixed_multiplier = models.BooleanField(
        default=False,
        help_text="Usar multiplicador fijo en lugar de margen porcentual",
        verbose_name="Use Fixed Multiplier"
    )
    fixed_multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        help_text="Multiplicador fijo (ej: 1.30 para +30%)",
        verbose_name="Fixed Multiplier"
    )
    
    # Estado
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    # Notas
    notes = models.TextField(blank=True, default='', verbose_name="Notes")
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    class Meta:
        verbose_name = "Category Price Margin"
        verbose_name_plural = "Category Price Margins"
        ordering = ['category__name']
    
    def __str__(self):
        if self.use_fixed_multiplier:
            return f"{self.category.name}: x{self.fixed_multiplier}"
        return f"{self.category.name}: +{self.margin_percentage}%"
    
    def calculate_price(self, base_price):
        """
        Calcula el precio final aplicando el margen.
        
        Args:
            base_price: Precio base de WooCommerce
            
        Returns:
            Precio final con margen aplicado
        """
        if not self.is_active or base_price is None:
            return base_price
        
        if self.use_fixed_multiplier:
            return float(base_price) * float(self.fixed_multiplier)
        else:
            # Calcular con margen porcentual
            margin_multiplier = 1 + (float(self.margin_percentage) / 100)
            return float(base_price) * margin_multiplier


class DefaultPriceMargin(models.Model):
    """
    Margen de precio por defecto para productos sin categoría específica.
    Solo puede haber un registro activo.
    """
    
    margin_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20.00,
        help_text="Porcentaje de margen por defecto",
        verbose_name="Default Margin Percentage"
    )
    
    use_fixed_multiplier = models.BooleanField(
        default=False,
        verbose_name="Use Fixed Multiplier"
    )
    fixed_multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.20,
        verbose_name="Fixed Multiplier"
    )
    
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    notes = models.TextField(blank=True, default='', verbose_name="Notes")
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    class Meta:
        verbose_name = "Default Price Margin"
        verbose_name_plural = "Default Price Margins"
    
    def __str__(self):
        if self.use_fixed_multiplier:
            return f"Default: x{self.fixed_multiplier}"
        return f"Default: +{self.margin_percentage}%"
    
    def calculate_price(self, base_price):
        """Calculate final price with default margin"""
        if not self.is_active or base_price is None:
            return base_price
        
        if self.use_fixed_multiplier:
            return float(base_price) * float(self.fixed_multiplier)
        else:
            margin_multiplier = 1 + (float(self.margin_percentage) / 100)
            return float(base_price) * margin_multiplier
    
    @classmethod
    def get_active(cls):
        """Get the active default margin configuration"""
        return cls.objects.filter(is_active=True).first()
