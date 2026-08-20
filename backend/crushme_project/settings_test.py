"""Hermetic settings for backend tests and the local E2E harness."""

import os
import tempfile
from pathlib import Path

os.environ['DJANGO_ENV'] = 'test'

from huey import MemoryHuey

from .settings import *  # noqa: F401, F403, E402

DJANGO_ENV = 'test'
IS_PRODUCTION = False
IS_TEST = True

SECRET_KEY = 'test-only-secret-key-with-at-least-32-bytes'
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'crushme-tests',
    },
}
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
HUEY = MemoryHuey(name='crushme-tests', immediate=True)

MEDIA_ROOT = Path(tempfile.gettempdir()) / 'crushme-test-media'
BACKUPS_ENABLED = False
ENABLE_SLOW_QUERIES_REPORT = False
ENABLE_SILK = False
FAKE_DATA_ALLOWED = True

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
