"""Tests for WooCommerce integration boundaries."""

from unittest.mock import patch

from django.test import override_settings

from crushme_app.services.woocommerce_service import WooCommerceService


@override_settings(
    WOOCOMMERCE_API_URL='',
    WOOCOMMERCE_CONSUMER_KEY='',
    WOOCOMMERCE_CONSUMER_SECRET='',
)
def test_unconfigured_client_avoids_remote_request():
    """Fails if a disabled WooCommerce integration still attempts HTTP."""
    service = WooCommerceService()

    with patch('crushme_app.services.woocommerce_service.requests.get') as request_get:
        result = service.get_product_by_id(900_001)

    assert result == {
        'success': False,
        'error': 'WooCommerce integration is not configured',
        'status_code': None,
    }
    request_get.assert_not_called()
