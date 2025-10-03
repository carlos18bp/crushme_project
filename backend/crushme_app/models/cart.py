"""
Shopping cart models for the e-commerce system
Handles cart functionality with items and quantities
"""
from django.db import models
from django.utils import timezone
from django.conf import settings
from .product import Product


class Cart(models.Model):
    """
    Shopping cart model
    Each user has one active cart at a time
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name="User"
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
        verbose_name = "Shopping Cart"
        verbose_name_plural = "Shopping Carts"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Cart for {self.user.get_full_name()}"
    
    @property
    def total_items(self):
        """Get total number of items in cart"""
        return self.items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    
    @property
    def total_price(self):
        """Calculate total price of all items in cart"""
        total = 0
        for item in self.items.all():
            total += item.subtotal
        return total
    
    @property
    def is_empty(self):
        """Check if cart is empty"""
        return self.items.count() == 0
    
    def add_woocommerce_product(self, wc_product_id, product_name, unit_price, quantity=1, product_image=None):
        """
        Add a WooCommerce product to cart or update quantity if already exists
        Returns the cart item
        
        Args:
            wc_product_id: WooCommerce product ID
            product_name: Name of the product
            unit_price: Price per unit
            quantity: Quantity to add (default 1)
            product_image: URL of the product image (optional)
        """
        cart_item, created = self.items.get_or_create(
            woocommerce_product_id=wc_product_id,
            defaults={
                'product_name': product_name,
                'quantity': quantity,
                'unit_price': unit_price,
                'product_image': product_image
            }
        )
        
        if not created:
            # If item already exists, update quantity
            cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item
    
    def remove_woocommerce_product(self, wc_product_id):
        """Remove a WooCommerce product completely from cart"""
        try:
            cart_item = self.items.get(woocommerce_product_id=wc_product_id)
            cart_item.delete()
            return True
        except CartItem.DoesNotExist:
            return False
    
    def update_woocommerce_product_quantity(self, wc_product_id, quantity):
        """Update quantity of a specific WooCommerce product in cart"""
        try:
            cart_item = self.items.get(woocommerce_product_id=wc_product_id)
            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()
            return True
        except CartItem.DoesNotExist:
            return False
    
    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()
    
    def get_item_count_for_woocommerce_product(self, wc_product_id):
        """Get quantity of specific WooCommerce product in cart"""
        try:
            cart_item = self.items.get(woocommerce_product_id=wc_product_id)
            return cart_item.quantity
        except CartItem.DoesNotExist:
            return 0


class CartItem(models.Model):
    """
    Individual items in a shopping cart
    Links cart with products and quantities
    Works with WooCommerce products
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Cart"
    )
    # WooCommerce product ID instead of ForeignKey
    woocommerce_product_id = models.IntegerField(
        verbose_name="WooCommerce Product ID",
        help_text="ID of the product in WooCommerce",
        default=0
    )
    # Store product details at time of adding to cart
    product_name = models.CharField(
        max_length=500,
        verbose_name="Product Name",
        help_text="Name of the product from WooCommerce",
        default="Unknown Product"
    )
    product_image = models.URLField(
        max_length=1000,
        verbose_name="Product Image",
        help_text="Main image URL from WooCommerce",
        blank=True,
        null=True
    )
    # Legacy field for backward compatibility (optional)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        related_name='cart_items',
        verbose_name="Product (Legacy)",
        null=True,
        blank=True,
        help_text="Legacy field for local products"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantity"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Unit Price",
        help_text="Price per unit at the time of adding to cart"
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
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = ['cart', 'woocommerce_product_id']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cart', 'woocommerce_product_id']),
        ]
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} in {self.cart.user.get_full_name()}'s cart"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this cart item"""
        return self.quantity * self.unit_price
    
    def save(self, *args, **kwargs):
        """Override save method"""
        super().save(*args, **kwargs)
    
    def increase_quantity(self, amount=1):
        """Increase quantity by specified amount"""
        self.quantity += amount
        self.save()
    
    def decrease_quantity(self, amount=1):
        """Decrease quantity by specified amount"""
        if self.quantity > amount:
            self.quantity -= amount
            self.save()
        else:
            # If quantity would be 0 or negative, delete the item
            self.delete()
