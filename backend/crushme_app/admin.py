"""
Django Admin configuration for CrushMe e-commerce application
Provides comprehensive admin interface for all models with optimized views and inline editing
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_attachments.admin import AttachmentsAdminMixin
from .forms.product import ProductForm

# Import all models
from .models import (
    User, PasswordCode, Product, Cart, CartItem, 
    Order, OrderItem, WishList, WishListItem, FavoriteWishList
)

# AttachmentsAdminMixin handles the gallery management automatically


# ===========================
# USER MODELS ADMIN
# ===========================

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin for User model extending Django's UserAdmin
    Optimized for email-based authentication
    """
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    # Define fieldsets for user detail view
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Define fieldsets for user creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    # Remove username field since we use email
    username = None
    
    # Override filter_horizontal to remove groups and user_permissions
    filter_horizontal = ()
    
    def get_queryset(self, request):
        """Optimize queryset to reduce database hits"""
        return super().get_queryset(request).select_related()


@admin.register(PasswordCode)
class PasswordCodeAdmin(admin.ModelAdmin):
    """Admin for password reset codes"""
    list_display = ('user_email', 'code', 'used', 'is_expired_display', 'created_at')
    list_filter = ('used', 'created_at')
    search_fields = ('user__email', 'code')
    readonly_fields = ('code', 'created_at')
    ordering = ('-created_at',)
    
    def user_email(self, obj):
        """Display user email instead of object representation"""
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def is_expired_display(self, obj):
        """Display expiration status with color coding"""
        if obj.is_expired():
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Valid</span>')
    is_expired_display.short_description = 'Status'


# ===========================
# PRODUCT MODELS ADMIN
# ===========================

