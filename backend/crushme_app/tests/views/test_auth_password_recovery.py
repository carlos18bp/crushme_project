"""Password recovery endpoint behavior tests."""

import pytest
from rest_framework.test import APIClient

from crushme_app.models import PasswordCode
from crushme_app.tests.factories import create_user
from crushme_app.views.auth_views import email_service

pytestmark = pytest.mark.django_db

INITIAL_PASSWORD = 'Initial-password-123!'  # pragma: allowlist secret
NEW_PASSWORD = 'Replacement-password-456!'  # pragma: allowlist secret


def test_forgot_password_retires_previous_unused_code(monkeypatch):
    """Fails if a replacement reset request leaves an older code usable."""
    user = create_user(
        email='forgot-password@example.test',
        username='forgot-password-user',
        password=INITIAL_PASSWORD,
    )
    prior_code = PasswordCode.objects.create(
        user=user,
        code='1111',
        code_type='password_reset',
    )
    request_data = {'email': user.email}
    client = APIClient()
    monkeypatch.setattr(
        email_service,
        'send_password_reset_code',
        lambda **_kwargs: True,
    )

    response = client.post(
        '/api/auth/forgot-password/',
        request_data,
        format='json',
        REMOTE_ADDR='198.51.100.31',
    )

    prior_code.refresh_from_db()
    unused_code_count = PasswordCode.objects.filter(
        user=user,
        code_type='password_reset',
        used=False,
    ).count()
    assert response.status_code == 200
    assert prior_code.used is True
    assert unused_code_count == 1


def test_reset_password_rejects_previously_used_code():
    """Fails if a consumed reset code can be replayed to change a password."""
    user = create_user(
        email='used-reset-code@example.test',
        username='used-reset-code-user',
        password=INITIAL_PASSWORD,
    )
    reset_code = PasswordCode.objects.create(
        user=user,
        code='2222',
        code_type='password_reset',
        used=True,
    )
    password_before_reset = user.password
    request_data = {
        'email': user.email,
        'reset_code': reset_code.code,
        'new_password': NEW_PASSWORD,
        'new_password_confirm': NEW_PASSWORD,
    }
    client = APIClient()

    response = client.post(
        '/api/auth/reset-password/',
        request_data,
        format='json',
        REMOTE_ADDR='198.51.100.32',
    )

    user.refresh_from_db()
    assert response.status_code == 400
    assert response.data['non_field_errors'][0] == 'Invalid or expired reset code.'
    assert user.password == password_before_reset


def test_reset_password_marks_valid_code_used():
    """Fails if a successful password reset leaves its code available for replay."""
    user = create_user(
        email='valid-reset-code@example.test',
        username='valid-reset-code-user',
        password=INITIAL_PASSWORD,
    )
    reset_code = PasswordCode.objects.create(
        user=user,
        code='3333',
        code_type='password_reset',
    )
    request_data = {
        'email': user.email,
        'reset_code': reset_code.code,
        'new_password': NEW_PASSWORD,
        'new_password_confirm': NEW_PASSWORD,
    }
    client = APIClient()

    response = client.post(
        '/api/auth/reset-password/',
        request_data,
        format='json',
        REMOTE_ADDR='198.51.100.33',
    )

    user.refresh_from_db()
    reset_code.refresh_from_db()
    assert response.status_code == 200
    assert response.data['message'] == (
        'Password reset successful. You can now login with your new password.'
    )
    assert user.check_password(NEW_PASSWORD) is True
    assert reset_code.used is True
