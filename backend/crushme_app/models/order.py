"""
Order models for the e-commerce system
Handles order processing and purchase history
"""
from django.db import models
from django.utils import timezone
from django.conf import settings
from .product import Product
import uuid


class Order(models.Model):
    """
    Order model for purchase history
    Contains order information and shipping details
    """
    
    # Order status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="User"
    )
    order_number = models.CharField(
        max_length=32,
        unique=True,
        verbose_name="Order Number",
        help_text="Unique order identifier"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Amount",
        help_text="Total order amount"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Order Status"
    )
    
    # Shipping information
    shipping_address = models.TextField(
        verbose_name="Shipping Address",
        help_text="Complete shipping address"
    )
    shipping_city = models.CharField(
        max_length=100,
        verbose_name="Shipping City",
        blank=True
    )
    shipping_state = models.CharField(
        max_length=100,
        verbose_name="Shipping State/Province",
        blank=True
    )
    shipping_postal_code = models.CharField(
        max_length=20,
        verbose_name="Postal Code",
        blank=True
    )
    shipping_country = models.CharField(
        max_length=100,
        verbose_name="Country",
        default="United States"
    )
    
    # Contact information
    phone_number = models.CharField(
        max_length=20,
        verbose_name="Phone Number",
        blank=True
    )
    
    # Order notes
    notes = models.TextField(
        verbose_name="Order Notes",
        blank=True,
        help_text="Additional notes or instructions"
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
    shipped_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Shipped At"
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Delivered At"
    )
    
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['order_number']),
        ]
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        """Generate order number if not provided"""
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_order_number():
        """Generate a unique order number"""
        import random
        import string
        
        # Generate a random string of 8 characters
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Add timestamp for uniqueness
        timestamp_part = str(int(timezone.now().timestamp()))[-6:]
        
        return f"ORD{timestamp_part}{random_part}"
    
    @property
    def total_items(self):
        """Get total number of items in order"""
        return self.items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    
    @property
    def full_shipping_address(self):
        """Get formatted full shipping address"""
        address_parts = [self.shipping_address]
        
        if self.shipping_city:
            address_parts.append(self.shipping_city)
        if self.shipping_state:
            address_parts.append(self.shipping_state)
        if self.shipping_postal_code:
            address_parts.append(self.shipping_postal_code)
        if self.shipping_country:
            address_parts.append(self.shipping_country)
            
        return ', '.join(filter(None, address_parts))
    
    def can_be_cancelled(self):
        """Check if order can be cancelled"""
        return self.status in ['pending', 'processing']
    
    def can_be_shipped(self):
        """Check if order can be shipped"""
        return self.status == 'processing'
    
    def mark_as_shipped(self):
        """Mark order as shipped"""
        if self.can_be_shipped():
            self.status = 'shipped'
            self.shipped_at = timezone.now()
            self.save()
            return True
        return False
    
    def mark_as_delivered(self):
        """Mark order as delivered"""
        if self.status == 'shipped':
            self.status = 'delivered'
            self.delivered_at = timezone.now()
            self.save()
            return True
        return False
    
    def cancel_order(self):
        """Cancel the order"""
        if self.can_be_cancelled():
            self.status = 'cancelled'
            self.save()
            
            # Return items to stock
            for item in self.items.all():
                item.product.increase_stock(item.quantity)
            
            return True
        return False


class OrderItem(models.Model):
    """
    Individual items within an order
    Stores product information at the time of purchase
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Order"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name="Product"
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Quantity"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Unit Price",
        help_text="Price per unit at the time of purchase"
    )
    
    # Store product details at time of purchase (for historical purposes)
    product_name = models.CharField(
        max_length=200,
        verbose_name="Product Name (at purchase)",
        help_text="Product name at the time of purchase"
    )
    product_description = models.TextField(
        verbose_name="Product Description (at purchase)",
        help_text="Product description at the time of purchase"
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
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        unique_together = ['order', 'product']
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} (Order #{self.order.order_number})"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this order item"""
        return self.quantity * self.unit_price
    
    def save(self, *args, **kwargs):
        """Store product information at time of purchase"""
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_description:
            self.product_description = self.product.description
        if not self.unit_price:
            self.unit_price = self.product.price
            
        super().save(*args, **kwargs)
