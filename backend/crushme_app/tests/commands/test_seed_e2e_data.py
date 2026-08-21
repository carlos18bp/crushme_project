"""Behavior tests for the guarded deterministic E2E seed command."""

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from crushme_app.models import (
    DiscountCode,
    FavoriteProduct,
    Feed,
    Order,
    PasswordCode,
    Review,
    User,
    UserAddress,
    WishList,
    WooCommerceCategory,
    WooCommerceProduct,
    WooCommerceProductVariation,
)


def test_seed_e2e_data_refuses_the_regular_test_environment(db):
    """Reject the command outside the dedicated E2E environment."""
    with pytest.raises(CommandError, match="requires DJANGO_ENV=e2e"):
        call_command("seed_e2e_data")


@override_settings(DJANGO_ENV="e2e", FAKE_DATA_ALLOWED=True)
def test_seed_e2e_data_is_idempotent(db):
    """Keep deterministic fixture identities stable across repeated runs."""
    call_command("seed_e2e_data")
    call_command("seed_e2e_data")

    assert User.objects.filter(username="e2e_user").count() == 1
    assert WooCommerceCategory.objects.filter(wc_id=134).count() == 1
    assert WooCommerceProduct.objects.filter(wc_id=900001).count() == 1


@override_settings(DJANGO_ENV="e2e", FAKE_DATA_ALLOWED=True)
def test_seed_e2e_data_creates_gift_recipient(db):
    """Create a recipient with usable shipping data for gift checkout."""
    call_command("seed_e2e_data")

    recipient = User.objects.get(username="e2e_recipient")
    address = UserAddress.objects.get(
        user=recipient,
        is_default_shipping=True,
    )
    assert recipient.email == "e2e-recipient@example.test"
    assert address.city == "Medellin"


@override_settings(DJANGO_ENV="e2e", FAKE_DATA_ALLOWED=True)
def test_seed_e2e_data_creates_complete_browser_scenario(db):
    """Create deterministic records needed by catalog, profile, and admin flows."""
    call_command("seed_e2e_data")

    user = User.objects.get(username="e2e_user")
    wishlist = WishList.objects.get(name="E2E Public Wishes")
    order = Order.objects.get(order_number="E2E-ORDER-0001")

    assert User.objects.get(username="e2e_admin").is_superuser is True
    assert User.objects.get(username="e2e_crush").is_crush is True
    assert User.objects.get(username="e2e_pending_crush").check_password(
        "E2E-pending-password-123!"
    )
    assert wishlist.items.get().woocommerce_product_id == 900001
    assert user.purchase_history.get() == order
    assert user.received_gifts.get().order_number == "E2E-GIFT-0001"


@override_settings(DJANGO_ENV="e2e", FAKE_DATA_ALLOWED=True)
def test_seed_e2e_data_creates_deterministic_feature_fixtures(db):
    """Create stable records for negative and display outcome coverage."""
    call_command("seed_e2e_data")

    user = User.objects.get(username="e2e_user")

    assert (
        WooCommerceProductVariation.objects.filter(
            product__wc_id=900002,
        ).count()
        == 2
    )
    assert FavoriteProduct.objects.get(user=user).woocommerce_product_id == 900001
    assert Review.objects.get(woocommerce_product_id=900001).rating == 5
    assert DiscountCode.objects.get(code="E2E10").discount_percentage == 10
    assert Feed.objects.get(user=user).text == "E2E deterministic feed update"
    assert PasswordCode.objects.get(user=user, code="4242").used is False


@override_settings(DJANGO_ENV="production", FAKE_DATA_ALLOWED=True)
def test_seed_e2e_data_refuses_production_even_with_opt_in(db):
    """Reject production even when the fake-data flag is enabled."""
    with pytest.raises(CommandError, match="DJANGO_ENV is production"):
        call_command("seed_e2e_data")
