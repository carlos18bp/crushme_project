"""MySQL compatibility settings for CI migration checks.

This module deliberately inherits the hermetic test configuration and only
replaces the database backend. It must never be pointed at a production-like
database.
"""

import os

from django.core.exceptions import ImproperlyConfigured

from .settings_test import *  # noqa: F401, F403


def _required_environment(name):
    value = os.environ.get(name, '').strip()
    if not value:
        raise ImproperlyConfigured(f'{name} is required for MySQL CI checks')
    return value


database_name = os.environ.get('CI_MYSQL_DATABASE', 'crushme_ci').strip()
database_host = os.environ.get('CI_MYSQL_HOST', '127.0.0.1').strip().lower()
allowed_hosts = {'127.0.0.1', 'localhost', 'mysql'}

if not any(marker in database_name.lower() for marker in ('ci', 'test')):
    raise ImproperlyConfigured(
        'CI_MYSQL_DATABASE must contain "ci" or "test"'
    )
if database_host not in allowed_hosts:
    raise ImproperlyConfigured(
        f'CI MySQL host must be local or ephemeral, received {database_host!r}'
    )

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': database_name,
        'USER': os.environ.get('CI_MYSQL_USER', 'root'),
        'PASSWORD': _required_environment('CI_MYSQL_PASSWORD'),
        'HOST': database_host,
        'PORT': os.environ.get('CI_MYSQL_PORT', '3306'),
        'CONN_MAX_AGE': 0,
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'TEST': {
            'NAME': f'test_{database_name}',
        },
    },
}

FAKE_DATA_ALLOWED = False
