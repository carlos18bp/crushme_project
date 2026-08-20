"""Production-like settings with non-production integration defaults."""

import os
from urllib.parse import urlparse

os.environ['DJANGO_ENV'] = 'staging'

from decouple import config as _config
from django.core.exceptions import ImproperlyConfigured

from .settings import *  # noqa: F401, F403, E402

DJANGO_ENV = 'staging'
IS_PRODUCTION = False
IS_STAGING = True
IS_TEST = False

_STAGING_HOST = 'crushme.projectapp.co'
_STAGING_ORIGIN = f'https://{_STAGING_HOST}'
_STAGING_DATABASE = 'crushme_staging'


def _redis_database(url):
    """Return the Redis database number or fail on a malformed URL."""
    parsed = urlparse(url)
    try:
        return int(parsed.path.lstrip('/'))
    except (TypeError, ValueError) as exc:
        raise ImproperlyConfigured(f'Invalid staging Redis URL: {url!r}') from exc


database_name = str(DATABASES['default']['NAME']).strip().lower()
if database_name != _STAGING_DATABASE:
    raise ImproperlyConfigured(
        f'Staging database must be {_STAGING_DATABASE}, received {database_name!r}'
    )

if _STAGING_HOST not in ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        f'Staging ALLOWED_HOSTS must include {_STAGING_HOST}'
    )
if _STAGING_ORIGIN not in CORS_ALLOWED_ORIGINS:
    raise ImproperlyConfigured(
        f'Staging CORS_ALLOWED_ORIGINS must include {_STAGING_ORIGIN}'
    )
if _STAGING_ORIGIN not in CSRF_TRUSTED_ORIGINS:
    raise ImproperlyConfigured(
        f'Staging CSRF_TRUSTED_ORIGINS must include {_STAGING_ORIGIN}'
    )
if FRONTEND_URL != _STAGING_ORIGIN:
    raise ImproperlyConfigured(
        f'Staging FRONTEND_URL must be {_STAGING_ORIGIN}'
    )

redis_cache_url = _config('REDIS_CACHE_URL', default='')
redis_huey_url = _config('REDIS_URL', default='')
if _redis_database(redis_cache_url) != 10:
    raise ImproperlyConfigured('Staging cache must use Redis database 10')
if _redis_database(redis_huey_url) != 11:
    raise ImproperlyConfigured('Staging Huey must use Redis database 11')

PAYPAL_MODE = _config('PAYPAL_MODE', default='sandbox')
if PAYPAL_MODE.lower() != 'sandbox':
    raise ImproperlyConfigured('Staging PayPal mode must be sandbox')

WOMPI_BASE_URL = _config(
    'WOMPI_BASE_URL',
    default='https://sandbox.wompi.co/v1',
)
WOMPI_ENVIRONMENT = _config('WOMPI_ENVIRONMENT', default='sandbox')
if WOMPI_ENVIRONMENT.lower() != 'sandbox':
    raise ImproperlyConfigured('Staging Wompi environment must be sandbox')
if urlparse(WOMPI_BASE_URL).hostname != 'sandbox.wompi.co':
    raise ImproperlyConfigured('Staging Wompi URL must use sandbox.wompi.co')

if any((WOOCOMMERCE_API_URL, WOOCOMMERCE_CONSUMER_KEY, WOOCOMMERCE_CONSUMER_SECRET)):
    raise ImproperlyConfigured('WooCommerce must remain disabled in staging')

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
FAKE_DATA_ALLOWED = True
BACKUPS_ENABLED = False
ENABLE_SLOW_QUERIES_REPORT = False
