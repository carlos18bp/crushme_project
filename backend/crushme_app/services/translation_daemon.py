"""Single-process Unix daemon for resource-bounded offline translation."""

from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import socketserver
import sys
from pathlib import Path
from typing import Any

from .translation_client import MAX_MESSAGE_BYTES, PROTOCOL_VERSION
from .translation_engine import CpuTranslationEngine
from .translation_manifest import ENGINE_ID

logger = logging.getLogger(__name__)


class TranslationRequestHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        self.connection.settimeout(5)
        try:
            raw_request = self.rfile.readline(MAX_MESSAGE_BYTES + 1)
        except TimeoutError:
            self._respond({"ok": False, "error": "request_timeout"})
            return
        if not raw_request.endswith(b"\n") or len(raw_request) > MAX_MESSAGE_BYTES:
            self._respond({"ok": False, "error": "request_too_large"})
            return

        try:
            request = json.loads(raw_request)
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._respond({"ok": False, "error": "invalid_json"})
            return
        if not isinstance(request, dict):
            self._respond({"ok": False, "error": "invalid_request"})
            return

        if request.get("version") != PROTOCOL_VERSION:
            self._respond({"ok": False, "error": "unsupported_version"})
            return
        if request.get("action") == "health":
            self._respond(
                {
                    "ok": True,
                    "engine": ENGINE_ID,
                    "active_pair": self.server.engine.active_pair,
                    "torch_loaded": "torch" in sys.modules,
                }
            )
            return
        if request.get("action") != "translate":
            self._respond({"ok": False, "error": "unsupported_action"})
            return

        text = request.get("text")
        source_language = request.get("source_language")
        target_language = request.get("target_language")
        if not isinstance(text, str) or not text.strip():
            self._respond({"ok": False, "error": "invalid_text"})
            return
        if (
            not isinstance(source_language, str)
            or not isinstance(target_language, str)
            or source_language not in {"es", "en"}
            or target_language not in {"es", "en"}
        ):
            self._respond({"ok": False, "error": "invalid_language"})
            return

        try:
            translated_text = self.server.engine.translate(
                text, source_language, target_language
            )
        except Exception as error:  # noqa: BLE001 - bounded daemon failure contract.
            logger.error(
                "Translation failed pair=%s-%s bytes=%d error_type=%s",
                source_language,
                target_language,
                len(text.encode("utf-8")),
                type(error).__name__,
            )
            self._respond({"ok": False, "error": "translation_failed"})
            return

        self._respond(
            {"ok": True, "translated_text": translated_text, "engine": ENGINE_ID}
        )

    def _respond(self, payload: dict[str, Any]) -> None:
        response = {"version": PROTOCOL_VERSION, **payload}
        self.wfile.write(
            json.dumps(response, ensure_ascii=True, separators=(",", ":")).encode()
            + b"\n"
        )


class TranslationServer(socketserver.UnixStreamServer):
    allow_reuse_address = True

    def __init__(self, socket_path: Path, engine: CpuTranslationEngine):
        self.engine = engine
        super().__init__(str(socket_path), TranslationRequestHandler)


def _prepare_socket(socket_path: Path) -> None:
    socket_path.parent.mkdir(parents=True, exist_ok=True, mode=0o750)
    if socket_path.exists():
        if not socket_path.is_socket():
            raise RuntimeError(f"Refusing to replace non-socket path: {socket_path}")
        socket_path.unlink()


def run_server(socket_path: Path, model_dir: Path) -> None:
    _prepare_socket(socket_path)
    engine = CpuTranslationEngine(model_dir)
    with TranslationServer(socket_path, engine) as server:
        os.chmod(socket_path, 0o660)  # nosec B103 - group-only local IPC.
        logger.info(
            "Translation daemon ready socket=%s engine=%s", socket_path, ENGINE_ID
        )

        def stop_server(signum, frame):  # noqa: ARG001 - signal callback contract.
            raise KeyboardInterrupt

        previous_sigterm = signal.signal(signal.SIGTERM, stop_server)
        try:
            server.serve_forever(poll_interval=0.5)
        except KeyboardInterrupt:
            logger.info("Translation daemon stopping")
        finally:
            signal.signal(signal.SIGTERM, previous_sigterm)
            if socket_path.exists() and socket_path.is_socket():
                socket_path.unlink()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--socket",
        type=Path,
        default=Path(
            os.getenv(
                "TRANSLATION_SOCKET_PATH",
                "/run/crushme-translation/translation.sock",
            )
        ),
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=Path(
            os.getenv(
                "TRANSLATION_MODEL_DIR",
                "~/.local/share/crushme/translation-models",
            )
        ).expanduser(),
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(
        level=os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    args = _parse_args()
    run_server(args.socket, args.model_dir)


if __name__ == "__main__":
    main()
