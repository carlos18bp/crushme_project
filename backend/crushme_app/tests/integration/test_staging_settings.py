"""Staging settings isolation tests."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[3]

SAFE_STAGING_ENV = {
    'DJANGO_ENV': 'staging',
    'DJANGO_SECRET_KEY': 'test-' * 12,  # pragma: allowlist secret
    'DJANGO_DEBUG': 'False',
    'DJANGO_ALLOWED_HOSTS': 'crushme.projectapp.co',
    'DB_NAME': 'crushme_staging',
    'DB_USER': 'crushme_staging_user',
    'DB_PASSWORD': 'test-' * 4,  # pragma: allowlist secret
    'DB_HOST': 'localhost',
    'DB_PORT': '3306',
    'REDIS_CACHE_URL': 'redis://localhost:6379/10',
    'REDIS_URL': 'redis://localhost:6379/11',
    'CORS_ALLOWED_ORIGINS': 'https://crushme.projectapp.co',
    'CSRF_TRUSTED_ORIGINS': 'https://crushme.projectapp.co',
    'FRONTEND_URL': 'https://crushme.projectapp.co',
    'PAYPAL_MODE': 'sandbox',
    'WOMPI_BASE_URL': 'https://sandbox.wompi.co/v1',
    'WOMPI_ENVIRONMENT': 'sandbox',
    'WOOCOMMERCE_API_URL': '',
    'WOOCOMMERCE_CONSUMER_KEY': '',
    'WOOCOMMERCE_CONSUMER_SECRET': '',
    'BACKUPS_ENABLED': 'False',
    'ENABLE_SLOW_QUERIES_REPORT': 'False',
}


def _load_staging_settings(**overrides):
    env = os.environ.copy()
    env.update(SAFE_STAGING_ENV)
    env.update(overrides)
    command = [
        sys.executable,
        '-c',
        (
            'from crushme_project import settings_staging as s; '
            'print(s.DATABASES["default"]["NAME"], s.PAYPAL_MODE, '
            's.WOMPI_ENVIRONMENT, s.BACKUPS_ENABLED, s.EMAIL_BACKEND)'
        ),
    ]
    return subprocess.run(
        command,
        cwd=BACKEND_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )


def test_staging_settings_load_isolated_baseline():
    """Fails if the approved staging contract cannot load."""
    result = _load_staging_settings()

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == (
        'crushme_staging sandbox sandbox False '
        'django.core.mail.backends.console.EmailBackend'
    )


@pytest.mark.parametrize(
    ('override', 'expected_error'),
    [
        pytest.param(
            {'DB_NAME': 'crushme'},
            'Staging database must be crushme_staging',
            id='production_database',
        ),
        pytest.param(
            {'PAYPAL_MODE': 'live'},
            'Staging PayPal mode must be sandbox',
            id='live_paypal',
        ),
        pytest.param(
            {'WOMPI_ENVIRONMENT': 'production'},
            'Staging Wompi environment must be sandbox',
            id='production_wompi_environment',
        ),
        pytest.param(
            {'WOMPI_BASE_URL': 'https://production.wompi.co/v1'},
            'Staging Wompi URL must use sandbox.wompi.co',
            id='production_wompi_url',
        ),
        pytest.param(
            {'WOOCOMMERCE_CONSUMER_KEY': 'configured'},
            'WooCommerce must remain disabled in staging',
            id='woocommerce_credentials',
        ),
        pytest.param(
            {'REDIS_CACHE_URL': 'redis://localhost:6379/1'},
            'Staging cache must use Redis database 10',
            id='production_cache',
        ),
        pytest.param(
            {'REDIS_URL': 'redis://localhost:6379/2'},
            'Staging Huey must use Redis database 11',
            id='production_huey',
        ),
    ],
)
def test_staging_settings_reject_unsafe_configuration(override, expected_error):
    """Fails if one unsafe deployment value reaches staging startup."""
    result = _load_staging_settings(**override)

    assert result.returncode != 0
    assert expected_error in result.stderr
