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
    User, PasswordCode, UserAddress, UserGallery, UserLink, GuestUser,
    Product, Cart, CartItem, 
    Order, OrderItem, WishList, WishListItem, FavoriteWishList,
    Review, Feed, FavoriteProduct,
    WooCommerceCategory, WooCommerceProduct, WooCommerceProductImage,
    WooCommerceProductVariation, ProductSyncLog,
    TranslatedContent, CategoryPriceMargin, DefaultPriceMargin
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
    Includes Crush verification management
    """
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_crush_display', 'crush_status_display', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_crush', 'crush_verification_status', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    actions = ['approve_crush_verification', 'reject_crush_verification']
    
    # Define fieldsets for user detail view
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name', 'phone', 'about')}),
        ('Profile Images', {'fields': ('profile_picture', 'cover_image')}),
        ('Public Status', {'fields': ('current_status', 'note')}),
        ('Verification', {'fields': ('email_verified', 'is_guest_converted')}),
        ('Crush Verification', {
            'fields': ('is_crush', 'crush_verification_status', 'crush_requested_at', 'crush_verified_at', 'crush_rejection_reason'),
            'classes': ('collapse',)
        }),
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
    
    def is_crush_display(self, obj):
        """Display Crush verification status with badge"""
        if obj.is_crush:
            return format_html('<span style="background-color: #ff69b4; color: white; padding: 3px 10px; border-radius: 10px; font-weight: bold;">✓ CRUSH</span>')
        return format_html('<span style="color: #999;">-</span>')
    is_crush_display.short_description = 'Crush Status'
    is_crush_display.admin_order_field = 'is_crush'
    
    def crush_status_display(self, obj):
        """Display Crush verification request status with color coding"""
        status_colors = {
            'none': '#999',
            'pending': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545',
        }
        status_labels = {
            'none': '—',
            'pending': '⏳ Pending',
            'approved': '✓ Approved',
            'rejected': '✗ Rejected',
        }
        color = status_colors.get(obj.crush_verification_status, '#999')
        label = status_labels.get(obj.crush_verification_status, obj.crush_verification_status)
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, label
        )
    crush_status_display.short_description = 'Request Status'
    crush_status_display.admin_order_field = 'crush_verification_status'
    
    def approve_crush_verification(self, request, queryset):
        """Admin action to approve Crush verification requests"""
        from django.utils import timezone
        
        # Filter only pending requests
        pending_users = queryset.filter(crush_verification_status='pending')
        count = pending_users.count()
        
        # Update users
        pending_users.update(
            is_crush=True,
            crush_verification_status='approved',
            crush_verified_at=timezone.now(),
            crush_rejection_reason=None
        )
        
        self.message_user(
            request,
            f'{count} Crush verification request(s) approved successfully.',
            level='success'
        )
    approve_crush_verification.short_description = '✓ Approve selected Crush verification requests'
    
    def reject_crush_verification(self, request, queryset):
        """Admin action to reject Crush verification requests"""
        # Filter only pending requests
        pending_users = queryset.filter(crush_verification_status='pending')
        count = pending_users.count()
        
        # Update users
        pending_users.update(
            is_crush=False,
            crush_verification_status='rejected',
            crush_verified_at=None,
            crush_rejection_reason='Rejected by administrator'
        )
        
        self.message_user(
            request,
            f'{count} Crush verification request(s) rejected.',
            level='warning'
        )
    reject_crush_verification.short_description = '✗ Reject selected Crush verification requests'


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


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    """Admin for user addresses"""
    list_display = (
        'get_owner', 'address_line_1', 'city', 'state', 'country',
        'is_default_shipping', 'is_default_billing'
    )
    list_filter = ('country', 'state', 'is_default_shipping', 'is_default_billing')
    search_fields = ('user__email', 'guest_email', 'address_line_1', 'city')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Owner Information', {
            'fields': ('user', 'guest_email', 'guest_first_name', 'guest_last_name', 'guest_phone')
        }),
        ('Address Information', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'zip_code', 'country')
        }),
        ('Preferences', {
            'fields': ('is_default_shipping', 'is_default_billing')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_owner(self, obj):
        """Get the owner of the address (user or guest)"""
        if obj.user:
            return f"User: {obj.user.email}"
        elif obj.guest_email:
            return f"Guest: {obj.guest_email}"
        return "Unknown"
    get_owner.short_description = 'Owner'
    get_owner.admin_order_field = 'user__email'


@admin.register(UserGallery)
class UserGalleryAdmin(admin.ModelAdmin):
    """Admin for user gallery photos"""
    list_display = ('user_email', 'caption', 'is_profile_picture', 'image_preview', 'uploaded_at')
    list_filter = ('is_profile_picture', 'uploaded_at')
    search_fields = ('user__email', 'user__username', 'caption')
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_at', 'image_preview')
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def image_preview(self, obj):
        """Display image preview"""
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(UserLink)
class UserLinkAdmin(admin.ModelAdmin):
    """Admin for user links (linktree-style)"""
    list_display = ('user_email', 'title', 'url', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'user__username', 'title', 'url')
    ordering = ('user', 'order', '-created_at')
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'


@admin.register(GuestUser)
class GuestUserAdmin(admin.ModelAdmin):
    """Admin for guest users"""
    list_display = (
        'email', 'full_name', 'phone', 'total_orders', 
        'total_spent', 'has_been_converted', 'created_at'
    )
    list_filter = ('has_been_converted', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'full_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('email', 'first_name', 'last_name', 'full_name', 'phone')
        }),
        ('Purchase History', {
            'fields': ('total_orders', 'total_spent')
        }),
        ('Conversion', {
            'fields': ('has_been_converted', 'converted_user')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        """Display full name"""
        return obj.get_full_name()
    full_name.short_description = 'Full Name'


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


@admin.register(FavoriteProduct)
class FavoriteProductAdmin(admin.ModelAdmin):
    """Admin for favorite products"""
    list_display = ('user_email', 'woocommerce_product_id', 'product_name_display', 'cache_status', 'created_at')
    list_filter = ('created_at', 'cache_updated_at')
    search_fields = ('user__email', 'woocommerce_product_id', 'product_data__name')
    ordering = ('-created_at',)
    readonly_fields = ('cache_updated_at', 'created_at', 'updated_at')
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def product_name_display(self, obj):
        """Display product name from cached data"""
        product_name = obj.product_data.get('name', 'N/A')
        return product_name[:50] + '...' if len(product_name) > 50 else product_name
    product_name_display.short_description = 'Product Name'
    
    def cache_status(self, obj):
        """Display cache status with color coding"""
        if not obj.cache_updated_at:
            return format_html('<span style="color: red;">No Cache</span>')
        
        if obj.needs_cache_refresh():
            return format_html('<span style="color: orange;">Stale</span>')
        
        return format_html('<span style="color: green;">Fresh</span>')
    cache_status.short_description = 'Cache Status'


# ===========================
# REVIEW MODELS ADMIN
# ===========================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin for Review model
    Reviews for WooCommerce products
    """
    list_display = (
        'woocommerce_product_id', 'reviewer_display', 'rating_display', 
        'is_active', 'is_verified_purchase', 'created_at'
    )
    list_filter = ('rating', 'is_active', 'is_verified_purchase', 'created_at')
    search_fields = (
        'woocommerce_product_id', 'comment', 'title',
        'user__email', 'anonymous_name', 'anonymous_email'
    )
    readonly_fields = ('created_at', 'updated_at', 'reviewer_name', 'reviewer_email')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Product Information', {
            'fields': ('woocommerce_product_id',)
        }),
        ('Reviewer Information', {
            'fields': ('user', 'reviewer_name', 'reviewer_email', 'anonymous_name', 'anonymous_email')
        }),
        ('Review Content', {
            'fields': ('rating', 'title', 'comment')
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified_purchase')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def reviewer_display(self, obj):
        """Display reviewer name"""
        if obj.user:
            return format_html('<strong>{}</strong> (Registered)', obj.reviewer_name)
        return format_html('{} (Guest)', obj.reviewer_name)
    reviewer_display.short_description = 'Reviewer'
    
    def rating_display(self, obj):
        """Display rating with stars"""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        color = '#ffc107' if obj.rating >= 4 else '#ff9800' if obj.rating >= 3 else '#ff5722'
        return format_html(
            '<span style="color: {}; font-size: 16px;">{}</span> ({})',
            color, stars, obj.rating
        )
    rating_display.short_description = 'Rating'


# ===========================
# FEED MODELS ADMIN
# ===========================

@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    """
    Admin for Feed model (user posts)
    """
    list_display = ('user_email', 'text_preview', 'color_display', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'user__username', 'text')
    readonly_fields = ('created_at', 'updated_at', 'color_preview')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Contenido', {
            'fields': ('text', 'color', 'color_preview')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'Usuario'
    user_email.admin_order_field = 'user__email'
    
    def text_preview(self, obj):
        """Display truncated text"""
        preview = obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
        return preview
    text_preview.short_description = 'Texto'
    
    def color_display(self, obj):
        """Display color with visual preview"""
        return format_html(
            '<span style="background-color: {}; padding: 5px 15px; color: white; border-radius: 3px;">{}</span>',
            obj.color, obj.color
        )
    color_display.short_description = 'Color'
    
    def color_preview(self, obj):
        """Display larger color preview"""
        return format_html(
            '<div style="background-color: {}; width: 100px; height: 50px; border: 1px solid #ccc; border-radius: 5px;"></div>',
            obj.color
        )
    color_preview.short_description = 'Vista Previa del Color'


# ===========================
# WOOCOMMERCE MODELS ADMIN
# ===========================

@admin.register(WooCommerceCategory)
class WooCommerceCategoryAdmin(admin.ModelAdmin):
    """Admin for WooCommerce categories"""
    list_display = ('wc_id', 'name', 'slug', 'product_count', 'parent_name', 'synced_at')
    list_filter = ('synced_at', 'wc_parent_id')
    search_fields = ('name', 'slug', 'wc_id')
    readonly_fields = ('wc_id', 'synced_at', 'created_at')
    ordering = ('display_order', 'name')
    
    fieldsets = (
        ('WooCommerce Info', {
            'fields': ('wc_id', 'name', 'slug', 'description')
        }),
        ('Hierarchy', {
            'fields': ('wc_parent_id', 'parent')
        }),
        ('Stats', {
            'fields': ('product_count', 'display_order')
        }),
        ('Image', {
            'fields': ('image_url',)
        }),
        ('Timestamps', {
            'fields': ('synced_at', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def parent_name(self, obj):
        """Display parent category name"""
        if obj.parent:
            return obj.parent.name
        return "—"
    parent_name.short_description = 'Parent'
    parent_name.admin_order_field = 'parent__name'


class WooCommerceProductImageInline(admin.TabularInline):
    """Inline admin for product images"""
    model = WooCommerceProductImage
    extra = 0
    readonly_fields = ('wc_id', 'image_preview', 'synced_at')
    fields = ('position', 'image_preview', 'src', 'name', 'alt')
    
    def image_preview(self, obj):
        """Display image preview"""
        if obj.src:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover;" />',
                obj.src
            )
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(WooCommerceProduct)
class WooCommerceProductAdmin(admin.ModelAdmin):
    """Admin for WooCommerce products"""
    list_display = (
        'wc_id', 'name_truncated', 'product_type', 'price', 
        'stock_status_display', 'stock_quantity', 'status', 'synced_at'
    )
    list_filter = ('product_type', 'status', 'stock_status', 'on_sale', 'featured', 'synced_at')
    search_fields = ('name', 'wc_id', 'slug')
    readonly_fields = (
        'wc_id', 'slug', 'permalink', 'date_created_wc', 
        'date_modified_wc', 'synced_at', 'created_at', 'primary_image_preview'
    )
    ordering = ('-date_created_wc',)
    filter_horizontal = ('categories',)
    
    fieldsets = (
        ('WooCommerce Info', {
            'fields': ('wc_id', 'name', 'slug', 'permalink', 'product_type', 'status')
        }),
        ('Descriptions', {
            'fields': ('short_description', 'description'),
            'classes': ('collapse',)
        }),
        ('Pricing', {
            'fields': ('price', 'regular_price', 'sale_price', 'on_sale')
        }),
        ('Stock', {
            'fields': ('stock_status', 'stock_quantity', 'manage_stock')
        }),
        ('Categories', {
            'fields': ('categories',)
        }),
        ('Attributes & Variations', {
            'fields': ('attributes', 'default_attributes'),
            'classes': ('collapse',)
        }),
        ('Dimensions', {
            'fields': ('weight', 'length', 'width', 'height'),
            'classes': ('collapse',)
        }),
        ('Rating & Sales', {
            'fields': ('average_rating', 'rating_count', 'total_sales', 'featured')
        }),
        ('Images', {
            'fields': ('primary_image_preview',)
        }),
        ('Timestamps', {
            'fields': ('date_created_wc', 'date_modified_wc', 'synced_at', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [WooCommerceProductImageInline]
    
    def name_truncated(self, obj):
        """Display truncated product name"""
        return obj.name[:50] + '...' if len(obj.name) > 50 else obj.name
    name_truncated.short_description = 'Product Name'
    name_truncated.admin_order_field = 'name'
    
    def stock_status_display(self, obj):
        """Display stock status with color"""
        colors = {
            'instock': 'green',
            'outofstock': 'red',
            'onbackorder': 'orange',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.stock_status, 'gray'), obj.stock_status.upper()
        )
    stock_status_display.short_description = 'Stock Status'
    stock_status_display.admin_order_field = 'stock_status'
    
    def primary_image_preview(self, obj):
        """Display primary image"""
        primary = obj.primary_image
        if primary and primary.src:
            return format_html(
                '<img src="{}" width="150" height="150" style="object-fit: cover;" />',
                primary.src
            )
        return "No image"
    primary_image_preview.short_description = 'Primary Image'


@admin.register(WooCommerceProductVariation)
class WooCommerceProductVariationAdmin(admin.ModelAdmin):
    """Admin for product variations"""
    list_display = (
        'wc_id', 'product_name', 'attribute_description', 
        'price', 'stock_status_display', 'stock_quantity', 'synced_at'
    )
    list_filter = ('status', 'stock_status', 'synced_at')
    search_fields = ('wc_id', 'product__name', 'attributes')
    readonly_fields = (
        'wc_id', 'wc_product_id', 'permalink', 'attributes',
        'date_created_wc', 'date_modified_wc', 'synced_at', 'created_at',
        'image_preview'
    )
    ordering = ('-synced_at',)
    
    fieldsets = (
        ('WooCommerce Info', {
            'fields': ('wc_id', 'wc_product_id', 'product', 'permalink', 'status')
        }),
        ('Variation Attributes', {
            'fields': ('attributes',)
        }),
        ('Pricing', {
            'fields': ('price', 'regular_price', 'sale_price', 'on_sale')
        }),
        ('Stock', {
            'fields': ('stock_status', 'stock_quantity', 'manage_stock')
        }),
        ('Dimensions', {
            'fields': ('weight', 'length', 'width', 'height'),
            'classes': ('collapse',)
        }),
        ('Image', {
            'fields': ('image_url', 'image_preview')
        }),
        ('Timestamps', {
            'fields': ('date_created_wc', 'date_modified_wc', 'synced_at', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def product_name(self, obj):
        """Display parent product name"""
        return obj.product.name[:40] + '...' if len(obj.product.name) > 40 else obj.product.name
    product_name.short_description = 'Product'
    product_name.admin_order_field = 'product__name'
    
    def attribute_description(self, obj):
        """Display variation attributes"""
        return obj.get_attribute_description()
    attribute_description.short_description = 'Attributes'
    
    def stock_status_display(self, obj):
        """Display stock status with color"""
        colors = {
            'instock': 'green',
            'outofstock': 'red',
            'onbackorder': 'orange',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.stock_status, 'gray'), obj.stock_status.upper()
        )
    stock_status_display.short_description = 'Stock'
    stock_status_display.admin_order_field = 'stock_status'
    
    def image_preview(self, obj):
        """Display variation image"""
        if obj.image_url:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.image_url
            )
        return "No image"
    image_preview.short_description = 'Image'


@admin.register(ProductSyncLog)
class ProductSyncLogAdmin(admin.ModelAdmin):
    """Admin for sync logs"""
    list_display = (
        'started_at', 'sync_type', 'status_display', 
        'categories_synced', 'products_synced', 'variations_synced',
        'errors_count', 'duration_display'
    )
    list_filter = ('sync_type', 'status', 'started_at')
    search_fields = ('error_details',)
    readonly_fields = (
        'sync_type', 'status', 'categories_synced', 'products_synced',
        'variations_synced', 'images_synced', 'errors_count', 'error_details',
        'started_at', 'completed_at', 'duration_seconds'
    )
    ordering = ('-started_at',)
    
    fieldsets = (
        ('Sync Info', {
            'fields': ('sync_type', 'status', 'started_at', 'completed_at', 'duration_seconds')
        }),
        ('Statistics', {
            'fields': ('categories_synced', 'products_synced', 'variations_synced', 'images_synced')
        }),
        ('Errors', {
            'fields': ('errors_count', 'error_details'),
            'classes': ('collapse',)
        }),
    )
    
    def status_display(self, obj):
        """Display status with color"""
        colors = {
            'started': 'blue',
            'success': 'green',
            'failed': 'red',
            'partial': 'orange',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'gray'), obj.get_status_display().upper()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def duration_display(self, obj):
        """Display duration in human-readable format"""
        if obj.duration_seconds:
            minutes, seconds = divmod(obj.duration_seconds, 60)
            if minutes > 0:
                return f"{minutes}m {seconds}s"
            return f"{seconds}s"
        return "—"
    duration_display.short_description = 'Duration'
    duration_display.admin_order_field = 'duration_seconds'


# ===========================
# TRANSLATION & PRICE MODELS ADMIN
# ===========================

@admin.register(TranslatedContent)
class TranslatedContentAdmin(admin.ModelAdmin):
    """Admin for translated content cache"""
    list_display = (
        'content_type', 'object_id', 'target_language',
        'source_text_preview', 'translated_text_preview',
        'is_verified', 'updated_at'
    )
    list_filter = ('content_type', 'target_language', 'is_verified', 'translation_engine')
    search_fields = ('object_id', 'source_text', 'translated_text')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    
    fieldsets = (
        ('Content Info', {
            'fields': ('content_type', 'object_id')
        }),
        ('Languages', {
            'fields': ('source_language', 'target_language')
        }),
        ('Content', {
            'fields': ('source_text', 'translated_text')
        }),
        ('Metadata', {
            'fields': ('translation_engine', 'is_verified', 'created_at', 'updated_at')
        }),
    )
    
    def source_text_preview(self, obj):
        """Display truncated source text"""
        text = obj.source_text[:80] + '...' if len(obj.source_text) > 80 else obj.source_text
        return text
    source_text_preview.short_description = 'Source Text'
    
    def translated_text_preview(self, obj):
        """Display truncated translated text"""
        text = obj.translated_text[:80] + '...' if len(obj.translated_text) > 80 else obj.translated_text
        return text
    translated_text_preview.short_description = 'Translated Text'


@admin.register(CategoryPriceMargin)
class CategoryPriceMarginAdmin(admin.ModelAdmin):
    """Admin for category price margins"""
    list_display = (
        'category_name', 'margin_display', 'products_count', 'is_active', 'updated_at'
    )
    list_filter = ('is_active', 'use_fixed_multiplier')
    search_fields = ('category__name', 'notes')
    readonly_fields = ('created_at', 'updated_at', 'products_count')
    ordering = ('category__name',)
    actions = ['activate_margins', 'deactivate_margins', 'apply_20_percent', 'apply_30_percent', 'apply_40_percent']
    
    fieldsets = (
        ('Category', {
            'fields': ('category',)
        }),
        ('Margin Configuration', {
            'fields': ('margin_percentage', 'use_fixed_multiplier', 'fixed_multiplier'),
            'description': 'Configure profit margin for this category. Example: 30% margin means selling price = cost × 1.30'
        }),
        ('Status', {
            'fields': ('is_active', 'notes')
        }),
        ('Statistics', {
            'fields': ('products_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def category_name(self, obj):
        """Display category name"""
        return obj.category.name
    category_name.short_description = 'Category'
    category_name.admin_order_field = 'category__name'
    
    def products_count(self, obj):
        """Count products in this category"""
        count = obj.category.products.filter(status='publish').count()
        return format_html(
            '<span style="color: #666;">{} products</span>',
            count
        )
    products_count.short_description = 'Products'
    
    def margin_display(self, obj):
        """Display margin configuration"""
        if obj.use_fixed_multiplier:
            return format_html(
                '<span style="color: blue; font-weight: bold;">x{}</span>',
                obj.fixed_multiplier
            )
        return format_html(
            '<span style="color: green; font-weight: bold;">+{}%</span>',
            obj.margin_percentage
        )
    margin_display.short_description = 'Margin'
    
    # Admin actions
    def activate_margins(self, request, queryset):
        """Activate selected margins"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} margins activated successfully.')
    activate_margins.short_description = 'Activate selected margins'
    
    def deactivate_margins(self, request, queryset):
        """Deactivate selected margins"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} margins deactivated successfully.')
    deactivate_margins.short_description = 'Deactivate selected margins'
    
    def apply_20_percent(self, request, queryset):
        """Apply 20 percent margin to selected categories"""
        updated = queryset.update(margin_percentage=20, use_fixed_multiplier=False, is_active=True)
        self.message_user(request, f'20% margin applied to {updated} categories.')
    apply_20_percent.short_description = 'Apply 20 percent margin'
    
    def apply_30_percent(self, request, queryset):
        """Apply 30 percent margin to selected categories"""
        updated = queryset.update(margin_percentage=30, use_fixed_multiplier=False, is_active=True)
        self.message_user(request, f'30% margin applied to {updated} categories.')
    apply_30_percent.short_description = 'Apply 30 percent margin'
    
    def apply_40_percent(self, request, queryset):
        """Apply 40 percent margin to selected categories"""
        updated = queryset.update(margin_percentage=40, use_fixed_multiplier=False, is_active=True)
        self.message_user(request, f'40% margin applied to {updated} categories.')
    apply_40_percent.short_description = 'Apply 40 percent margin'


@admin.register(DefaultPriceMargin)
class DefaultPriceMarginAdmin(admin.ModelAdmin):
    """Admin for default price margin"""
    list_display = (
        'margin_display', 'is_active', 'updated_at'
    )
    list_filter = ('is_active', 'use_fixed_multiplier')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Default Margin Configuration', {
            'fields': ('margin_percentage', 'use_fixed_multiplier', 'fixed_multiplier')
        }),
        ('Status', {
            'fields': ('is_active', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def margin_display(self, obj):
        """Display margin configuration"""
        if obj.use_fixed_multiplier:
            return format_html(
                '<span style="color: blue; font-weight: bold;">x{}</span>',
                obj.fixed_multiplier
            )
        return format_html(
            '<span style="color: green; font-weight: bold;">+{}%</span>',
            obj.margin_percentage
        )
    margin_display.short_description = 'Default Margin'


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
                    if model['object_name'] in ['User', 'PasswordCode', 'UserAddress', 'UserGallery', 'UserLink', 'GuestUser', 'Feed']
                ]
            },
            {
                'name': _('WooCommerce Products'),
                'app_label': 'woocommerce_management',
                'models': [
                    model for model in app_dict.get('crushme_app', {}).get('models', [])
                    if model['object_name'] in [
                        'WooCommerceCategory', 
                        'WooCommerceProduct', 
                        'WooCommerceProductVariation',
                        'CategoryPriceMargin',
                        'DefaultPriceMargin',
                        'TranslatedContent',
                        'ProductSyncLog'
                    ]
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
                'name': _('Review Management'),
                'app_label': 'review_management',
                'models': [
                    model for model in app_dict.get('crushme_app', {}).get('models', [])
                    if model['object_name'] in ['Review']
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
admin_site.register(UserAddress, UserAddressAdmin)
admin_site.register(UserGallery, UserGalleryAdmin)
admin_site.register(UserLink, UserLinkAdmin)
admin_site.register(GuestUser, GuestUserAdmin)
admin_site.register(Feed, FeedAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(Cart, CartAdmin)
# CartItem is managed through CartAdmin inline
admin_site.register(Order, OrderAdmin)
# OrderItem is managed through OrderAdmin inline
admin_site.register(WishList, WishListAdmin)
# WishListItem is managed through WishListAdmin inline
admin_site.register(FavoriteWishList, FavoriteWishListAdmin)
admin_site.register(Review, ReviewAdmin)

# WooCommerce models
admin_site.register(WooCommerceCategory, WooCommerceCategoryAdmin)
admin_site.register(WooCommerceProduct, WooCommerceProductAdmin)
admin_site.register(WooCommerceProductVariation, WooCommerceProductVariationAdmin)
admin_site.register(ProductSyncLog, ProductSyncLogAdmin)
admin_site.register(TranslatedContent, TranslatedContentAdmin)

# Price Margin models (IMPORTANT!)
admin_site.register(CategoryPriceMargin, CategoryPriceMarginAdmin)
admin_site.register(DefaultPriceMargin, DefaultPriceMarginAdmin)