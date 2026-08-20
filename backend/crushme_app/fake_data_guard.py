"""Defense-in-depth guard for fake-data management commands."""

from pathlib import Path

from django.conf import settings
from django.core.management.base import CommandError

_BUILTIN_PROTECTED_DATABASES = {
    'crushme',
    'crushme_db',
    'crushme_production',
}


def _database_identifiers(database_name):
    value = str(database_name or '').strip().lower()
    if not value:
        return set()

    path = Path(value)
    return {value, path.name, path.stem}


def ensure_fake_data_allowed(command_name):
    """Reject seed/destructive commands outside an explicitly safe database."""
    environment = str(getattr(settings, 'DJANGO_ENV', '')).strip().lower()
    database_name = settings.DATABASES.get('default', {}).get('NAME', '')
    configured = getattr(settings, 'FAKE_DATA_PROTECTED_DATABASES', ())
    protected = _BUILTIN_PROTECTED_DATABASES | {
        str(name).strip().lower() for name in configured if str(name).strip()
    }

    reason = None
    if environment == 'production':
        reason = 'DJANGO_ENV is production'
    elif not getattr(settings, 'FAKE_DATA_ALLOWED', False):
        reason = 'FAKE_DATA_ALLOWED is disabled'
    elif _database_identifiers(database_name) & protected:
        reason = f'database {database_name!s} is protected'

    if reason:
        raise CommandError(
            f'Refusing to run {command_name}: {reason}. '
            'Use an isolated development or test database.'
        )
