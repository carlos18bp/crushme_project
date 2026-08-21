"""Behavior tests for commerce input contracts."""

from types import SimpleNamespace

import pytest
from django.contrib.auth.models import AnonymousUser

from crushme_app.models import Order, Review
from crushme_app.serializers.order_serializers import (
    OrderSearchSerializer,
    OrderStatusUpdateSerializer,
)
from crushme_app.serializers.payment_serializers import (
    CheckoutInputSerializer,
    CheckoutItemInputSerializer,
)
from crushme_app.serializers.review_serializers import ReviewCreateSerializer
from crushme_app.serializers.wishlist_serializers import (
    WishListCreateUpdateSerializer,
    WishListShippingSerializer,
)

pytestmark = pytest.mark.django_db


def _order(user, status="pending"):
    return Order.objects.create(
        user=user,
        email=user.email,
        name="Test Buyer",
        total="100.00",
        status=status,
        address_line_1="Test street 123",
        city="Medellin",
        state="Antioquia",
        zipcode="050001",
        country="CO",
        phone="+573001234567",
    )


def _checkout_payload(**overrides):
    data = {
        "items": [{"woocommerce_product_id": 900001, "quantity": 1}],
        "customer_email": "buyer@example.test",
        "customer_name": "Test Buyer",
        "shipping_address": "Test street 123",
        "shipping_city": "Medellin",
        "shipping_state": "Antioquia",
        "shipping_postal_code": "050001",
    }
    data.update(overrides)
    return data


def test_wishlist_rejects_one_character_name():
    """Fails if users can persist an unusable one-character wishlist name."""
    serializer = WishListCreateUpdateSerializer(data={"name": "x"})

    assert serializer.is_valid() is False
    assert (
        serializer.errors["name"][0]
        == "Wishlist name must be at least 2 characters long."
    )


def test_wishlist_rejects_unknown_shipping_keys():
    """Fails if arbitrary nested shipping data bypasses the documented contract."""
    serializer = WishListCreateUpdateSerializer(
        data={"name": "Birthday", "shipping_data": {"secret_note": "unsafe"}},
    )

    assert serializer.is_valid() is False
    assert (
        serializer.errors["shipping_data"][0]
        == "Invalid shipping data keys: secret_note"
    )


def test_wishlist_shipping_rejects_short_phone():
    """Fails if an unusable recipient phone reaches gift checkout."""
    serializer = WishListShippingSerializer(data={"phone": "1234"})

    assert serializer.is_valid() is False
    assert (
        serializer.errors["phone"][0]
        == "Phone number must be at least 10 characters long."
    )


def test_anonymous_review_requires_identity_fields():
    """Fails if anonymous reviews are accepted without a traceable name and email."""
    request = SimpleNamespace(user=AnonymousUser())
    serializer = ReviewCreateSerializer(
        data={"woocommerce_product_id": 900001, "rating": 5, "comment": "Excellent"},
        context={"request": request},
    )

    assert serializer.is_valid() is False
    assert (
        serializer.errors["anonymous_name"][0]
        == "El nombre es requerido para usuarios anónimos"
    )


def test_authenticated_user_cannot_review_product_twice(user_factory):
    """Fails if one account can inflate a product rating with duplicate reviews."""
    user = user_factory()
    Review.objects.create(
        user=user, woocommerce_product_id=900001, rating=5, comment="First"
    )
    request = SimpleNamespace(user=user)
    serializer = ReviewCreateSerializer(
        data={"woocommerce_product_id": 900001, "rating": 4, "comment": "Second"},
        context={"request": request},
    )

    assert serializer.is_valid() is False
    assert serializer.errors["non_field_errors"][0] == (
        "Ya has hecho una reseña de este producto. Puedes editarla o eliminarla."
    )


def test_checkout_rejects_conflicting_variation_ids():
    """Fails if checkout accepts two different identifiers for one variation."""
    serializer = CheckoutItemInputSerializer(
        data={
            "woocommerce_product_id": 900001,
            "woocommerce_variation_id": 301,
            "variation_id": 302,
            "quantity": 1,
        }
    )

    assert serializer.is_valid() is False
    assert serializer.errors["non_field_errors"][0] == "Conflicting variation IDs"


def test_gift_checkout_requires_receiver_username():
    """Fails if a gift order is accepted without a resolvable recipient."""
    serializer = CheckoutInputSerializer(data=_checkout_payload(is_gift=True))

    assert serializer.is_valid() is False
    assert (
        serializer.errors["receiver_username"][0] == "This field is required for gifts."
    )


def test_order_status_rejects_skipping_processing(user_factory):
    """Fails if an order moves from pending directly to shipped."""
    order = _order(user_factory(), status="pending")
    serializer = OrderStatusUpdateSerializer(
        order, data={"status": "shipped"}, partial=True
    )

    assert serializer.is_valid() is False
    assert (
        serializer.errors["status"][0]
        == "Cannot change status from 'pending' to 'shipped'."
    )


def test_order_status_sets_shipping_timestamp(user_factory):
    """Fails if a valid shipped transition omits operational timestamps."""
    order = _order(user_factory(), status="processing")
    serializer = OrderStatusUpdateSerializer(
        order, data={"status": "shipped"}, partial=True
    )

    assert serializer.is_valid() is True
    updated = serializer.save()
    assert updated.status == "shipped"
    assert updated.shipped_at is not None


def test_order_search_rejects_inverted_total_range():
    """Fails if an impossible total range reaches the admin query."""
    serializer = OrderSearchSerializer(
        data={"min_total": "200.00", "max_total": "100.00"}
    )

    assert serializer.is_valid() is False
    assert serializer.errors["non_field_errors"][0] == (
        "Minimum total cannot be greater than maximum total."
    )
