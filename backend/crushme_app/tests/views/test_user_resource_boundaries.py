"""Authorization and isolation tests for user-owned resources."""

from decimal import Decimal
from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from crushme_app.models import (
    Contact,
    FavoriteProduct,
    Order,
    Review,
    UserAddress,
    WishList,
)

pytestmark = pytest.mark.django_db


def _client(user=None):
    client = APIClient()
    if user:
        client.force_authenticate(user=user)
    return client


def _order(user, **overrides):
    data = {
        "user": user,
        "email": user.email,
        "name": "Test Buyer",
        "total": Decimal("120000.00"),
        "address_line_1": "Test street 123",
        "city": "Medellin",
        "state": "Antioquia",
        "zipcode": "050001",
        "country": "CO",
        "phone": "+573001234567",
    }
    data.update(overrides)
    return Order.objects.create(**data)


def test_favorites_require_authentication():
    """Fails if anonymous callers can enumerate favorite products."""
    response = _client().get("/api/favorites/products/ids/")

    assert response.status_code == 401


def test_favorite_ids_are_isolated_by_user(user_factory):
    """Fails if one account receives another account's favorite IDs."""
    owner = user_factory()
    other = user_factory()
    FavoriteProduct.objects.create(user=owner, woocommerce_product_id=900001)
    FavoriteProduct.objects.create(user=other, woocommerce_product_id=900002)

    response = _client(owner).get("/api/favorites/products/ids/")

    assert response.status_code == 200
    assert response.data["product_ids"] == [900001]
    assert response.data["count"] == 1


def test_add_favorite_uses_local_catalog_without_woocommerce(
    user_factory,
    woocommerce_product_factory,
):
    """Fails if favoriting a synced product still depends on live WooCommerce."""
    user = user_factory()
    product = woocommerce_product_factory(wc_id=900001, name="Local product")
    product_data = {
        "id": product.wc_id,
        "name": product.name,
        "price": 100000.0,
        "images": [],
        "slug": product.slug,
        "stock_status": "instock",
    }

    with (
        patch(
            "crushme_app.views.favorite_product_views.get_product_full_data",
            return_value=product_data,
        ) as build_product_data,
        patch(
            "crushme_app.views.favorite_product_views.woocommerce_service.get_product_by_id"
        ) as fetch_remote_product,
    ):
        response = _client(user).post(
            "/api/favorites/products/add/",
            {"woocommerce_product_id": product.wc_id},
            format="json",
        )

    assert response.status_code == 201
    assert response.data["data"]["product_data"]["name"] == "Local product"
    favorite = FavoriteProduct.objects.get(user=user)
    assert favorite.product_data["id"] == product.wc_id
    assert favorite.product_data["name"] == "Local product"
    build_product_data.assert_called_once()
    fetch_remote_product.assert_not_called()


def test_clear_favorites_does_not_delete_another_users_rows(user_factory):
    """Fails if clearing favorites crosses the authenticated-user boundary."""
    owner = user_factory()
    other = user_factory()
    FavoriteProduct.objects.create(user=owner, woocommerce_product_id=900001)
    FavoriteProduct.objects.create(user=other, woocommerce_product_id=900002)

    response = _client(owner).delete("/api/favorites/products/clear/")

    assert response.status_code == 200
    assert FavoriteProduct.objects.filter(user=owner).count() == 0
    assert (
        FavoriteProduct.objects.filter(
            user=other, woocommerce_product_id=900002
        ).count()
        == 1
    )


def test_wishlist_detail_hides_another_users_list(user_factory):
    """Fails if a guessed wishlist ID exposes a private list to another user."""
    owner = user_factory()
    intruder = user_factory()
    wishlist = WishList.objects.create(user=owner, name="Private list")

    response = _client(intruder).get(f"/api/wishlists/{wishlist.id}/")

    assert response.status_code == 404
    assert response.data["error"] == "Wishlist not found"


def test_wishlist_create_returns_field_validation(user_factory):
    """Fails if invalid wishlist input becomes a server error or empty record."""
    response = _client(user_factory()).post(
        "/api/wishlists/create/", {"name": "x"}, format="json"
    )

    assert response.status_code == 400
    assert (
        response.data["details"]["name"][0]
        == "Wishlist name must be at least 2 characters long."
    )
    assert WishList.objects.count() == 0


