import pytest
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from crushme_app.fake_data_guard import ensure_fake_data_allowed


@pytest.mark.parametrize(
    'command_name',
    [
        'create_fake_data',
        'create_fake_users',
        'create_fake_products',
        'create_fake_carts',
        'create_fake_orders',
        'create_fake_wishlists',
        'delete_fake_data',
    ],
)
@override_settings(FAKE_DATA_ALLOWED=False)
def test_fake_data_commands_refuse_when_disabled(command_name):
    with pytest.raises(CommandError, match='FAKE_DATA_ALLOWED is disabled'):
        call_command(command_name)


@override_settings(DJANGO_ENV='production', FAKE_DATA_ALLOWED=True)
def test_guard_refuses_production_even_when_flag_is_enabled():
    with pytest.raises(CommandError, match='DJANGO_ENV is production'):
        ensure_fake_data_allowed('test-command')


@override_settings(FAKE_DATA_ALLOWED=True)
def test_guard_refuses_a_protected_database(monkeypatch):
    monkeypatch.setitem(settings.DATABASES['default'], 'NAME', 'crushme')

    with pytest.raises(CommandError, match='database crushme is protected'):
        ensure_fake_data_allowed('test-command')


@override_settings(
    DJANGO_ENV='test',
    FAKE_DATA_ALLOWED=True,
    FAKE_DATA_PROTECTED_DATABASES=('crushme',),
)
def test_guard_allows_an_isolated_test_database(monkeypatch):
    monkeypatch.setitem(settings.DATABASES['default'], 'NAME', ':memory:')

    assert ensure_fake_data_allowed('test-command') is None
