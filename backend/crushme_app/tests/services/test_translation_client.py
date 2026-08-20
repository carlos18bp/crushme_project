"""Contract tests for the local translation socket protocol."""

import json
import socket
import threading
from pathlib import Path

import pytest

from crushme_app.services.translation_client import (
    MAX_MESSAGE_BYTES,
    TranslationClient,
    TranslationClientError,
)
from crushme_app.services.translation_daemon import TranslationServer


class FakeTranslationEngine:
    """Deterministic engine used at the socket boundary."""

    active_pair = None

    def translate(self, text, source_language, target_language):
        """Return a visible protocol result without loading model code."""
        return f"translated:{source_language}:{target_language}:{text}"


@pytest.fixture
def translation_server(tmp_path):
    """Serve the real Unix protocol with a deterministic engine."""
    socket_path = tmp_path / "translation.sock"
    server = TranslationServer(socket_path, FakeTranslationEngine())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield socket_path
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_client_returns_daemon_translation(translation_server):
    """The client returns text received through the Unix protocol."""
    client = TranslationClient(translation_server, timeout_seconds=1)

    result = client.translate("Un regalo", "es", "en")

    assert result == "translated:es:en:Un regalo"


def test_health_reports_engine_identity(translation_server):
    """The health contract identifies the active runtime engine."""
    client = TranslationClient(translation_server, timeout_seconds=1)

    result = client.health()

    assert result["engine"] == "ctranslate2-cpu-int8"


def test_unavailable_socket_raises_bounded_error(tmp_path):
    """An absent daemon produces a bounded client error."""
    client = TranslationClient(Path(tmp_path / "missing.sock"), timeout_seconds=0.1)

    with pytest.raises(TranslationClientError, match="unavailable"):
        client.translate("Un regalo", "es", "en")


def test_daemon_rejects_unsupported_language(translation_server):
    """The daemon rejects languages outside the ES/EN contract."""
    client = TranslationClient(translation_server, timeout_seconds=1)

    with pytest.raises(TranslationClientError, match="invalid_language"):
        client.translate("Un cadeau", "fr", "en")


def test_client_rejects_oversized_request(translation_server):
    """The client rejects input that exceeds the bounded socket contract."""
    client = TranslationClient(translation_server, timeout_seconds=1)

    with pytest.raises(TranslationClientError, match="too large"):
        client.translate("x" * MAX_MESSAGE_BYTES, "es", "en")


def test_daemon_rejects_non_object_request(translation_server):
    """Valid JSON outside the request-object contract is rejected safely."""
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.connect(str(translation_server))
        connection.sendall(b"[]\n")
        with connection.makefile("r") as response_stream:
            response = json.loads(response_stream.readline())

    assert response["error"] == "invalid_request"
