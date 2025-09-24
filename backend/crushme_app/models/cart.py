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
    
    def add_product(self, product, quantity=1):
        """
        Add a product to cart or update quantity if already exists
        Returns the cart item
        """
        cart_item, created = self.items.get_or_create(
            product=product,
            defaults={
                'quantity': quantity,
                'unit_price': product.price
            }
        )
        
        if not created:
            # If item already exists, update quantity
            cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item
    
    def remove_product(self, product):
        """Remove a product completely from cart"""
        try:
            cart_item = self.items.get(product=product)
            cart_item.delete()
            return True
        except CartItem.DoesNotExist:
            return False
    
    def update_product_quantity(self, product, quantity):
        """Update quantity of a specific product in cart"""
        try:
            cart_item = self.items.get(product=product)
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
    
    def get_item_count_for_product(self, product):
        """Get quantity of specific product in cart"""
        try:
            cart_item = self.items.get(product=product)
            return cart_item.quantity
        except CartItem.DoesNotExist:
            return 0


class CartItem(models.Model):
    """
    Individual items in a shopping cart
    Links cart with products and quantities
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Cart"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name="Product"
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
        unique_together = ['cart', 'product']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.cart.user.get_full_name()}'s cart"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this cart item"""
        return self.quantity * self.unit_price
    
    def save(self, *args, **kwargs):
        """Override save to set unit_price from product if not provided"""
        if not self.unit_price:
            self.unit_price = self.product.price
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
    
    def update_price(self):
        """Update unit price to current product price"""
        self.unit_price = self.product.price
        self.save()
