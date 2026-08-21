"""Behavior tests for the local WooCommerce synchronization boundary."""

from decimal import Decimal

import pytest

from crushme_app.models import (
    ProductSyncLog,
    WooCommerceCategory,
)
from crushme_app.services.woocommerce_sync_service import WooCommerceSyncService

pytestmark = pytest.mark.django_db


def _product_payload(product_id=900001):
    return {
        "id": product_id,
        "name": "Synced product",
        "slug": f"synced-{product_id}",
        "permalink": f"https://example.test/products/{product_id}",
        "type": "variable",
        "price": "120000.00",
        "regular_price": "130000.00",
        "stock_status": "instock",
        "stock_quantity": 4,
        "status": "publish",
        "categories": [{"id": 134}],
        "images": [{"id": 71, "src": "https://example.test/image.jpg", "position": 0}],
    }


def test_sync_category_persists_remote_identity():
    """Fails if category synchronization loses the WooCommerce hierarchy identity."""
    service = WooCommerceSyncService()

    category = service._sync_category(
        {
            "id": 134,
            "name": "Toys",
            "slug": "toys",
            "parent": 40,
            "count": 7,
        }
    )

    assert category.wc_id == 134
    assert category.wc_parent_id == 40
    assert category.product_count == 7
    assert category.name == "Toys"


def test_sync_product_replaces_categories_and_images():
    """Fails if a product refresh retains stale category or image relationships."""
    old_category = WooCommerceCategory.objects.create(wc_id=40, name="Old", slug="old")
    new_category = WooCommerceCategory.objects.create(wc_id=134, name="New", slug="new")
    service = WooCommerceSyncService()
    product = service._sync_product(
        {**_product_payload(), "categories": [{"id": old_category.wc_id}]}
    )

    updated = service._sync_product(
        {**_product_payload(), "categories": [{"id": new_category.wc_id}]}
    )

    assert updated.id == product.id
    assert updated.get_categories_list() == ["New"]
    assert updated.images.count() == 1
    assert updated.primary_image.src == "https://example.test/image.jpg"


def test_sync_variation_normalizes_attribute_pairs(woocommerce_product_factory):
    """Fails if remote variation attributes cannot be selected."""
    product = woocommerce_product_factory(product_type="variable")
    service = WooCommerceSyncService()

    variation = service._sync_variation(
        product,
        {
            "id": 301,
            "permalink": "https://example.test/variation/301",
            "price": "125000.00",
            "regular_price": "125000.00",
            "stock_status": "instock",
            "status": "publish",
            "attributes": [
                {"name": "Color", "option": "Rose"},
                {"name": "Size", "option": "M"},
            ],
        },
    )
    variation.refresh_from_db()

    assert variation.wc_product_id == product.wc_id
    assert variation.attributes == {"Color": "Rose", "Size": "M"}
    assert variation.price == Decimal("125000.00")


def test_full_sync_records_success_counts(monkeypatch):
    """Fails if a completed synchronization is persisted as running or loses counts."""
    service = WooCommerceSyncService()
    monkeypatch.setattr(service, "sync_categories", lambda: 2)
    monkeypatch.setattr(service, "sync_products", lambda: 3)
    monkeypatch.setattr(service, "sync_variations", lambda: 4)

    result = service.sync_all()

    log = ProductSyncLog.objects.get(id=result["log_id"])
    assert result == {
        "success": True,
        "categories": 2,
        "products": 3,
        "variations": 4,
        "log_id": log.id,
    }
    assert log.status == "success"
    assert log.completed_at is not None


def test_full_sync_records_failure_without_raising(monkeypatch):
    """Fails if one upstream sync error leaves no failed operational record."""
    service = WooCommerceSyncService()

    def fail_categories():
        raise RuntimeError("Woo catalog unavailable")

    monkeypatch.setattr(service, "sync_categories", fail_categories)

    result = service.sync_all()

    log = ProductSyncLog.objects.get(id=result["log_id"])
    assert result["success"] is False
    assert result["error"] == "Woo catalog unavailable"
    assert log.status == "failed"
    assert log.errors_count == 1
    assert log.error_details == "Woo catalog unavailable"


def test_stock_sync_updates_only_requested_products(woocommerce_product_factory):
    """Fails if a bounded stock refresh mutates unrelated catalog rows."""
    target = woocommerce_product_factory(
        wc_id=900001, price=Decimal("100.00"), stock_quantity=1
    )
    other = woocommerce_product_factory(
        wc_id=900002, price=Decimal("200.00"), stock_quantity=2
    )
    service = WooCommerceSyncService()
    service.wc_service = type(
        "Client",
        (),
        {
            "get_product_by_id": staticmethod(
                lambda _product_id: {
                    "success": True,
                    "data": {
                        "price": "150.00",
                        "regular_price": "160.00",
                        "sale_price": None,
                        "on_sale": False,
                        "stock_status": "outofstock",
                        "stock_quantity": 0,
                        "manage_stock": True,
                    },
                }
            ),
        },
    )()

    updated = service.sync_stock_and_prices([target.wc_id])

    target.refresh_from_db()
    other.refresh_from_db()
    assert updated == 1
    assert target.price == Decimal("150.00")
    assert target.stock_status == "outofstock"
    assert other.price == Decimal("200.00")
    assert other.stock_quantity == 2
