"""Behavior tests for the public local-catalog API."""

from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from crushme_app.models import WooCommerceProductVariation

pytestmark = pytest.mark.django_db


def _get(path):
    return APIClient().get(path, HTTP_ACCEPT_LANGUAGE="es", HTTP_X_CURRENCY="COP")


def test_catalog_returns_only_published_products(woocommerce_product_factory):
    """Fails if unpublished mirrored products become visible in the public catalog."""
    published = woocommerce_product_factory(
        wc_id=900001, name="Visible", status="publish"
    )
    woocommerce_product_factory(wc_id=900002, name="Hidden", status="draft")

    response = _get("/api/products/woocommerce/products/?lang=es&per_page=10&page=1")

    assert response.status_code == 200
    assert response.data["pagination"]["total_products"] == 1
    assert [item["id"] for item in response.data["data"]] == [published.wc_id]
    assert response.data["source"] == "local_db"


def test_catalog_rejects_non_numeric_pagination():
    """Fails if malformed pagination produces a server error."""
    response = _get("/api/products/woocommerce/products/?page=invalid")

    assert response.status_code == 400
    assert response.data["error"] == "Parámetros inválidos"


def test_catalog_search_requires_query():
    """Fails if an empty search silently executes an unbounded catalog query."""
    response = _get("/api/products/woocommerce/products/search/?q=")

    assert response.status_code == 400
    assert response.data["error"] == "Query de búsqueda requerido"


def test_catalog_search_matches_original_spanish_name(woocommerce_product_factory):
    """Fails if local Spanish product names are not searchable without translations."""
    product = woocommerce_product_factory(wc_id=900001, name="Vela de masaje")

    response = _get("/api/products/woocommerce/products/search/?q=vela&lang=es")

    assert response.status_code == 200
    assert response.data["pagination"]["total_results"] == 1
    assert response.data["data"][0]["id"] == product.wc_id
    assert response.data["search"]["query"] == "vela"


def test_simple_product_stock_can_use_cached_data(woocommerce_product_factory):
    """Fails if callers cannot avoid the real-time WooCommerce stock dependency."""
    product = woocommerce_product_factory(
        wc_id=900001,
        stock_status="instock",
        stock_quantity=7,
        manage_stock=True,
    )

    response = _get(
        f"/api/products/woocommerce/products/{product.wc_id}/stock/?real_time=false"
    )

    assert response.status_code == 200
    assert response.data["source"] == "local_db"
    assert response.data["stock"]["quantity"] == 7
    assert response.data["stock"]["available"] is True


def test_variable_product_stock_requires_variation_selection(
    woocommerce_product_factory,
):
    """Fails if a variable product is incorrectly reported as directly purchasable."""
    product = woocommerce_product_factory(wc_id=900001, product_type="variable")
    WooCommerceProductVariation.objects.create(
        wc_id=301,
        wc_product_id=product.wc_id,
        product=product,
        permalink="https://example.test/variation/301",
        price=Decimal("125000.00"),
        status="publish",
    )

    response = _get(f"/api/products/woocommerce/products/{product.wc_id}/stock/")

    assert response.status_code == 200
    assert response.data["variations_count"] == 1
    assert response.data["stock"]["requires_variation_selection"] is True
    assert response.data["stock"]["available"] is True


def test_variations_endpoint_excludes_unpublished_rows(woocommerce_product_factory):
    """Fails if a disabled variation remains selectable in product detail."""
    product = woocommerce_product_factory(wc_id=900001, product_type="variable")
    for variation_id, status in ((301, "publish"), (302, "private")):
        WooCommerceProductVariation.objects.create(
            wc_id=variation_id,
            wc_product_id=product.wc_id,
            product=product,
            permalink=f"https://example.test/variation/{variation_id}",
            price=Decimal("125000.00"),
            status=status,
        )

    response = _get(
        f"/api/products/woocommerce/products/{product.wc_id}/variations/?page=1&per_page=10"
    )

    assert response.status_code == 200
    assert response.data["pagination"]["total_variations"] == 1
    assert [variation["id"] for variation in response.data["data"]] == [301]
