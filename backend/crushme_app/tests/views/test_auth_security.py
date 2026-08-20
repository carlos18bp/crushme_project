"""Security regression tests for public authentication boundaries."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from django.core.cache import cache
from django.db import close_old_connections, connection
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from crushme_app.models import PasswordCode, User
from crushme_app.throttles import LoginRateThrottle
from crushme_app.views.auth_views import email_service

pytestmark = pytest.mark.django_db
TEST_PASSWORD = 'Valid-password-123!'  # pragma: allowlist secret


def test_token_refresh_rotation_revokes_previous_token():
    """A rotated refresh token cannot be replayed."""
    user = User.objects.create_user(
        username='refresh-user',
        email='refresh@example.com',
        password='unused',
    )
    old_refresh = str(RefreshToken.for_user(user))
    client = APIClient()

    first = client.post(
        '/api/auth/token/refresh/',
        {'refresh': old_refresh},
        format='json',
    )
    replay = client.post(
        '/api/auth/token/refresh/',
        {'refresh': old_refresh},
        format='json',
    )

    assert first.status_code == 200
    assert first.data['refresh'] != old_refresh
    assert replay.status_code == 401


def test_logout_revokes_refresh_token():
    """Logging out revokes the submitted refresh token."""
    user = User.objects.create_user(
        username='logout-user',
        email='logout@example.com',
        password='unused',
    )
    refresh = str(RefreshToken.for_user(user))
    client = APIClient()

    logout_response = client.post(
        '/api/auth/logout/',
        {'refresh': refresh},
        format='json',
    )
    replay = client.post(
        '/api/auth/token/refresh/',
        {'refresh': refresh},
        format='json',
    )

    assert logout_response.status_code == 204
    assert replay.status_code == 401


@pytest.mark.django_db(transaction=True)
def test_concurrent_refresh_accepts_token_only_once():
    """MySQL row locking permits one winner for concurrent rotation."""
    if connection.vendor != 'mysql':
        pytest.skip('Row-lock behavior is verified against the production database engine')

    user = User.objects.create_user(
        username='concurrent-refresh-user',
        email='concurrent-refresh@example.com',
        password='unused',
    )
    refresh = str(RefreshToken.for_user(user))
    barrier = Barrier(2)

    def rotate_refresh(_index):
        close_old_connections()
        try:
            barrier.wait(timeout=5)
            response = APIClient().post(
                '/api/auth/token/refresh/',
                {'refresh': refresh},
                format='json',
            )
            return response.status_code
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = list(executor.map(rotate_refresh, range(2)))

    assert sorted(statuses) == [200, 401]


def test_login_throttle_rejects_second_request(monkeypatch):
    """Repeated login attempts from one identity are throttled."""
    cache.clear()
    monkeypatch.setattr(LoginRateThrottle, 'rate', '1/min', raising=False)
    client = APIClient()

    first = client.post(
        '/api/auth/login/',
        {'username': 'missing', 'password': 'invalid'},
        format='json',
        REMOTE_ADDR='198.51.100.10',
    )
    second = client.post(
        '/api/auth/login/',
        {'username': 'missing', 'password': 'invalid'},
        format='json',
        REMOTE_ADDR='198.51.100.10',
    )

    assert first.status_code == 400
    assert second.status_code == 429


def test_unverified_google_login_endpoint_is_absent():
    """The former unverified OAuth endpoint is not routable."""
    response = APIClient().post(
        '/api/auth/google_login/',
        {'email': 'victim@example.com'},
        format='json',
    )

    assert response.status_code == 404


def test_woocommerce_connection_requires_admin():
    """Anonymous callers cannot probe WooCommerce connectivity."""
    response = APIClient().get('/api/products/woocommerce/test/')

    assert response.status_code == 401


def test_signup_removes_account_when_verification_delivery_fails(monkeypatch):
    """Fails if a failed verification email leaves a newly registered account behind."""
    submitted_email = 'delivery-failure@example.test'
    client = APIClient()
    monkeypatch.setattr(
        email_service,
        'send_verification_code',
        lambda **_kwargs: False,
    )

    response = client.post(
        '/api/auth/signup/',
        {
            'email': submitted_email,
            'username': 'delivery-failure-user',
            'password': TEST_PASSWORD,
            'password_confirm': TEST_PASSWORD,
        },
        format='json',
        REMOTE_ADDR='198.51.100.21',
    )

    assert response.status_code == 500
    assert User.objects.filter(email=submitted_email).count() == 0


def test_verify_email_activates_pending_account():
    """Fails if a valid verification code returns tokens without activating the account."""
    user = User.objects.create_user(
        email='pending-verification@example.test',
        username='pending-verification-user',
        password=TEST_PASSWORD,
        email_verified=False,
        is_active=False,
    )
    verification_code = PasswordCode.objects.create(
        user=user,
        code='1234',
        code_type='email_verification',
    )
    client = APIClient()

    response = client.post(
        '/api/auth/verify-email/',
        {'email': user.email, 'verification_code': verification_code.code},
        format='json',
        REMOTE_ADDR='198.51.100.22',
    )

    user.refresh_from_db()
    verification_code.refresh_from_db()
    assert response.status_code == 200
    assert user.email_verified is True
    assert user.is_active is True
    assert verification_code.used is True


def test_signup_rejects_verified_email():
    """Fails if registration can overwrite an account whose email is verified."""
    verified_user = User.objects.create_user(
        email='verified-account@example.test',
        username='verified-account-user',
        password=TEST_PASSWORD,
        email_verified=True,
        is_active=True,
    )
    client = APIClient()

    response = client.post(
        '/api/auth/signup/',
        {
            'email': verified_user.email,
            'username': 'replacement-user',
            'password': TEST_PASSWORD,
            'password_confirm': TEST_PASSWORD,
        },
        format='json',
        REMOTE_ADDR='198.51.100.23',
    )

    assert response.status_code == 400
    assert response.data['error'] == (
        'A user with this email is already registered and verified. Please login.'
    )
