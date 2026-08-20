import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from crushme_app.models import User, WooCommerceCategory, WooCommerceProduct


def test_seed_e2e_data_refuses_the_regular_test_environment(db):
    with pytest.raises(CommandError, match='requires DJANGO_ENV=e2e'):
        call_command('seed_e2e_data')


@override_settings(DJANGO_ENV='e2e', FAKE_DATA_ALLOWED=True)
def test_seed_e2e_data_is_idempotent(db):
    call_command('seed_e2e_data')
    call_command('seed_e2e_data')

    assert User.objects.filter(username='e2e_user').count() == 1
    assert WooCommerceCategory.objects.filter(wc_id=134).count() == 1
    assert WooCommerceProduct.objects.filter(wc_id=900001).count() == 1


@override_settings(DJANGO_ENV='production', FAKE_DATA_ALLOWED=True)
def test_seed_e2e_data_refuses_production_even_with_opt_in(db):
    with pytest.raises(CommandError, match='DJANGO_ENV is production'):
        call_command('seed_e2e_data')
