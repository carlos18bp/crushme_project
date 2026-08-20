from decimal import Decimal

import pytest

from crushme_app.models import (
    DiscountCode,
    User,
    UserAddress,
    WooCommerceProduct,
    WooCommerceProductVariation,
)
from crushme_app.services.checkout_service import build_checkout_order


pytestmark = pytest.mark.django_db


def _product(wc_id, price, name='Canonical product', product_type='simple'):
    return WooCommerceProduct.objects.create(
        wc_id=wc_id,
        name=name,
        slug=f'product-{wc_id}',
        permalink=f'https://store.example/products/{wc_id}',
        product_type=product_type,
        price=Decimal(str(price)),
        regular_price=Decimal(str(price)),
        stock_status='instock',
        status='publish',
    )


def _checkout_data(product_id=101, **overrides):
    data = {
        'items': [{
            'woocommerce_product_id': product_id,
            'product_name': 'Client-controlled name',
            'quantity': 1,
            'unit_price': 1,
        }],
        'customer_email': 'buyer@example.com',
        'customer_name': 'Buyer',
        'shipping_address': 'Street 1',
        'shipping_city': 'Medellin',
        'shipping_state': 'Antioquia',
        'shipping_postal_code': '050001',
        'shipping_country': 'CO',
        'phone_number': '+573001234567',
        'shipping': 1,
        'total': 2,
    }
    data.update(overrides)
    return data


def test_checkout_replaces_client_controlled_commercial_fields():
    _product(101, '10000.00')

    checkout = build_checkout_order(_checkout_data(), 'COP')

    assert checkout['items'][0]['product_name'] == 'Canonical product'
    assert checkout['items'][0]['unit_price'] == '10000'
    assert checkout['shipping'] == '10500'
    assert checkout['total'] == '20500'


def test_checkout_applies_discount_only_to_merchandise():
    _product(101, '10000.00')
    _product(48500, '5000.00', name='Shipping surcharge')
    DiscountCode.objects.create(code='SAVE10', discount_percentage=10)

    checkout = build_checkout_order(
        _checkout_data(shipping_city='Bogota', discount_code='save10'),
        'COP',
    )

    assert [item['woocommerce_product_id'] for item in checkout['items']] == [101, 48500]
    assert checkout['discount_amount'] == '1000'
    assert checkout['shipping'] == '15000'
    assert checkout['total'] == '29000'


def test_checkout_uses_selected_variation_price():
    product = _product(202, '10000.00', product_type='variable')
    variation = WooCommerceProductVariation.objects.create(
        wc_id=303,
        wc_product_id=product.wc_id,
        product=product,
        permalink='https://store.example/products/202?variation=303',
        price=Decimal('12500.00'),
        regular_price=Decimal('12500.00'),
        stock_status='instock',
        status='publish',
    )
    data = _checkout_data(product_id=product.wc_id)
    data['items'][0]['woocommerce_variation_id'] = variation.wc_id

    checkout = build_checkout_order(data, 'COP')

    assert checkout['items'][0]['variation_id'] == variation.wc_id
    assert checkout['items'][0]['unit_price'] == '12500'


def test_gift_checkout_uses_recipient_address_instead_of_client_address():
    _product(101, '10000.00')
    receiver = User.objects.create_user(
        username='receiver',
        email='receiver@example.com',
        password='unused',
    )
    UserAddress.objects.create(
        user=receiver,
        country='CO',
        state='San Andres',
        city='Providencia',
        zip_code='880001',
        address_line_1='Recipient street',
        guest_phone='+573009876543',
        is_default_shipping=True,
    )

    checkout = build_checkout_order(
        _checkout_data(is_gift=True, receiver_username='receiver'),
        'COP',
    )

    assert checkout['shipping_address'] == 'Recipient street'
    assert checkout['shipping_city'] == 'Providencia'
    assert checkout['shipping'] == '45000'
