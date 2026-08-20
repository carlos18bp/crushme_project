"""Authorization tests for product and WooCommerce endpoints."""

import pytest
from rest_framework.test import APIClient

from crushme_app.models import User

pytestmark = pytest.mark.django_db


def test_woocommerce_connection_rejects_authenticated_non_admin_user():
    """Fails if the WooCommerce connection endpoint accepts non-admin users."""
    user = User.objects.create_user(
        username='catalog-user',
        email='catalog-user@example.test',
        is_staff=False,
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get('/api/products/woocommerce/test/')

    assert response.status_code == 403
