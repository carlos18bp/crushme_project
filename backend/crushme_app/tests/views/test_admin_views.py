"""Behavior checks for administrative change views."""

from decimal import Decimal

import pytest
from django.urls import reverse

from crushme_app.models import Order, OrderItem, User


@pytest.mark.django_db
def test_order_change_view_renders_shipping_and_item_fields(client):
    """Catch stale OrderAdmin field names that make the change form crash."""
    admin = User.objects.create_superuser(
        username="admin-view",
        email="admin-view@example.test",
        password="Admin-password-123!",  # pragma: allowlist secret
    )
    order = Order.objects.create(
        user=admin,
        order_number="ADMIN-ORDER-1",
        total=Decimal("25.00"),
        status="processing",
        email="buyer@example.test",
        name="Admin Buyer",
        country="CO",
        state="Cundinamarca",
        city="Bogota",
        zipcode="110111",
        address_line_1="Admin street 123",
        phone="+573001234567",
    )
    OrderItem.objects.create(
        order=order,
        woocommerce_product_id=900001,
        product_name="Admin product",
        quantity=1,
        unit_price=Decimal("25.00"),
    )
    client.force_login(admin)

    response = client.get(
        reverse("admin:crushme_app_order_change", args=[order.pk]),
    )

    assert response.status_code == 200
    assert b"id_address_line_1" in response.content
    assert b"id_items-0-woocommerce_product_id" in response.content
