"""Behavior tests for the dependency-aware health endpoint."""

from unittest.mock import patch

import pytest
from django.test import override_settings
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_health_reports_runtime_dependencies(client):
    """A ready application must report every dependency as healthy."""
    response = client.get(reverse("health-check"))

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app": "ok",
        "database": "ok",
        "redis": "ok",
        "translation": "ok",
        "translation_engine": "argos",
        "project": "crushme_project",
        "environment": "test",
    }


def test_health_response_is_not_cacheable(client):
    """Health responses must not be cached by clients or intermediaries."""
    response = client.get(reverse("health-check"))

    assert response.headers["Cache-Control"] == "no-store"


def test_health_returns_503_when_database_is_unavailable(client):
    """A database failure must make the readiness probe fail closed."""
    with patch("crushme_project.health.connection.cursor", side_effect=OSError):
        response = client.get(reverse("health-check"))

    assert response.status_code == 503
    assert response.json()["database"] == "error"
    assert response.json()["status"] == "error"


def test_health_returns_503_when_redis_is_unavailable(client):
    """A Redis failure must make the readiness probe fail closed."""
    with patch("crushme_project.health.cache.get", side_effect=OSError):
        response = client.get(reverse("health-check"))

    assert response.status_code == 503
    assert response.json()["redis"] == "error"
    assert response.json()["status"] == "error"


@patch("crushme_project.health.TranslationClient.health", side_effect=OSError)
@override_settings(TRANSLATION_ENGINE="ctranslate2_cpu")
def test_health_returns_503_when_translation_daemon_is_unavailable(health, client):
    """A missing configured daemon must make readiness fail closed."""
    response = client.get(reverse("health-check"))

    assert response.status_code == 503
    assert response.json()["translation"] == "error"
    assert response.json()["status"] == "error"
