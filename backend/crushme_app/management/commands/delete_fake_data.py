"""
Command to delete all fake data from CrushMe e-commerce platform
Based on gym_project pattern
Usage: python manage.py delete_fake_data --confirm
"""
from django.core.management.base import BaseCommand
from crushme_app.models import (
    User, Product, Cart, CartItem, Order, OrderItem,
    WishList, WishListItem, FavoriteWishList, PasswordCode
)
from django_attachments.models import Library, Attachment


class Command(BaseCommand):
    help = 'Delete all fake data for users, products, carts, orders, and wishlists'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all fake data'
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.ERROR(
                    '⚠️  This command will delete ALL data from the database!\n'
                    'Use --confirm flag if you are sure you want to proceed:\n'
                    'python manage.py delete_fake_data --confirm'
                )
            )
            return

        self.stdout.write(self.style.WARNING('🗑️  Starting deletion of all fake data...'))
        self.stdout.write('')

        # Delete in reverse order of dependencies to avoid foreign key constraints
        
        # Delete wishlist-related data
        self.stdout.write('💝 Deleting wishlist data...')
        for favorite in FavoriteWishList.objects.all():
            favorite.delete()
            self.stdout.write(self.style.SUCCESS(f'FavoriteWishList "{favorite}" deleted'))

        for item in WishListItem.objects.all():
            item.delete()
            self.stdout.write(self.style.SUCCESS(f'WishListItem "{item}" deleted'))

        for wishlist in WishList.objects.all():
            wishlist.delete()
            self.stdout.write(self.style.SUCCESS(f'WishList "{wishlist}" deleted'))

        # Delete order-related data
        self.stdout.write('📋 Deleting order data...')
        for item in OrderItem.objects.all():
            item.delete()
            self.stdout.write(self.style.SUCCESS(f'OrderItem "{item}" deleted'))

        for order in Order.objects.all():
            order.delete()
            self.stdout.write(self.style.SUCCESS(f'Order "{order}" deleted'))

        # Delete cart-related data
        self.stdout.write('🛒 Deleting cart data...')
        for item in CartItem.objects.all():
            item.delete()
            self.stdout.write(self.style.SUCCESS(f'CartItem "{item}" deleted'))

        for cart in Cart.objects.all():
            cart.delete()
            self.stdout.write(self.style.SUCCESS(f'Cart "{cart}" deleted'))

        # Delete products and their galleries
        self.stdout.write('📦 Deleting product data...')
        for product in Product.objects.all():
            product_name = str(product)
            gallery_name = str(product.gallery) if product.gallery else None
            
            # The Product.delete() method will handle gallery deletion automatically
            product.delete()
            self.stdout.write(self.style.SUCCESS(f'Product "{product_name}" deleted'))
            if gallery_name:
                self.stdout.write(self.style.SUCCESS(f'Gallery "{gallery_name}" deleted'))

        # Delete password codes
        self.stdout.write('🔐 Deleting password codes...')
        for code in PasswordCode.objects.all():
            code.delete()
            self.stdout.write(self.style.SUCCESS(f'PasswordCode "{code}" deleted'))

        # Delete users (keep superusers)
        self.stdout.write('👥 Deleting users...')
        for user in User.objects.filter(is_superuser=False):
            user.delete()
            self.stdout.write(self.style.SUCCESS(f'User "{user}" deleted'))

        # Clean up any orphaned galleries and attachments
        self.stdout.write('🧹 Cleaning up orphaned data...')
        for attachment in Attachment.objects.all():
            attachment.delete()
            self.stdout.write(self.style.SUCCESS(f'Orphaned attachment "{attachment}" deleted'))

        for library in Library.objects.all():
            library.delete()
            self.stdout.write(self.style.SUCCESS(f'Orphaned library "{library}" deleted'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ All fake data deleted successfully!'))
        self.stdout.write('')
        self.stdout.write('🎯 Database is now clean and ready for fresh data or production use.')