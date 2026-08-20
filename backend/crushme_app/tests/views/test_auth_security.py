from types import SimpleNamespace

import pytest
from argostranslate import settings as argos_settings
from argostranslate.sbd import MiniSBDSentencizer
from argostranslate.translate import PackageTranslation
from django.conf import settings
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from crushme_app.models import User
from crushme_app.throttles import LoginRateThrottle


pytestmark = pytest.mark.django_db


def test_token_refresh_rotation_revokes_previous_token():
    user = User.objects.create_user(
        username='refresh-user',
        email='refresh@example.com',
        password='unused',
    )
    old_refresh = str(RefreshToken.for_user(user))
    client = APIClient()

    first = client.post(
        '/api/auth/token/refresh/',
        {'refresh': old_refresh},
        format='json',
    )
    replay = client.post(
        '/api/auth/token/refresh/',
        {'refresh': old_refresh},
        format='json',
    )

    assert first.status_code == 200
    assert first.data['refresh'] != old_refresh
    assert replay.status_code == 401


def test_login_throttle_rejects_second_request(monkeypatch):
    cache.clear()
    monkeypatch.setattr(LoginRateThrottle, 'rate', '1/min', raising=False)
    client = APIClient()

    first = client.post(
        '/api/auth/login/',
        {'username': 'missing', 'password': 'invalid'},
        format='json',
        REMOTE_ADDR='198.51.100.10',
    )
    second = client.post(
        '/api/auth/login/',
        {'username': 'missing', 'password': 'invalid'},
        format='json',
        REMOTE_ADDR='198.51.100.10',
    )

    assert first.status_code == 400
    assert second.status_code == 429


def test_unverified_google_login_endpoint_is_absent():
    response = APIClient().post(
        '/api/auth/google_login/',
        {'email': 'victim@example.com'},
        format='json',
    )

    assert response.status_code == 404


def test_woocommerce_connection_requires_admin():
    response = APIClient().get('/api/products/woocommerce/test/')

    assert response.status_code == 401


def test_stanza_model_loader_is_disabled(tmp_path):
    package = SimpleNamespace(
        from_code='en',
        package_path=tmp_path,
        packaged_sbd_path=tmp_path / 'stanza',
    )

    translation = PackageTranslation(object(), object(), package)

    assert settings.ARGOS_CHUNK_TYPE == 'MINISBD'
    assert argos_settings.chunk_type is argos_settings.ChunkType.MINISBD
    assert isinstance(translation.sentencizer, MiniSBDSentencizer)
