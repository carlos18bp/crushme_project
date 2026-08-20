"""Create the deterministic scenario used by the local Playwright harness."""

import os
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from crushme_app.fake_data_guard import ensure_fake_data_allowed
from crushme_app.models import (
    User,
    UserAddress,
    WooCommerceCategory,
    WooCommerceProduct,
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

        category, _ = WooCommerceCategory.objects.update_or_create(
            wc_id=134,
            defaults={
                'name': 'Juguetes',
                'slug': 'juguetes',
                'product_count': 1,
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

        self.stdout.write(self.style.SUCCESS('E2E scenario is ready.'))
