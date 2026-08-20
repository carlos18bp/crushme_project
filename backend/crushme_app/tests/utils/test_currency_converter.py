"""Tests for deterministic currency conversion."""

from unittest.mock import patch

from django.test import override_settings

from crushme_app.utils.currency_converter import CurrencyConverter


@override_settings(CURRENCY_FIXED_COP_TO_USD_RATE=0.0002)
def test_fixed_exchange_rate_controls_usd_conversion():
    """Fails if hermetic environments stop using their configured rate."""
    converted_price = CurrencyConverter.convert_cop_to_usd(10_000)

    assert converted_price == 2.0


@override_settings(CURRENCY_FIXED_COP_TO_USD_RATE=0.0002)
def test_fixed_exchange_rate_avoids_remote_provider():
    """Fails if a configured rate still allows an outbound HTTP request."""
    with patch('crushme_app.utils.currency_converter.requests.get') as request_get:
        exchange_rate = CurrencyConverter.get_exchange_rate()

    assert exchange_rate == 0.0002
    request_get.assert_not_called()
