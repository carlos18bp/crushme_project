"""Create the deterministic scenario used by the local Playwright harness."""

import os
import uuid
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from crushme_app.fake_data_guard import ensure_fake_data_allowed
from crushme_app.models import (
    DiscountCode,
    FavoriteProduct,
    FavoriteWishList,
    Feed,
    Order,
    OrderItem,
    PasswordCode,
    Review,
    User,
    UserAddress,
    WooCommerceCategory,
    WooCommerceProduct,
    WooCommerceProductVariation,
    WishList,
    WishListItem,
)


class Command(BaseCommand):
    help = 'Seed the deterministic CrushMe Playwright scenario'

    @transaction.atomic
    def handle(self, *args, **options):
        ensure_fake_data_allowed('seed_e2e_data')
        if settings.DJANGO_ENV != 'e2e':
            raise CommandError('seed_e2e_data requires DJANGO_ENV=e2e')

        username = os.environ.get('E2E_USERNAME', 'e2e_user')
        password = os.environ.get('E2E_USER_PASSWORD', 'E2E-password-123!')
        user, _ = User.objects.update_or_create(
            username=username,
            defaults={
                'email': 'e2e-user@example.test',
                'email_verified': True,
                'is_active': True,
                'first_name': 'E2E',
                'last_name': 'User',
            },
        )
        user.set_password(password)
        user.save(update_fields=['password'])
        UserAddress.objects.update_or_create(
            user=user,
            is_default_shipping=True,
            defaults={
                'country': 'CO',
                'state': 'Cundinamarca',
                'city': 'Bogota',
                'zip_code': '110111',
                'address_line_1': 'E2E buyer street 456',
                'guest_phone': '+573009876543',
            },
        )

        admin_username = os.environ.get('E2E_ADMIN_USERNAME', 'e2e_admin')
        admin_password = os.environ.get(
            'E2E_ADMIN_PASSWORD',
            'E2E-admin-password-123!',
        )
        admin, _ = User.objects.update_or_create(
            username=admin_username,
            defaults={
                'email': 'e2e-admin@example.test',
                'email_verified': True,
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'E2E',
                'last_name': 'Admin',
            },
        )
        admin.set_password(admin_password)
        admin.save(update_fields=['password'])

        recipient, _ = User.objects.update_or_create(
            username='e2e_recipient',
            defaults={
                'email': 'e2e-recipient@example.test',
                'email_verified': True,
                'is_active': True,
                'first_name': 'E2E',
                'last_name': 'Recipient',
            },
        )
        recipient.set_unusable_password()
        recipient.save(update_fields=['password'])
        UserAddress.objects.update_or_create(
            user=recipient,
            is_default_shipping=True,
            defaults={
                'country': 'CO',
                'state': 'Antioquia',
                'city': 'Medellin',
                'zip_code': '050001',
                'address_line_1': 'E2E recipient street 123',
                'guest_phone': '+573001234567',
            },
        )

        crush, _ = User.objects.update_or_create(
            username='e2e_crush',
            defaults={
                'email': 'e2e-crush@example.test',
                'email_verified': True,
                'is_active': True,
                'is_crush': True,
                'crush_verification_status': 'approved',
                'crush_verified_at': timezone.now(),
                'first_name': 'E2E',
                'last_name': 'Crush',
                'about': 'Deterministic public Crush profile.',
                'current_status': 'Available for E2E validation',
            },
        )
        crush.set_unusable_password()
        crush.save(update_fields=['password'])

        pending_crush, _ = User.objects.update_or_create(
            username='e2e_pending_crush',
            defaults={
                'email': 'e2e-pending-crush@example.test',
                'email_verified': True,
                'is_active': True,
                'is_crush': False,
                'crush_verification_status': 'pending',
                'crush_requested_at': timezone.now(),
                'first_name': 'E2E',
                'last_name': 'Pending Crush',
            },
        )
        pending_crush.set_password('E2E-pending-password-123!')
        pending_crush.save(update_fields=['password'])

        category, _ = WooCommerceCategory.objects.update_or_create(
            wc_id=134,
            defaults={
                'name': 'Juguetes',
                'slug': 'juguetes',
                'product_count': 2,
            },
        )
        product, _ = WooCommerceProduct.objects.update_or_create(
            wc_id=900001,
            defaults={
                'name': 'E2E Rose Quartz Wand',
                'slug': 'e2e-rose-quartz-wand',
                'permalink': 'https://example.test/e2e-product',
                'short_description': 'Deterministic Playwright catalog fixture.',
                'description': 'Isolated product data for end-to-end validation.',
                'price': Decimal('120000.00'),
                'regular_price': Decimal('120000.00'),
                'stock_status': 'instock',
                'stock_quantity': 10,
                'manage_stock': True,
                'status': 'publish',
                'featured': True,
            },
        )
        product.categories.set([category])

        variable_product, _ = WooCommerceProduct.objects.update_or_create(
            wc_id=900002,
            defaults={
                'name': 'E2E Variable Harness',
                'slug': 'e2e-variable-harness',
                'permalink': 'https://example.test/e2e-variable-product',
                'product_type': WooCommerceProduct.TYPE_VARIABLE,
                'short_description': 'Product with deterministic size options.',
                'description': 'Variable catalog fixture for Playwright.',
                'price': Decimal('135000.00'),
                'regular_price': Decimal('135000.00'),
                'stock_status': 'instock',
                'stock_quantity': 8,
                'manage_stock': True,
                'attributes': [
                    {
                        'name': 'Size',
                        'variation': True,
                        'options': ['Small', 'Large'],
                    },
                ],
                'default_attributes': [{'name': 'Size', 'option': 'Small'}],
                'status': 'publish',
                'featured': False,
            },
        )
        variable_product.categories.set([category])
        for wc_id, size, price, stock in (
            (910001, 'Small', '135000.00', 5),
            (910002, 'Large', '145000.00', 3),
        ):
            WooCommerceProductVariation.objects.update_or_create(
                wc_id=wc_id,
                defaults={
                    'wc_product_id': variable_product.wc_id,
                    'product': variable_product,
                    'permalink': f'https://example.test/e2e-variation-{wc_id}',
                    'price': Decimal(price),
                    'regular_price': Decimal(price),
                    'stock_status': 'instock',
                    'stock_quantity': stock,
                    'manage_stock': True,
                    'attributes': {'Size': size},
                    'status': 'publish',
                },
            )

        wishlist, _ = WishList.objects.update_or_create(
            id=900001,
            defaults={
                'unique_link': uuid.UUID('00000000-0000-4000-8000-000000000001'),
                'user': crush,
                'name': 'E2E Public Wishes',
                'description': 'A deterministic wishlist for browser validation.',
                'is_active': True,
                'is_public': True,
                'shipping_data': {
                    'name': 'E2E Crush',
                    'address': 'E2E crush street 789, Medellin',
                    'phone': '+573001112233',
                    'email': 'e2e-crush@example.test',
                },
            },
        )
        WishListItem.objects.update_or_create(
            wishlist=wishlist,
            woocommerce_product_id=product.wc_id,
            defaults={
                'notes': 'E2E seeded wish',
                'priority': 'high',
                'product_data': {
                    'name': product.name,
                    'price': str(product.price),
                    'stock_status': 'instock',
                    'stock_quantity': product.stock_quantity,
                    'images': [],
                },
            },
        )

        owned_wishlist, _ = WishList.objects.update_or_create(
            id=900002,
            defaults={
                'unique_link': uuid.UUID('00000000-0000-4000-8000-000000000002'),
                'user': user,
                'name': 'E2E Owned Wishes',
                'description': 'An owned wishlist for deterministic item management.',
                'is_active': True,
                'is_public': True,
            },
        )
        WishListItem.objects.update_or_create(
            wishlist=owned_wishlist,
            woocommerce_product_id=product.wc_id,
            defaults={
                'notes': 'E2E owned wish',
                'priority': 'medium',
                'product_data': {
                    'name': product.name,
                    'price': str(product.price),
                    'stock_status': 'instock',
                    'stock_quantity': product.stock_quantity,
                    'images': [],
                },
            },
        )

        WishList.objects.update_or_create(
            id=900003,
            defaults={
                'unique_link': uuid.UUID('00000000-0000-4000-8000-000000000003'),
                'user': crush,
                'name': 'E2E Empty Wishes',
                'description': 'A public wishlist with no available items.',
                'is_active': True,
                'is_public': True,
            },
        )
        FavoriteWishList.objects.get_or_create(user=user, wishlist=wishlist)
        FavoriteProduct.objects.update_or_create(
            user=user,
            woocommerce_product_id=product.wc_id,
            defaults={
                'product_data': {
                    'id': product.wc_id,
                    'name': product.name,
                    'price': str(product.price),
                    'images': [],
                },
                'cache_updated_at': timezone.now(),
            },
        )

        Review.objects.update_or_create(
            user=crush,
            woocommerce_product_id=product.wc_id,
            defaults={
                'rating': 5,
                'title': 'E2E verified review',
                'comment': 'Deterministic review content for Playwright.',
                'is_active': True,
                'is_verified_purchase': True,
            },
        )
        DiscountCode.objects.update_or_create(
            code='E2E10',
            defaults={
                'discount_percentage': Decimal('10.00'),
                'is_active': True,
                'times_used': 0,
                'max_uses': 100,
            },
        )
        Feed.objects.update_or_create(
            user=user,
            action='general',
            defaults={
                'text': 'E2E deterministic feed update',
                'style': 'timeline-midnight-rose',
            },
        )

        order, _ = Order.objects.update_or_create(
            order_number='E2E-ORDER-0001',
            defaults={
                'user': user,
                'total': Decimal('120000.00'),
                'status': 'processing',
                'email': user.email,
                'name': user.get_full_name(),
                'country': 'CO',
                'state': 'Cundinamarca',
                'city': 'Bogota',
                'zipcode': '110111',
                'address_line_1': 'E2E buyer street 456',
                'phone': '+573009876543',
                'payment_provider': 'paypal',
                'transaction_id': 'E2E-TXN-0001',
            },
        )
        OrderItem.objects.update_or_create(
            order=order,
            woocommerce_product_id=product.wc_id,
            defaults={
                'quantity': 1,
                'unit_price': Decimal('120000.00'),
                'product_name': product.name,
                'product_description': product.short_description,
            },
        )
        user.purchase_history.add(order)

        gift, _ = Order.objects.update_or_create(
            order_number='E2E-GIFT-0001',
            defaults={
                'user': crush,
                'total': Decimal('120000.00'),
                'status': 'delivered',
                'email': user.email,
                'name': user.get_full_name(),
                'country': 'CO',
                'state': 'Cundinamarca',
                'city': 'Bogota',
                'zipcode': '110111',
                'address_line_1': 'E2E buyer street 456',
                'phone': '+573009876543',
                'is_gift': True,
                'sender_username': crush.username,
                'receiver_username': user.username,
                'gift_message': 'A deterministic E2E gift.',
                'payment_provider': 'wompi',
                'transaction_id': 'E2E-TXN-GIFT-0001',
            },
        )
        OrderItem.objects.update_or_create(
            order=gift,
            woocommerce_product_id=product.wc_id,
            defaults={
                'quantity': 1,
                'unit_price': Decimal('120000.00'),
                'product_name': product.name,
                'product_description': product.short_description,
            },
        )
        user.received_gifts.add(gift)

        PasswordCode.objects.update_or_create(
            user=user,
            code_type='password_reset',
            code='4242',
            defaults={'used': False},
        )

        self.stdout.write(self.style.SUCCESS('E2E scenario is ready.'))
