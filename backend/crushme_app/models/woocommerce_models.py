"""
WooCommerce synchronized models
These models store WooCommerce data locally for faster access
"""
from django.db import models
from django.utils import timezone
import json


class WooCommerceCategory(models.Model):
    """
    Categoría sincronizada desde WooCommerce.
    Se actualiza periódicamente (1 vez al día).
    """
    # WooCommerce ID
    wc_id = models.IntegerField(unique=True, db_index=True, verbose_name="WooCommerce ID")
    
    # Basic info (Spanish - original from WooCommerce)
    name = models.CharField(max_length=255, verbose_name="Category Name")
    slug = models.SlugField(max_length=255, db_index=True, verbose_name="Slug")
    description = models.TextField(blank=True, default='', verbose_name="Description")
    
    # Hierarchy (parent_id will be auto-created by Django from parent ForeignKey)
    wc_parent_id = models.IntegerField(default=0, db_index=True, verbose_name="WooCommerce Parent ID")
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Parent Category"
    )
    
    # Stats
    product_count = models.IntegerField(default=0, verbose_name="Product Count")
    
    # Image
    image_url = models.URLField(max_length=500, blank=True, default='', verbose_name="Image URL")
    
    # Display
    display_order = models.IntegerField(default=0, verbose_name="Display Order")
    
    # Timestamps
    synced_at = models.DateTimeField(auto_now=True, verbose_name="Last Synced At")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    
    class Meta:
        verbose_name = "WooCommerce Category"
        verbose_name_plural = "WooCommerce Categories"
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['wc_id']),
            models.Index(fields=['slug']),
            models.Index(fields=['wc_parent_id']),
        ]
    
    def __str__(self):
        return f"{self.name} (ID: {self.wc_id})"
    
    def get_full_path(self):
        """Get full category path (e.g., 'Parent > Child > This')"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class WooCommerceProduct(models.Model):
    """
    Producto sincronizado desde WooCommerce.
    Almacena toda la información excepto stock y precio (que se consultan en tiempo real).
    """
    
    # Product types
    TYPE_SIMPLE = 'simple'
    TYPE_GROUPED = 'grouped'
    TYPE_EXTERNAL = 'external'
    TYPE_VARIABLE = 'variable'
    
    TYPE_CHOICES = [
        (TYPE_SIMPLE, 'Simple'),
        (TYPE_GROUPED, 'Grouped'),
        (TYPE_EXTERNAL, 'External'),
        (TYPE_VARIABLE, 'Variable'),
    ]
    
    # WooCommerce ID
    wc_id = models.IntegerField(unique=True, db_index=True, verbose_name="WooCommerce ID")
    
    # Basic info (Spanish - original from WooCommerce)
    name = models.CharField(max_length=500, verbose_name="Product Name")
    slug = models.SlugField(max_length=500, db_index=True, verbose_name="Slug")
    permalink = models.URLField(max_length=500, verbose_name="WooCommerce Link")
    
    # Product type
    product_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_SIMPLE,
        db_index=True,
        verbose_name="Product Type"
    )
    
    # Descriptions (Spanish - sin traducir aún)
    short_description = models.TextField(blank=True, default='', verbose_name="Short Description")
    description = models.TextField(blank=True, default='', verbose_name="Full Description")
    
    # Pricing info (stored for reference, but always fetch fresh from WooCommerce)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Current Price")
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Regular Price")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Sale Price")
    on_sale = models.BooleanField(default=False, verbose_name="On Sale")
    
    # Stock info (stored for reference, but always fetch fresh from WooCommerce)
    stock_status = models.CharField(max_length=20, default='instock', verbose_name="Stock Status")
    stock_quantity = models.IntegerField(null=True, blank=True, verbose_name="Stock Quantity")
    manage_stock = models.BooleanField(default=False, verbose_name="Manage Stock")
    
    # Categories (relationship)
    categories = models.ManyToManyField(
        WooCommerceCategory,
        related_name='products',
        blank=True,
        verbose_name="Categories"
    )
    
    # Attributes as JSON (para variaciones y características)
    attributes = models.JSONField(default=list, blank=True, verbose_name="Attributes")
    
    # Default attributes for variable products
    default_attributes = models.JSONField(default=list, blank=True, verbose_name="Default Attributes")
    
    # Dimensions
    weight = models.CharField(max_length=50, blank=True, default='', verbose_name="Weight")
    length = models.CharField(max_length=50, blank=True, default='', verbose_name="Length")
    width = models.CharField(max_length=50, blank=True, default='', verbose_name="Width")
    height = models.CharField(max_length=50, blank=True, default='', verbose_name="Height")
    
    # Rating
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name="Average Rating")
    rating_count = models.IntegerField(default=0, verbose_name="Rating Count")
    
    # Sales
    total_sales = models.IntegerField(default=0, verbose_name="Total Sales")
    
    # Status
    status = models.CharField(max_length=20, default='publish', db_index=True, verbose_name="Status")
    featured = models.BooleanField(default=False, db_index=True, verbose_name="Featured")
    
    # Parent (for variations)
    parent_id = models.IntegerField(default=0, verbose_name="Parent Product ID")
    
    # Timestamps
    date_created_wc = models.DateTimeField(null=True, blank=True, verbose_name="WC Created Date")
    date_modified_wc = models.DateTimeField(null=True, blank=True, verbose_name="WC Modified Date")
    synced_at = models.DateTimeField(auto_now=True, verbose_name="Last Synced At")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    
    class Meta:
        verbose_name = "WooCommerce Product"
        verbose_name_plural = "WooCommerce Products"
        ordering = ['-date_created_wc']
        indexes = [
            models.Index(fields=['wc_id']),
            models.Index(fields=['slug']),
            models.Index(fields=['product_type']),
            models.Index(fields=['status']),
            models.Index(fields=['featured']),
            models.Index(fields=['on_sale']),
        ]
    
    def __str__(self):
        return f"{self.name} (ID: {self.wc_id})"
    
    @property
    def is_variable(self):
        """Check if product is variable (has variations)"""
        return self.product_type == self.TYPE_VARIABLE
    
    @property
    def primary_image(self):
        """Get primary image"""
        return self.images.filter(position=0).first()
    
    @property
    def all_images(self):
        """Get all images ordered by position"""
        return self.images.all().order_by('position')
    
    @property
    def final_price(self):
        """
        Precio final con margen aplicado (SIEMPRE usar este).
        Este es el precio que se debe mostrar al cliente.
        """
        return self.get_price_with_margin()
    
    @property
    def final_regular_price(self):
        """Precio regular final con margen aplicado"""
        return self.get_regular_price_with_margin()
    
    @property
    def final_sale_price(self):
        """Precio de oferta final con margen aplicado"""
        return self.get_sale_price_with_margin()
    
    def get_categories_list(self):
        """Get list of category names"""
        return [cat.name for cat in self.categories.all()]
    
    def get_price_with_margin(self, base_price=None):
        """
        Calcula el precio con margen de categoría aplicado.
        
        Args:
            base_price: Precio base. Si es None, usa self.price
            
        Returns:
            Precio con margen aplicado
        """
        if base_price is None:
            base_price = self.price
        
        if base_price is None:
            return None
        
        # Intentar obtener margen de la primera categoría del producto
        from .translation_models import CategoryPriceMargin, DefaultPriceMargin
        
        category_margin = None
        for category in self.categories.all():
            try:
                category_margin = category.price_margin
                if category_margin and category_margin.is_active:
                    return category_margin.calculate_price(base_price)
            except CategoryPriceMargin.DoesNotExist:
                continue
        
        # Si no hay margen de categoría, usar margen por defecto
        default_margin = DefaultPriceMargin.get_active()
        if default_margin:
            return default_margin.calculate_price(base_price)
        
        # Si no hay ningún margen configurado, retornar precio base
        return float(base_price)
    
    def get_regular_price_with_margin(self):
        """Calcula el precio regular con margen aplicado"""
        return self.get_price_with_margin(self.regular_price)
    
    def get_sale_price_with_margin(self):
        """Calcula el precio de oferta con margen aplicado"""
        if self.sale_price:
            return self.get_price_with_margin(self.sale_price)
        return None


class WooCommerceProductImage(models.Model):
    """
    Imágenes de productos (solo URLs, no descargamos las imágenes).
    """
    product = models.ForeignKey(
        WooCommerceProduct,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Product"
    )
    
    # WooCommerce image ID
    wc_id = models.IntegerField(verbose_name="WooCommerce Image ID")
    
    # Image URLs (diferentes tamaños)
    src = models.URLField(max_length=500, verbose_name="Full Size URL")
    thumbnail = models.URLField(max_length=500, blank=True, default='', verbose_name="Thumbnail URL")
    
    # Image info
    name = models.CharField(max_length=255, blank=True, default='', verbose_name="Image Name")
    alt = models.CharField(max_length=255, blank=True, default='', verbose_name="Alt Text")
    position = models.IntegerField(default=0, verbose_name="Position")
    
    # Timestamps
    synced_at = models.DateTimeField(auto_now=True, verbose_name="Last Synced At")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    
    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ['position', 'wc_id']
        indexes = [
            models.Index(fields=['product', 'position']),
        ]
    
    def __str__(self):
        return f"Image {self.position} for {self.product.name}"


class WooCommerceProductVariation(models.Model):
    """
    Variaciones de productos variables.
    """
    # WooCommerce IDs
    wc_id = models.IntegerField(unique=True, db_index=True, verbose_name="WooCommerce Variation ID")
    wc_product_id = models.IntegerField(db_index=True, verbose_name="WooCommerce Product ID")
    
    # Parent product
    product = models.ForeignKey(
        WooCommerceProduct,
        on_delete=models.CASCADE,
        related_name='variations',
        verbose_name="Parent Product"
    )
    
    # Variation info
    permalink = models.URLField(max_length=500, verbose_name="WooCommerce Link")
    
    # Pricing (stored for reference, but always fetch fresh from WooCommerce)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Current Price")
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Regular Price")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Sale Price")
    on_sale = models.BooleanField(default=False, verbose_name="On Sale")
    
    # Stock (stored for reference, but always fetch fresh from WooCommerce)
    stock_status = models.CharField(max_length=20, default='instock', verbose_name="Stock Status")
    stock_quantity = models.IntegerField(null=True, blank=True, verbose_name="Stock Quantity")
    manage_stock = models.BooleanField(default=False, verbose_name="Manage Stock")
    
    # Attributes (e.g., {"Color": "Red", "Size": "M"})
    attributes = models.JSONField(default=dict, blank=True, verbose_name="Variation Attributes")
    
    # Image
    image_url = models.URLField(max_length=500, blank=True, default='', verbose_name="Image URL")
    
    # Dimensions
    weight = models.CharField(max_length=50, blank=True, default='', verbose_name="Weight")
    length = models.CharField(max_length=50, blank=True, default='', verbose_name="Length")
    width = models.CharField(max_length=50, blank=True, default='', verbose_name="Width")
    height = models.CharField(max_length=50, blank=True, default='', verbose_name="Height")
    
    # Status
    status = models.CharField(max_length=20, default='publish', verbose_name="Status")
    
    # Timestamps
    date_created_wc = models.DateTimeField(null=True, blank=True, verbose_name="WC Created Date")
    date_modified_wc = models.DateTimeField(null=True, blank=True, verbose_name="WC Modified Date")
    synced_at = models.DateTimeField(auto_now=True, verbose_name="Last Synced At")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    
    class Meta:
        verbose_name = "Product Variation"
        verbose_name_plural = "Product Variations"
        ordering = ['wc_id']
        indexes = [
            models.Index(fields=['wc_id']),
            models.Index(fields=['wc_product_id']),
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        attrs = ", ".join([f"{k}: {v}" for k, v in self.attributes.items()])
        return f"{self.product.name} - {attrs} (ID: {self.wc_id})"
    
    def get_attribute_description(self):
        """Get human-readable attribute description"""
        return ", ".join([f"{k}: {v}" for k, v in self.attributes.items()])
    
    @property
    def final_price(self):
        """Precio final con margen aplicado (SIEMPRE usar este)"""
        return self.get_price_with_margin()
    
    @property
    def final_regular_price(self):
        """Precio regular final con margen aplicado"""
        return self.get_regular_price_with_margin()
    
    @property
    def final_sale_price(self):
        """Precio de oferta final con margen aplicado"""
        return self.get_sale_price_with_margin()
    
    def get_price_with_margin(self, base_price=None):
        """
        Calcula el precio con margen de categoría aplicado.
        Usa las categorías del producto padre.
        
        Args:
            base_price: Precio base. Si es None, usa self.price
            
        Returns:
            Precio con margen aplicado
        """
        if base_price is None:
            base_price = self.price
        
        if base_price is None:
            return None
        
        # Usar el método del producto padre
        return self.product.get_price_with_margin(base_price)
    
    def get_regular_price_with_margin(self):
        """Calcula el precio regular con margen aplicado"""
        return self.get_price_with_margin(self.regular_price)
    
    def get_sale_price_with_margin(self):
        """Calcula el precio de oferta con margen aplicado"""
        if self.sale_price:
            return self.get_price_with_margin(self.sale_price)
        return None


class ProductSyncLog(models.Model):
    """
    Log de sincronizaciones para tracking y debugging.
    """
    SYNC_TYPE_FULL = 'full'
    SYNC_TYPE_INCREMENTAL = 'incremental'
    SYNC_TYPE_CATEGORIES = 'categories'
    SYNC_TYPE_PRODUCTS = 'products'
    SYNC_TYPE_VARIATIONS = 'variations'
    
    SYNC_TYPE_CHOICES = [
        (SYNC_TYPE_FULL, 'Full Sync'),
        (SYNC_TYPE_INCREMENTAL, 'Incremental Sync'),
        (SYNC_TYPE_CATEGORIES, 'Categories Only'),
        (SYNC_TYPE_PRODUCTS, 'Products Only'),
        (SYNC_TYPE_VARIATIONS, 'Variations Only'),
    ]
    
    STATUS_STARTED = 'started'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_PARTIAL = 'partial'
    
    STATUS_CHOICES = [
        (STATUS_STARTED, 'Started'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_PARTIAL, 'Partial Success'),
    ]
    
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPE_CHOICES, verbose_name="Sync Type")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_STARTED, verbose_name="Status")
    
    # Stats
    categories_synced = models.IntegerField(default=0, verbose_name="Categories Synced")
    products_synced = models.IntegerField(default=0, verbose_name="Products Synced")
    variations_synced = models.IntegerField(default=0, verbose_name="Variations Synced")
    images_synced = models.IntegerField(default=0, verbose_name="Images Synced")
    
    errors_count = models.IntegerField(default=0, verbose_name="Errors Count")
    error_details = models.TextField(blank=True, default='', verbose_name="Error Details")
    
    # Timing
    started_at = models.DateTimeField(default=timezone.now, verbose_name="Started At")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Completed At")
    duration_seconds = models.IntegerField(null=True, blank=True, verbose_name="Duration (seconds)")
    
    class Meta:
        verbose_name = "Product Sync Log"
        verbose_name_plural = "Product Sync Logs"
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['-started_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.get_sync_type_display()} - {self.get_status_display()} ({self.started_at.strftime('%Y-%m-%d %H:%M')})"
    
    def mark_completed(self, status='success'):
        """Mark sync as completed"""
        self.completed_at = timezone.now()
        self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
        self.status = status
        self.save()
    
    def add_error(self, error_message):
        """Add error to log"""
        self.errors_count += 1
        if self.error_details:
            self.error_details += f"\n{error_message}"
        else:
            self.error_details = error_message
        self.save()
