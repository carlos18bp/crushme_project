"""
Product model for the e-commerce system
Includes gallery functionality using Django Attachments
"""
from django.db import models
from django.utils import timezone
from django_attachments.fields import GalleryField
from django_attachments.models import Library


class Product(models.Model):
    """
    Product model with gallery support using Django Attachments
    Based on the candle_project implementation for image handling
    """
    
    # Product category choices
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('books', 'Books'),
        ('home_garden', 'Home & Garden'),
        ('sports', 'Sports & Outdoors'),
        ('toys', 'Toys & Games'),
        ('beauty', 'Beauty & Personal Care'),
        ('automotive', 'Automotive'),
        ('food', 'Food & Beverages'),
        ('health', 'Health & Wellness'),
        ('jewelry', 'Jewelry & Accessories'),
        ('music', 'Music & Instruments'),
        ('art', 'Art & Crafts'),
        ('office', 'Office Supplies'),
        ('pet', 'Pet Supplies'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name="Product Name",
        help_text="The name of the product"
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Detailed description of the product"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Price",
        help_text="Product price in USD"
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name="Category",
        help_text="Product category"
    )
    
    # Gallery using Django Attachments (based on candle_project implementation)
    gallery = GalleryField(
        related_name='products_with_attachment',
        on_delete=models.CASCADE,
        verbose_name="Product Gallery",
        help_text="Image gallery for the product"
    )
    
    # Stock management
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Stock Quantity",
        help_text="Available quantity in stock"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Whether the product is available for purchase"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """
        Override save method based on candle_project pattern
        """
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Custom delete method to ensure the gallery is also deleted when a Product is deleted.
        Based on candle_project implementation
        """
        try:
            if self.gallery:
                self.gallery.delete()
        except Library.DoesNotExist:
            pass
        super(Product, self).delete(*args, **kwargs)
    
    @property
    def is_in_stock(self):
        """Check if product has stock available"""
        return self.stock_quantity > 0 and self.is_active
    
    @property
    def primary_image(self):
        """Get the primary image from the gallery"""
        if self.gallery and self.gallery.primary_attachment:
            return self.gallery.primary_attachment
        return None
        
    @property
    def gallery_images(self):
        """Get all images from the gallery"""
        if self.gallery:
            return self.gallery.attachment_set.filter(image_width__isnull=False)
        return []
    
    def reduce_stock(self, quantity):
        """Reduce stock quantity by given amount"""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save(update_fields=['stock_quantity'])
            return True
        return False
    
    def increase_stock(self, quantity):
        """Increase stock quantity by given amount"""
        self.stock_quantity += quantity
        self.save(update_fields=['stock_quantity'])
    
    def get_category_display_name(self):
        """Get human-readable category name"""
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)
    
    @classmethod
    def get_products_by_category(cls, category):
        """Get all active products by category"""
        return cls.objects.filter(category=category, is_active=True)
    
    @classmethod
    def search_products(cls, query):
        """Search products by name or description"""
        return cls.objects.filter(
            models.Q(name__icontains=query) | 
            models.Q(description__icontains=query),
            is_active=True
        )
