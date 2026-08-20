"""Production-like settings with non-production integration defaults."""

import os

os.environ['DJANGO_ENV'] = 'staging'

from decouple import config as _config

from .settings import *  # noqa: F401, F403, E402

DJANGO_ENV = 'staging'
IS_PRODUCTION = False
IS_STAGING = True
IS_TEST = False

FAKE_DATA_ALLOWED = _config('FAKE_DATA_ALLOWED', default=True, cast=bool)
BACKUPS_ENABLED = _config('BACKUPS_ENABLED', default=False, cast=bool)
ENABLE_SLOW_QUERIES_REPORT = _config(
    'ENABLE_SLOW_QUERIES_REPORT',
    default=False,
    cast=bool,
)

PAYPAL_MODE = _config('PAYPAL_MODE', default='sandbox')
WOMPI_BASE_URL = _config(
    'WOMPI_BASE_URL',
    default='https://sandbox.wompi.co/v1',
)
WOMPI_ENVIRONMENT = _config('WOMPI_ENVIRONMENT', default='sandbox')

