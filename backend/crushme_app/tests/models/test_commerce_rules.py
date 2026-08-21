"""Behavior tests for core commerce model rules."""

from decimal import Decimal

import pytest

from crushme_app.models import (
    DiscountCode,
    FavoriteProduct,
    FavoriteWishList,
    Order,
    OrderItem,
    Review,
    WishList,
)

pytestmark = pytest.mark.django_db


def _order(user, status="pending"):
    return Order.objects.create(
        user=user,
        email=user.email,
        name="Test Buyer",
        total=Decimal("120000.00"),
        status=status,
        address_line_1="Test street 123",
        city="Medellin",
        state="Antioquia",
        zipcode="050001",
        country="CO",
        phone="+573001234567",
    )


def test_order_moves_from_processing_to_shipped(user_factory):
    """Fails if shipping an eligible order omits its status or timestamp."""
    order = _order(user_factory(), status="processing")

    changed = order.mark_as_shipped()

    order.refresh_from_db()
    assert changed is True
    assert order.status == "shipped"
    assert order.shipped_at is not None


def test_order_cannot_skip_directly_to_shipped(user_factory):
    """Fails if a pending order bypasses the processing state."""
    order = _order(user_factory(), status="pending")

    changed = order.mark_as_shipped()

    order.refresh_from_db()
    assert changed is False
    assert order.status == "pending"
    assert order.shipped_at is None


def test_order_delivers_only_after_shipping(user_factory):
    """Fails if delivery is accepted before a shipment exists."""
    order = _order(user_factory(), status="processing")

    early_delivery = order.mark_as_delivered()
    order.mark_as_shipped()
    delivered = order.mark_as_delivered()

    order.refresh_from_db()
    assert early_delivery is False
    assert delivered is True
    assert order.status == "delivered"
    assert order.delivered_at is not None


def test_order_total_items_sums_quantities(user_factory):
    """Fails if purchase history counts lines instead of purchased units."""
    order = _order(user_factory())
    OrderItem.objects.create(
        order=order,
        woocommerce_product_id=10,
        quantity=2,
        unit_price=Decimal("10000.00"),
        product_name="First product",
    )
    OrderItem.objects.create(
        order=order,
        woocommerce_product_id=11,
        quantity=3,
        unit_price=Decimal("20000.00"),
        product_name="Second product",
    )

    assert order.total_items == 5


def test_discount_stops_at_its_usage_limit():
    """Fails if a discount remains redeemable after reaching max uses."""
    discount = DiscountCode.objects.create(
        code="LIMIT1",
        discount_percentage=Decimal("10.00"),
        max_uses=1,
    )

    discount.increment_usage()

    discount.refresh_from_db()
    assert discount.times_used == 1
    assert discount.is_valid() is False


def test_inactive_discount_is_never_valid():
    """Fails if disabling a campaign does not stop redemptions."""
    discount = DiscountCode.objects.create(
        code="OFF10",
        discount_percentage=Decimal("10.00"),
        is_active=False,
    )

    assert discount.is_valid() is False


def test_wishlist_deduplicates_woocommerce_products(user_factory):
    """Fails if adding one WooCommerce product twice creates duplicate lines."""
    wishlist = WishList.objects.create(user=user_factory(), name="Birthday")

    first, first_created = wishlist.add_woocommerce_product(
        900001, {"name": "Rose wand"}
    )
    second, second_created = wishlist.add_woocommerce_product(
        900001, {"name": "Duplicate"}
    )

    assert first_created is True
    assert second_created is False
    assert second.id == first.id
    assert wishlist.items.count() == 1


def test_wishlist_shipping_updates_only_submitted_fields(user_factory):
    """Fails if a partial shipping edit erases previously stored recipient data."""
    wishlist = WishList.objects.create(
        user=user_factory(),
        name="Birthday",
        shipping_data={"name": "Recipient", "address": "Old street 123"},
    )

    wishlist.set_shipping_data(phone="+573001234567")

    wishlist.refresh_from_db()
    assert wishlist.shipping_name == "Recipient"
    assert wishlist.shipping_address == "Old street 123"
    assert wishlist.shipping_phone == "+573001234567"


def test_user_cannot_favorite_own_wishlist(user_factory):
    """Fails if self-favorites inflate a wishlist's public popularity."""
    user = user_factory()
    wishlist = WishList.objects.create(user=user, name="Private list")

    with pytest.raises(ValueError, match="cannot favorite their own"):
        FavoriteWishList.add_favorite(user, wishlist)

    assert FavoriteWishList.objects.count() == 0


def test_favorite_product_updates_cached_data_without_duplication(user_factory):
    """Fails if refreshing a favorite creates a second favorite row."""
    user = user_factory()
    FavoriteProduct.add_favorite(user, 900001, {"name": "Old name"})

    favorite, created = FavoriteProduct.add_favorite(
        user, 900001, {"name": "Current name"}
    )

    assert created is False
    assert favorite.product_data == {"name": "Current name"}
    assert (
        FavoriteProduct.objects.filter(user=user, woocommerce_product_id=900001).count()
        == 1
    )


def test_review_statistics_ignore_inactive_reviews(user_factory):
    """Fails if moderated reviews still affect public ratings."""
    user = user_factory()
    Review.objects.create(
        user=user, woocommerce_product_id=900001, rating=5, comment="Visible"
    )
    Review.objects.create(
        anonymous_name="Hidden",
        anonymous_email="hidden@example.test",
        woocommerce_product_id=900001,
        rating=1,
        comment="Hidden",
        is_active=False,
    )

    stats = Review.get_product_stats(900001)

    assert stats["total_reviews"] == 1
    assert stats["average_rating"] == 5.0
    assert stats["rating_distribution"]["stars_5"] == 1
    assert stats["rating_distribution"]["stars_1"] == 0