def test_wishlist_duplicate_returns_specific_validation(user_factory):
    """Fails if a duplicate product rejection is reduced to a generic error."""
    user = user_factory()
    wishlist = WishList.objects.create(user=user, name="Private list")
    wishlist.add_woocommerce_product(900001)

    response = _client(user).post(
        f"/api/wishlists/{wishlist.id}/add-woocommerce-product/",
        {"woocommerce_product_id": 900001, "priority": "medium"},
        format="json",
    )

    assert response.status_code == 400
    assert response.data["error"] == "Product is already in this wishlist"


def test_review_update_rejects_non_owner(user_factory):
    """Fails if any authenticated user can edit another user's review."""
    owner = user_factory()
    intruder = user_factory()
    review = Review.objects.create(
        user=owner,
        woocommerce_product_id=900001,
        rating=5,
        comment="Original comment",
    )

    response = _client(intruder).patch(
        f"/api/reviews/{review.id}/update/",
        {"rating": 1},
        format="json",
    )

    review.refresh_from_db()
    assert response.status_code == 403
    assert review.rating == 5
    assert response.data["error"] == "No tienes permiso para editar esta reseña"


def test_anonymous_review_returns_field_errors():
    """Fails if anonymous review identity validation is hidden from the client."""
    response = _client().post(
        "/api/reviews/",
        {"woocommerce_product_id": 900001, "rating": 5, "comment": "Excellent"},
        format="json",
    )

    assert response.status_code == 400
    assert response.data["errors"]["anonymous_name"][0] == (
        "El nombre es requerido para usuarios anónimos"
    )


def test_order_detail_hides_another_users_order(user_factory):
    """Fails if a guessed order ID exposes private purchase and shipping data."""
    owner = user_factory()
    intruder = user_factory()
    order = _order(owner)

    response = _client(intruder).get(f"/api/orders/{order.id}/")

    assert response.status_code == 404
    assert response.data["error"] == "Order not found"


def test_order_cancel_rejects_delivered_state(user_factory):
    """Fails if a completed order can be cancelled through the user API."""
    user = user_factory()
    order = _order(user, status="delivered")

    response = _client(user).post(
        f"/api/orders/{order.id}/cancel/",
        {"reason": "Too late"},
        format="json",
    )

    order.refresh_from_db()
    assert response.status_code == 400
    assert order.status == "delivered"
    assert response.data["details"]["non_field_errors"][0] == (
        "Order with status 'delivered' cannot be cancelled."
    )


def test_contact_listing_requires_staff(user_factory):
    """Fails if a regular account can enumerate private contact messages."""
    response = _client(user_factory(is_staff=False)).get("/api/contact/all/")

    assert response.status_code == 403


def test_contact_detail_marks_message_read_for_staff(user_factory):
    """Fails if staff viewing a contact does not persist its read state."""
    staff = user_factory(is_staff=True)
    contact = Contact.objects.create(
        email="contact@example.test",
        nombre="Contact Person",
        asunto="Question about an order",
        texto="Please help with my order status.",
    )

    response = _client(staff).get(f"/api/contact/{contact.id}/")

    contact.refresh_from_db()
    assert response.status_code == 200
    assert contact.is_read is True
    assert response.data["contact"]["is_read"] is True


def test_gift_search_validates_limit_before_querying_users():
    """Fails if a malformed public search limit triggers a server error."""
    response = _client().get("/api/users/search/?q=recipient&limit=invalid")

    assert response.status_code == 400
    assert response.data["error"] == "Limit must be an integer"


def test_gift_search_returns_shipping_cost_for_default_address(user_factory):
    """Fails if gift recipient search loses destination-derived shipping cost."""
    recipient = user_factory(username="recipient_user")
    UserAddress.objects.create(
        user=recipient,
        address_line_1="Recipient street 123",
        city="Medellin",
        state="Antioquia",
        zip_code="050001",
        country="CO",
        is_default_shipping=True,
    )

    response = _client().get("/api/users/search/?q=recipient&limit=5")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["username"] == "recipient_user"
    assert response.data["results"][0]["shipping_cost"] == 10500
