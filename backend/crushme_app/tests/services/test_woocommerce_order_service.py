"""Behavior tests for outbound WooCommerce order contracts."""

from decimal import Decimal
from types import SimpleNamespace

import pytest

from crushme_app.models import Order, OrderItem, UserAddress
from crushme_app.services import woocommerce_order_service as service_module
from crushme_app.services.woocommerce_order_service import (
    ColombianAddressParser,
    WooCommerceOrderService,
)

pytestmark = pytest.mark.django_db


def _order(user, **overrides):
    data = {
        "user": user,
        "email": user.email,
        "name": "Test Buyer",
        "total": Decimal("120000.00"),
        "address_line_1": "Carrera 80 #50-25 Apto 301",
        "address_line_2": "El Poblado",
        "city": "Medellin",
        "state": "Antioquia",
        "zipcode": "050001",
        "country": "CO",
        "phone": "+573001234567",
        "notes": "Ring the bell",
    }
    data.update(overrides)
    return Order.objects.create(**data)


def _add_item(order, variation_id=None):
    return OrderItem.objects.create(
        order=order,
        woocommerce_product_id=900001,
        woocommerce_variation_id=variation_id,
        quantity=2,
        unit_price=Decimal("60000.00"),
        product_name="Rose wand",
    )


def test_colombian_address_parser_extracts_street_and_unit():
    """Fails if WooCommerce receives an unstructured Colombian apartment address."""
    parsed = ColombianAddressParser.parse("Carrera 80 #50-25 Apto 301")

    assert parsed == {
        "type_address": "Carrera",
        "street_1": "80",
        "street_2": "50",
        "street_3": "25",
        "unit_number": "301",
        "type_property": "Apartamento",
    }


def test_order_payload_preserves_variation_and_shipping_cost(user_factory):
    """Fails if an outbound order drops its selected variation or shipping line."""
    order = _order(user_factory())
    _add_item(order, variation_id=301)

    payload = WooCommerceOrderService()._build_order_payload(order, shipping_cost=10500)

    assert payload["line_items"] == [
        {"product_id": 900001, "quantity": 2, "variation_id": 301}
    ]
    assert payload["shipping"]["state"] == "ANT"
    assert payload["shipping"]["address_1"] == "Carrera 80 #50-25 Apto 301"
    assert payload["shipping_lines"][0]["total"] == "10500"


def test_gift_payload_uses_receivers_default_address(user_factory):
    """Fails if a gift is shipped to the buyer instead of its selected recipient."""
    buyer = user_factory(username="buyer")
    recipient = user_factory(
        username="recipient", first_name="Gift", last_name="Receiver"
    )
    UserAddress.objects.create(
        user=recipient,
        address_line_1="Calle 10 #20-30",
        city="Bogota",
        state="Bogota",
        zip_code="110111",
        country="CO",
        guest_phone="+573009876543",
        is_default_shipping=True,
    )
    order = _order(buyer, is_gift=True, receiver_username=recipient.username)
    _add_item(order)

    payload = WooCommerceOrderService()._build_order_payload(order)

    assert payload["shipping"]["first_name"] == "Gift"
    assert payload["shipping"]["last_name"] == "Receiver"
    assert payload["shipping"]["address_1"] == "Calle 10 #20-30"
    assert payload["shipping"]["postcode"] == "110111"


def test_send_order_returns_remote_identity(monkeypatch, user_factory):
    """Fails if a successful WooCommerce response loses the remote order identity."""
    order = _order(user_factory())
    _add_item(order)
    response = SimpleNamespace(
        status_code=201,
        json=lambda: {"id": 81, "number": "WC-81"},
    )
    monkeypatch.setattr(
        service_module.requests, "post", lambda *_args, **_kwargs: response
    )

    result = WooCommerceOrderService().send_order(order)

    assert result["success"] is True
    assert result["woocommerce_order_id"] == 81
    assert result["woocommerce_order_number"] == "WC-81"
    assert result["data"] == {"id": 81, "number": "WC-81"}


def test_send_order_reports_rejected_status_without_response_body(
    monkeypatch, user_factory
):
    """Fails if an upstream rejection leaks provider response data to callers."""
    order = _order(user_factory())
    _add_item(order)
    response = SimpleNamespace(status_code=422)
    monkeypatch.setattr(
        service_module.requests, "post", lambda *_args, **_kwargs: response
    )

    result = WooCommerceOrderService().send_order(order)

    assert result == {
        "success": False,
        "error": "API returned status 422",
        "status_code": 422,
    }


def test_send_order_normalizes_network_failure(monkeypatch, user_factory):
    """Fails if a network exception escapes the checkout integration boundary."""
    order = _order(user_factory())
    _add_item(order)

    def fail_request(*_args, **_kwargs):
        raise TimeoutError("provider secret detail")

    monkeypatch.setattr(service_module.requests, "post", fail_request)

    result = WooCommerceOrderService().send_order(order)

    assert result == {
        "success": False,
        "error": "WooCommerce order request failed",
    }
