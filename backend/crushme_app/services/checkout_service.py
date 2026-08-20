"""Build immutable, server-authoritative checkout payloads."""

from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from rest_framework.exceptions import ValidationError

from ..models import (
    DiscountCode,
    UserAddress,
    WooCommerceProduct,
    WooCommerceProductVariation,
)
from ..serializers.payment_serializers import CheckoutInputSerializer
from ..utils import calculate_shipping_cost
from ..utils.currency_converter import CurrencyConverter


MONEY_QUANTUM = {
    'COP': Decimal('1'),
    'USD': Decimal('0.01'),
}


def _money(value, currency):
    return Decimal(str(value)).quantize(MONEY_QUANTUM[currency], rounding=ROUND_HALF_UP)


def _price_for_currency(price_cop, currency):
    converted = CurrencyConverter.convert_price(price_cop, currency)
    if converted is None:
        raise ValidationError({'items': 'A product does not have a valid price.'})
    return _money(converted, currency)


def _receiver_shipping_data(receiver_username):
    address = UserAddress.objects.filter(
        user__username=receiver_username,
        is_default_shipping=True,
    ).first()
    if not address:
        address = UserAddress.objects.filter(user__username=receiver_username).first()
    if not address:
        raise ValidationError({
            'receiver_username': 'The gift recipient has no shipping address.'
        })

    return {
        'shipping_address': address.address_line_1,
        'shipping_address_line_2': address.address_line_2 or '',
        'shipping_city': address.city,
        'shipping_state': address.state,
        'shipping_postal_code': address.zip_code,
        'shipping_country': address.country,
        'phone_number': address.guest_phone or '',
    }


def _canonical_items(items, currency):
    quantities = defaultdict(int)
    for item in items:
        key = (item['woocommerce_product_id'], item.get('variation_id'))
        quantities[key] += item['quantity']
        if quantities[key] > 100:
            raise ValidationError({'items': 'A product quantity exceeds the allowed limit.'})

    dropshipping_id = getattr(settings, 'DROPSHIPPING_PRODUCT_ID', 48500)
    submitted_dropshipping = any(product_id == dropshipping_id for product_id, _ in quantities)
    quantities = {
        key: quantity
        for key, quantity in quantities.items()
        if key[0] != dropshipping_id
    }

    product_ids = {product_id for product_id, _ in quantities}
    product_ids.add(dropshipping_id)
    products = {
        product.wc_id: product
        for product in WooCommerceProduct.objects.filter(wc_id__in=product_ids).prefetch_related(
            'categories'
        )
    }
    missing_ids = product_ids.difference(products)
    missing_ids.discard(dropshipping_id)
    if missing_ids:
        raise ValidationError({'items': 'One or more products are unavailable.'})

    variation_ids = {
        variation_id
        for _, variation_id in quantities
        if variation_id is not None
    }
    variations = {
        variation.wc_id: variation
        for variation in WooCommerceProductVariation.objects.filter(
            wc_id__in=variation_ids
        ).select_related('product')
    }
    if variation_ids.difference(variations):
        raise ValidationError({'items': 'One or more product variations are unavailable.'})

    canonical = []
    for (product_id, variation_id), quantity in quantities.items():
        product = products[product_id]
        if product.status != 'publish' or product.stock_status != 'instock':
            raise ValidationError({'items': 'One or more products are unavailable.'})

        priced_item = product
        if variation_id is not None:
            variation = variations[variation_id]
            if variation.product_id != product.id or variation.status != 'publish':
                raise ValidationError({'items': 'A variation does not belong to its product.'})
            if variation.stock_status != 'instock':
                raise ValidationError({'items': 'One or more product variations are unavailable.'})
            priced_item = variation
        elif product.is_variable:
            raise ValidationError({'items': 'A variation is required for a variable product.'})

        if priced_item.manage_stock and priced_item.stock_quantity is not None:
            if quantity > priced_item.stock_quantity:
                raise ValidationError({'items': 'Requested quantity exceeds available stock.'})

        canonical.append({
            'woocommerce_product_id': product.wc_id,
            'woocommerce_variation_id': variation_id,
            'variation_id': variation_id,
            'product_name': product.name[:127],
            'quantity': quantity,
            'unit_price': str(_price_for_currency(priced_item.final_price, currency)),
        })

    dropshipping_product = products.get(dropshipping_id)
    if dropshipping_product and dropshipping_product.status == 'publish':
        if dropshipping_product.stock_status != 'instock' or dropshipping_product.final_price is None:
            raise ValidationError({'items': 'The shipping surcharge is unavailable.'})
        canonical.append({
            'woocommerce_product_id': dropshipping_product.wc_id,
            'woocommerce_variation_id': None,
            'variation_id': None,
            'product_name': dropshipping_product.name[:127],
            'quantity': 1,
            'unit_price': str(
                _price_for_currency(dropshipping_product.final_price, currency)
            ),
        })
    elif submitted_dropshipping:
        raise ValidationError({'items': 'The shipping surcharge is unavailable.'})

    return canonical


def build_checkout_order(data, currency, authenticated_user=None, language='en'):
    """Validate checkout input and replace all monetary fields with server values."""
    currency = currency.upper()
    if currency not in MONEY_QUANTUM:
        raise ValidationError({'currency': 'Unsupported payment currency.'})

    serializer = CheckoutInputSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    checkout = dict(serializer.validated_data)

    if checkout['is_gift']:
        checkout.update(_receiver_shipping_data(checkout['receiver_username']))
    if authenticated_user and authenticated_user.is_authenticated:
        checkout['customer_email'] = authenticated_user.email
        checkout['sender_username'] = authenticated_user.username

    items = _canonical_items(checkout.pop('items'), currency)
    dropshipping_id = getattr(settings, 'DROPSHIPPING_PRODUCT_ID', 48500)
    item_total = sum(
        Decimal(item['unit_price']) * item['quantity']
        for item in items
    )
    discount_base = sum(
        Decimal(item['unit_price']) * item['quantity']
        for item in items
        if item['woocommerce_product_id'] != dropshipping_id
    )

    discount_code = (checkout.get('discount_code') or '').strip().upper()
    discount_percentage = Decimal('0')
    if discount_code:
        discount = DiscountCode.objects.filter(code=discount_code, is_active=True).first()
        if not discount or not discount.is_valid():
            raise ValidationError({'discount_code': 'The discount code is not valid.'})
        discount_percentage = Decimal(discount.discount_percentage)

    discount_amount = _money(
        discount_base * discount_percentage / Decimal('100'),
        currency,
    )
    shipping_cop = calculate_shipping_cost(checkout['shipping_city'])
    shipping = _price_for_currency(shipping_cop, currency)
    total = _money(item_total + shipping - discount_amount, currency)
    if total <= 0:
        raise ValidationError({'total': 'The checkout total must be positive.'})

    canonical = {
        **checkout,
        'items': items,
        'shipping': str(shipping),
        'subtotal': str(item_total),
        'discount_code': discount_code or None,
        'discount_percentage': str(discount_percentage),
        'discount_amount': str(discount_amount),
        'total': str(total),
        'currency': currency,
        'language': 'es' if str(language).lower().startswith('es') else 'en',
    }
    return canonical
