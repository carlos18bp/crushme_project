"""Small explicit factories for behavior tests without factory-boy magic."""

from decimal import Decimal

from django_attachments.models import Library

from crushme_app.models import Product, User, WooCommerceCategory, WooCommerceProduct


def create_user(**overrides):
    password = overrides.pop('password', 'Test-password-123!')
    sequence = User.objects.count() + 1
    defaults = {
        'username': f'test_user_{sequence}',
        'email': f'test_user_{sequence}@example.test',
        'email_verified': True,
        'is_active': True,
    }
    defaults.update(overrides)
    return User.objects.create_user(password=password, **defaults)


def create_product(**overrides):
    sequence = Product.objects.count() + 1
    defaults = {
        'name': f'Test Product {sequence}',
        'description': 'Product created by the test factory.',
        'price': Decimal('29.99'),
        'stock_quantity': 10,
        'is_active': True,
        'gallery': Library.objects.create(title=f'Test Product {sequence}'),
    }
    defaults.update(overrides)
    return Product.objects.create(**defaults)


def create_woocommerce_product(**overrides):
    sequence = WooCommerceProduct.objects.count() + 1
    category = overrides.pop('category', None)
    defaults = {
        'wc_id': 900_000 + sequence,
        'name': f'Woo Test Product {sequence}',
        'slug': f'woo-test-product-{sequence}',
        'permalink': f'https://example.test/products/{sequence}',
        'price': Decimal('120000.00'),
        'regular_price': Decimal('120000.00'),
        'stock_status': 'instock',
        'stock_quantity': 10,
        'status': 'publish',
    }
    defaults.update(overrides)
    product = WooCommerceProduct.objects.create(**defaults)
    if category:
        product.categories.add(category)
    return product


def create_woocommerce_category(**overrides):
    sequence = WooCommerceCategory.objects.count() + 1
    defaults = {
        'wc_id': 800_000 + sequence,
        'name': f'Test Category {sequence}',
        'slug': f'test-category-{sequence}',
        'product_count': 1,
    }
    defaults.update(overrides)
    return WooCommerceCategory.objects.create(**defaults)
