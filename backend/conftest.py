"""Root conftest for crushme_project.

Provides shared pytest fixtures used across all test modules.
"""

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Unauthenticated DRF API client."""
    return APIClient()


@pytest.fixture
def user(db):
    """Regular authenticated user."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass123',
    )


@pytest.fixture
def admin_user(db):
    """Staff user for admin-gated endpoints."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        is_staff=True,
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """API client authenticated as a regular user."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """API client authenticated as an admin user."""
    api_client.force_authenticate(user=admin_user)
    return api_client
