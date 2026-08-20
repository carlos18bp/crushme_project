"""Dependency-aware health probe for the production runtime."""

import os

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse


def _database_status() -> str:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:  # noqa: BLE001 - probes must convert failures into readiness.
        return "error"
    return "ok"


def _redis_status() -> str:
    try:
        # A read is enough to force the Redis backend to establish a connection.
        cache.get("health-check")
    except Exception:  # noqa: BLE001 - cache backends expose different errors.
        return "error"
    return "ok"


def health_check(request):
    """Report application and dependency readiness without leaking errors."""
    database = _database_status()
    redis = _redis_status()
    healthy = database == redis == "ok"
    payload = {
        "status": "ok" if healthy else "error",
        "app": "ok",
        "database": database,
        "redis": redis,
        "project": settings.PROJECT_NAME,
        "environment": getattr(
            settings,
            "DJANGO_ENV",
            os.getenv("DJANGO_ENV", "development"),
        ),
    }
    response = JsonResponse(payload, status=200 if healthy else 503)
    response["Cache-Control"] = "no-store"
    return response
