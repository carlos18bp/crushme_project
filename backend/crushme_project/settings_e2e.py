"""File-backed, hermetic settings used only by the Playwright harness."""

import os
import tempfile
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from .settings_test import *  # noqa: F401, F403

DJANGO_ENV = 'e2e'
IS_PRODUCTION = False
IS_TEST = True

_default_db = Path(tempfile.gettempdir()) / 'crushme-e2e.sqlite3'
E2E_DATABASE_PATH = Path(os.environ.get('E2E_DB_PATH', _default_db)).resolve()
if 'e2e' not in E2E_DATABASE_PATH.name.lower():
    raise ImproperlyConfigured('E2E_DB_PATH filename must contain "e2e"')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': E2E_DATABASE_PATH,
        'OPTIONS': {'timeout': 20},
    },
}

MEDIA_ROOT = Path(tempfile.gettempdir()) / 'crushme-e2e-media'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']
CORS_ALLOWED_ORIGINS = ['http://127.0.0.1:5174', 'http://localhost:5174']
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
FRONTEND_URL = 'http://127.0.0.1:5174'
FAKE_DATA_ALLOWED = True
TRANSLATION_RUNTIME_ENABLED = False

# E2E never contacts live gateways, WooCommerce, SMTP, Redis, or translation APIs.
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
WOOCOMMERCE_CONSUMER_KEY = ''
WOOCOMMERCE_CONSUMER_SECRET = ''
WOOCOMMERCE_API_URL = ''
PAYPAL_CLIENT_ID = ''
PAYPAL_CLIENT_SECRET = ''
PAYPAL_MODE = 'sandbox'
WOMPI_PUBLIC_KEY = ''
WOMPI_PRIVATE_KEY = ''
WOMPI_EVENTS_SECRET = ''
WOMPI_INTEGRITY_KEY = ''
WOMPI_BASE_URL = 'https://sandbox.wompi.co/v1'
WOMPI_ENVIRONMENT = 'sandbox'
