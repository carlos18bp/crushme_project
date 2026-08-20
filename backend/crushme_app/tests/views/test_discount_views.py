"""Discount validation endpoint behavior tests."""

from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from crushme_app.models import DiscountCode

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'request_code',
    [
        pytest.param('  SAVE15  ', id='surrounding_whitespace'),
        pytest.param('save15', id='lowercase'),
    ],
)
def test_validate_discount_code_returns_valid_result_for_normalized_input(request_code):
    """Fails if normalized input does not return the stored valid discount code."""
    stored_code = 'SAVE15'
    DiscountCode.objects.create(
        code=stored_code,
        discount_percentage=Decimal('15.00'),
    )
    request_data = {'code': request_code}
    client = APIClient()

    response = client.post(
        '/api/discounts/validate/',
        request_data,
        format='json',
        REMOTE_ADDR='198.51.100.34',
    )

    assert response.status_code == 200
    assert response.data['exists'] is True
    assert response.data['is_valid'] is True
    assert response.data['code'] == stored_code
