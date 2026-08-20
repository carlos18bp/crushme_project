"""Unix-socket client for the local CPU-only translation daemon."""

from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Any

PROTOCOL_VERSION = 1
MAX_MESSAGE_BYTES = 64 * 1024


class TranslationClientError(RuntimeError):
    """Raised when the local translation service cannot satisfy a request."""


class TranslationClient:
    def __init__(self, socket_path: Path, timeout_seconds: float):
        self.socket_path = socket_path
        self.timeout_seconds = timeout_seconds

    def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        encoded = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode()
        if len(encoded) + 1 > MAX_MESSAGE_BYTES:
            raise TranslationClientError("Translation request is too large")

        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
                connection.settimeout(self.timeout_seconds)
                connection.connect(str(self.socket_path))
                connection.sendall(encoded + b"\n")
                response = self._read_response(connection)
        except (OSError, TimeoutError) as error:
            raise TranslationClientError(
                "Translation service is unavailable"
            ) from error

        if response.get("version") != PROTOCOL_VERSION or not response.get("ok"):
            raise TranslationClientError(
                f"Translation service rejected the request: {response.get('error', 'unknown')}"
            )
        return response

    @staticmethod
    def _read_response(connection: socket.socket) -> dict[str, Any]:
        chunks = bytearray()
        while len(chunks) <= MAX_MESSAGE_BYTES:
            chunk = connection.recv(min(4096, MAX_MESSAGE_BYTES + 1 - len(chunks)))
            if not chunk:
                break
            chunks.extend(chunk)
            if b"\n" in chunk:
                break
        if len(chunks) > MAX_MESSAGE_BYTES or b"\n" not in chunks:
            raise TranslationClientError("Invalid translation service response")
        try:
            response = json.loads(bytes(chunks).split(b"\n", 1)[0])
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise TranslationClientError(
                "Malformed translation service response"
            ) from error
        if not isinstance(response, dict):
            raise TranslationClientError("Malformed translation service response")
        return response

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        response = self._request(
            {
                "version": PROTOCOL_VERSION,
                "action": "translate",
                "text": text,
                "source_language": source_language,
                "target_language": target_language,
            }
        )
        translated_text = response.get("translated_text")
        if not isinstance(translated_text, str) or not translated_text:
            raise TranslationClientError("Translation service returned no text")
        return translated_text

    def health(self) -> dict[str, Any]:
        return self._request({"version": PROTOCOL_VERSION, "action": "health"})