@admin.register(Product)
class ProductAdmin(AttachmentsAdminMixin, admin.ModelAdmin):
    """
    Comprehensive admin for Product model
    Includes gallery management and stock tracking
    Based on candle_project implementation
    """
    form = ProductForm
    list_display = (
        'name', 'category', 'price', 'stock_quantity', 
        'is_active', 'is_in_stock_display', 'created_at'
    )
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'primary_image_display')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock_quantity', 'is_active')
        }),
        ('Gallery', {
            'fields': ('gallery', 'primary_image_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Gallery management is handled by AttachmentsAdminMixin
    
    def delete_queryset(self, request, queryset):
        """Custom delete to handle gallery cleanup"""
        for obj in queryset:
            obj.delete()
    
    def is_in_stock_display(self, obj):
        """Display stock status with color coding"""
        if obj.is_in_stock:
            return format_html('<span style="color: green;">✓ In Stock</span>')
        return format_html('<span style="color: red;">✗ Out of Stock</span>')
    is_in_stock_display.short_description = 'Stock Status'
    
    def primary_image_display(self, obj):
        """Display primary image if available"""
        primary_image = obj.primary_image
        if primary_image and primary_image.file:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                primary_image.file.url
            )
        return "No image"
    primary_image_display.short_description = 'Primary Image'


# ===========================
# CART MODELS ADMIN
# ===========================

class CartItemInline(admin.TabularInline):
    """Inline admin for cart items"""
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal_display', 'created_at')
    fields = ('product', 'quantity', 'unit_price', 'subtotal_display', 'created_at')
    
    def subtotal_display(self, obj):
        """Display calculated subtotal"""
        if obj.pk:
            return f"${obj.subtotal:.2f}"
        return "-"
    subtotal_display.short_description = 'Subtotal'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin for shopping carts with inline items"""
    list_display = ('user_email', 'total_items_display', 'total_price_display', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'total_items_display', 'total_price_display')
    ordering = ('-updated_at',)
    
    inlines = [CartItemInline]
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def total_items_display(self, obj):
        """Display total items count"""
        return obj.total_items
    total_items_display.short_description = 'Items'
    
    def total_price_display(self, obj):
        """Display total price formatted"""
        return f"${obj.total_price:.2f}"
    total_price_display.short_description = 'Total'


# ===========================
# ORDER MODELS ADMIN
# ===========================

class OrderItemInline(admin.TabularInline):
    """Inline admin for order items"""
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal_display', 'created_at')
    fields = ('product', 'product_name', 'quantity', 'unit_price', 'subtotal_display')
    
    def subtotal_display(self, obj):
        """Display calculated subtotal"""
        if obj.pk:
            return f"${obj.subtotal:.2f}"
        return "-"
    subtotal_display.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Comprehensive admin for Order model
    Includes status management and shipping tracking
    """
    list_display = (
        'order_number', 'user_email', 'status_display', 
        'total_display', 'total_items_display', 'created_at'
    )
    list_filter = ('status', 'created_at', 'shipped_at', 'delivered_at')
    search_fields = ('order_number', 'user__email', 'shipping_address')
    readonly_fields = (
        'order_number', 'created_at', 'updated_at', 
        'total_items_display', 'full_shipping_address'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'total', 'total_items_display')
        }),
        ('Shipping Information', {
            'fields': (
                'shipping_address', 'shipping_city', 'shipping_state',
                'shipping_postal_code', 'shipping_country', 'phone_number',
                'full_shipping_address'
            )
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrderItemInline]
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def status_display(self, obj):
        """Display status with color coding"""
        status_colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8', 
            'shipped': '#007bff',
            'delivered': '#28a745',
            'cancelled': '#dc3545',
            'refunded': '#6c757d',
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def total_display(self, obj):
        """Display total formatted"""
        return f"${obj.total:.2f}"
    total_display.short_description = 'Total'
    total_display.admin_order_field = 'total'
    
    def total_items_display(self, obj):
        """Display total items count"""
        return obj.total_items
    total_items_display.short_description = 'Items'


# ===========================
# WISHLIST MODELS ADMIN
# ===========================

class WishListItemInline(admin.TabularInline):
    """Inline admin for wishlist items"""
    model = WishListItem
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('product', 'priority', 'notes', 'created_at')


@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    """Admin for WishList model with sharing capabilities"""
    list_display = (
        'name', 'user_email', 'is_active', 'is_public', 
        'total_items_display_wishlist', 'total_value_display', 'created_at'
    )
    list_filter = ('is_active', 'is_public', 'created_at')
    search_fields = ('name', 'description', 'user__email')
    readonly_fields = (
        'unique_link', 'created_at', 'updated_at', 
        'total_items_display_wishlist', 'total_value_display', 'public_url'
    )
    ordering = ('-created_at',)
    
    inlines = [WishListItemInline]
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def total_items_display_wishlist(self, obj):
        """Display total items count"""
        return obj.total_items
    total_items_display_wishlist.short_description = 'Items'
    
    def total_value_display(self, obj):
        """Display total value formatted"""
        return f"${obj.total_value:.2f}"
    total_value_display.short_description = 'Total Value'


@admin.register(WishListItem)
class WishListItemAdmin(admin.ModelAdmin):
    """Admin for individual wishlist items"""
    list_display = ('product_name', 'wishlist_name', 'priority', 'is_available_display', 'created_at')
    list_filter = ('priority', 'created_at', 'product__is_active')
    search_fields = ('product__name', 'wishlist__name', 'notes')
    ordering = ('-created_at',)
    
    def product_name(self, obj):
        """Display product name"""
        return obj.product.name
    product_name.short_description = 'Product'
    product_name.admin_order_field = 'product__name'
    
    def wishlist_name(self, obj):
        """Display wishlist name"""
        return obj.wishlist.name
    wishlist_name.short_description = 'Wishlist'
    wishlist_name.admin_order_field = 'wishlist__name'
    
    def is_available_display(self, obj):
        """Display availability status"""
        if obj.is_available:
            return format_html('<span style="color: green;">✓ Available</span>')
        return format_html('<span style="color: red;">✗ Unavailable</span>')
    is_available_display.short_description = 'Availability'


@admin.register(FavoriteWishList)
class FavoriteWishListAdmin(admin.ModelAdmin):
    """Admin for favorite wishlists"""
    list_display = ('user_email', 'wishlist_name', 'wishlist_owner', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'wishlist__name', 'wishlist__user__email')
    ordering = ('-created_at',)
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def wishlist_name(self, obj):
        """Display wishlist name"""
        return obj.wishlist.name
    wishlist_name.short_description = 'Wishlist'
    wishlist_name.admin_order_field = 'wishlist__name'
    
    def wishlist_owner(self, obj):
        """Display wishlist owner"""
        return obj.wishlist.user.email
    wishlist_owner.short_description = 'Wishlist Owner'
    wishlist_owner.admin_order_field = 'wishlist__user__email'


# ===========================
# ADMIN SITE CUSTOMIZATION
# ===========================

# Customize admin site header and title
# Custom AdminSite to organize models by functional sections
from django.utils.translation import gettext_lazy as _

class CrushMeAdminSite(admin.AdminSite):
    """
    Custom AdminSite to organize models by functional sections.
    Provides a structured and intuitive admin interface for the e-commerce platform.
    """
    site_header = 'CrushMe Administration'
    site_title = 'CrushMe Admin'
    index_title = 'Welcome to CrushMe E-commerce Control Panel'

    def get_app_list(self, request):
        app_dict = self._build_app_dict(request)
        # Custom structure for the admin index
        custom_app_list = [
            {
                'name': _('User Management'),
                'app_label': 'user_management',
                'models': [
                    model for model in app_dict.get('crushme_app', {}).get('models', [])
                    if model['object_name'] in ['User', 'PasswordCode']
                ]
            },
            {
                'name': _('Product Management'),
                'app_label': 'product_management',
                'models': [
                    model for model in app_dict.get('crushme_app', {}).get('models', [])
                    if model['object_name'] in ['Product']
                ]
            },
            {
                'name': _('Shopping Management'),
                'app_label': 'shopping_management',
                'models': [
                    model for model in app_dict.get('crushme_app', {}).get('models', [])
                    if model['object_name'] in ['Cart', 'CartItem']
                ]
            },
            {
                'name': _('Order Management'),
                'app_label': 'order_management',
                'models': [
                    model for model in app_dict.get('crushme_app', {}).get('models', [])
                    if model['object_name'] in ['Order', 'OrderItem']
                ]
            },
            {
                'name': _('Wishlist Management'),
                'app_label': 'wishlist_management',
                'models': [
                    model for model in app_dict.get('crushme_app', {}).get('models', [])
                    if model['object_name'] in ['WishList', 'WishListItem', 'FavoriteWishList']
                ]
            },
            {
                'name': _('Media & Attachments'),
                'app_label': 'media_management',
                'models': [
                    model for model in app_dict.get('django_attachments', {}).get('models', [])
                    if model['object_name'] in ['Library', 'Attachment']
                ]
            }
        ]
        return custom_app_list

# Create an instance of the custom AdminSite
admin_site = CrushMeAdminSite(name='crushme_admin')

# Register all models with the custom AdminSite
admin_site.register(User, CustomUserAdmin)
admin_site.register(PasswordCode, PasswordCodeAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(Cart, CartAdmin)
# CartItem is managed through CartAdmin inline
admin_site.register(Order, OrderAdmin)
# OrderItem is managed through OrderAdmin inline
admin_site.register(WishList, WishListAdmin)
# WishListItem is managed through WishListAdmin inline
admin_site.register(FavoriteWishList, FavoriteWishListAdmin)