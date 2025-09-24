"""
Wishlist models for the e-commerce system
Handles wishlist functionality with sharing capabilities and favorites
"""
from django.db import models
from django.utils import timezone
from django.conf import settings
from .product import Product
import uuid
import json


class WishList(models.Model):
    """
    Wishlist model with sharing capabilities
    Users can create multiple wishlists and share them with others
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlists',
        verbose_name="User"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Wishlist Name",
        help_text="Name of the wishlist"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Optional description of the wishlist"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Whether the wishlist is active"
    )
    unique_link = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        verbose_name="Unique Link",
        help_text="UUID for public sharing of the wishlist"
    )
    
    # Shipping data stored as JSON
    shipping_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Shipping Data",
        help_text="JSON data containing shipping information (name, address, phone, email)"
    )
    
    # Privacy settings
    is_public = models.BooleanField(
        default=False,
        verbose_name="Is Public",
        help_text="Whether the wishlist can be viewed by others via link"
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
        verbose_name = "Wish List"
        verbose_name_plural = "Wish Lists"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['unique_link']),
            models.Index(fields=['is_public']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.get_full_name()}"
    
    @property
    def total_items(self):
        """Get total number of items in wishlist"""
        return self.items.count()
    
    @property
    def total_value(self):
        """Calculate total value of all items in wishlist"""
        total = 0
        for item in self.items.all():
            total += item.product.price
        return total
    
    @property
    def public_url(self):
        """Get the public sharing URL"""
        return f"/wishlists/public/{self.unique_link}/"
    
    @property
    def shipping_name(self):
        """Get shipping name from JSON data"""
        return self.shipping_data.get('name', '')
    
    @property
    def shipping_address(self):
        """Get shipping address from JSON data"""
        return self.shipping_data.get('address', '')
    
    @property
    def shipping_phone(self):
        """Get shipping phone from JSON data"""
        return self.shipping_data.get('phone', '')
    
    @property
    def shipping_email(self):
        """Get shipping email from JSON data"""
        return self.shipping_data.get('email', '')
    
    def set_shipping_data(self, name=None, address=None, phone=None, email=None):
        """Set shipping data"""
        if not self.shipping_data:
            self.shipping_data = {}
        
        if name is not None:
            self.shipping_data['name'] = name
        if address is not None:
            self.shipping_data['address'] = address
        if phone is not None:
            self.shipping_data['phone'] = phone
        if email is not None:
            self.shipping_data['email'] = email
        
        self.save(update_fields=['shipping_data'])
    
    def add_product(self, product):
        """
        Add a product to wishlist if not already present
        Returns tuple (wishlist_item, created)
        """
        wishlist_item, created = self.items.get_or_create(
            product=product,
            defaults={'wishlist': self}
        )
        return wishlist_item, created
    
    def remove_product(self, product):
        """Remove a product from wishlist"""
        try:
            wishlist_item = self.items.get(product=product)
            wishlist_item.delete()
            return True
        except WishListItem.DoesNotExist:
            return False
    
    def has_product(self, product):
        """Check if product is in wishlist"""
        return self.items.filter(product=product).exists()
    
    def clear(self):
        """Remove all items from wishlist"""
        self.items.all().delete()
    
    def make_public(self):
        """Make wishlist public for sharing"""
        self.is_public = True
        self.save(update_fields=['is_public'])
    
    def make_private(self):
        """Make wishlist private"""
        self.is_public = False
        self.save(update_fields=['is_public'])
    
    def get_available_products(self):
        """Get all products in wishlist that are available (in stock and active)"""
        return self.items.filter(
            product__is_active=True,
            product__stock_quantity__gt=0
        )


class WishListItem(models.Model):
    """
    Individual items in a wishlist
    Links wishlist with products
    """
    wishlist = models.ForeignKey(
        WishList,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Wishlist"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='wishlist_items',
        verbose_name="Product"
    )
    
    # Optional notes about the item
    notes = models.TextField(
        blank=True,
        verbose_name="Notes",
        help_text="Optional notes about this item"
    )
    
    # Priority level
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="Priority"
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
        verbose_name = "Wishlist Item"
        verbose_name_plural = "Wishlist Items"
        unique_together = ['wishlist', 'product']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wishlist', 'product']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.product.name} in {self.wishlist.name}"
    
    @property
    def is_available(self):
        """Check if the product is available for purchase"""
        return self.product.is_in_stock


class FavoriteWishList(models.Model):
    """
    Model to track user's favorite wishlists (from other users)
    Allows users to follow/favorite other people's wishlists
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_wishlists',
        verbose_name="User"
    )
    wishlist = models.ForeignKey(
        WishList,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name="Wishlist"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Created At"
    )
    
    class Meta:
        verbose_name = "Favorite Wishlist"
        verbose_name_plural = "Favorite Wishlists"
        unique_together = ['user', 'wishlist']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} favorites {self.wishlist.name}"
    
    def save(self, *args, **kwargs):
        """Prevent users from favoriting their own wishlists"""
        if self.user == self.wishlist.user:
            raise ValueError("Users cannot favorite their own wishlists")
        super().save(*args, **kwargs)
    
    @classmethod
    def add_favorite(cls, user, wishlist):
        """
        Add a wishlist to user's favorites
        Returns tuple (favorite, created)
        """
        if user == wishlist.user:
            raise ValueError("Users cannot favorite their own wishlists")
        
        favorite, created = cls.objects.get_or_create(
            user=user,
            wishlist=wishlist
        )
        return favorite, created
    
    @classmethod
    def remove_favorite(cls, user, wishlist):
        """Remove a wishlist from user's favorites"""
        try:
            favorite = cls.objects.get(user=user, wishlist=wishlist)
            favorite.delete()
            return True
        except cls.DoesNotExist:
            return False
    
    @classmethod
    def is_favorited(cls, user, wishlist):
        """Check if user has favorited a wishlist"""
        return cls.objects.filter(user=user, wishlist=wishlist).exists()
    
    @classmethod
    def get_user_favorites(cls, user):
        """Get all wishlists favorited by a user"""
        return cls.objects.filter(user=user).select_related('wishlist')
    
    @classmethod
    def get_wishlist_favorites_count(cls, wishlist):
        """Get number of times a wishlist has been favorited"""
        return cls.objects.filter(wishlist=wishlist).count()
