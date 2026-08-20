"""Behavior tests for cart API validation."""

import pytest
from rest_framework.test import APIClient

from crushme_app.models import Cart

pytestmark = pytest.mark.django_db


def test_checkout_validation_rejects_empty_authenticated_cart(user_factory):
    """Fails if checkout validation allows an authenticated user to start with an empty cart."""
    user = user_factory()
    Cart.objects.create(user=user)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post('/api/cart/validate/', {}, format='json')

    assert response.status_code == 400
    assert response.data['details']['non_field_errors'][0] == 'Cart is empty.'
