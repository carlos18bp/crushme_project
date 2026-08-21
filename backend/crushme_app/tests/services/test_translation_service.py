"""Behavior tests for translation engine loading."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from django.test import override_settings

from crushme_app.services.translation_service import TranslationService


def test_importing_service_leaves_heavy_engines_unloaded():
    """Importing the service must leave the heavyweight engine unloaded."""
    command = (
        "import sys; "
        "import crushme_app.services.translation_service; "
        "blocked={'argostranslate.translate','ctranslate2','torch','spacy','stanza'}; "
        "raise SystemExit(bool(blocked.intersection(sys.modules)))"
    )

    result = subprocess.run(
        [sys.executable, "-c", command],
        cwd=Path(__file__).parents[3],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


@patch("crushme_app.services.translation_service._translate_offline")
def test_same_language_bypasses_translation_engine(translate_offline):
    """Same-language content must bypass the translation engine."""
    translator = TranslationService(target_language="es")

    result = translator.translate_if_needed("Un regalo", content_language="es")

    assert result == "Un regalo"
    translate_offline.assert_not_called()


@patch("crushme_app.services.translation_service._translate_offline")
@override_settings(TRANSLATION_RUNTIME_ENABLED=False)
def test_disabled_runtime_returns_original_text(translate_offline):
    """Hermetic environments must not load an offline inference engine."""
    translator = TranslationService(target_language="en")

    result = translator.translate_if_needed("Un regalo", content_language="es")

    assert result == "Un regalo"
    translate_offline.assert_not_called()


@patch(
    "crushme_app.services.translation_service._translate_with_cpu_service",
    return_value="A gift",
)
@override_settings(TRANSLATION_ENGINE="ctranslate2_cpu")
def test_different_language_uses_cpu_service(translate_with_cpu_service):
    """Different-language content must use the isolated CPU service."""
    translator = TranslationService(target_language="en")

    result = translator.translate_if_needed("Un regalo", content_language="es")

    assert result == "A gift"
    translate_with_cpu_service.assert_called_once_with("Un regalo", "es", "en")


@patch(
    "crushme_app.services.translation_service._translate_with_argos",
    return_value="A gift",
)
@override_settings(TRANSLATION_ENGINE="argos")
def test_argos_setting_uses_rollback_engine(translate_with_argos):
    """The temporary Argos setting remains an explicit rollback path."""
    translator = TranslationService(target_language="en")

    result = translator.translate_if_needed("Un regalo", content_language="es")

    assert result == "A gift"
    translate_with_argos.assert_called_once_with("Un regalo", "es", "en")


@patch(
    "crushme_app.services.translation_service._translate_with_cpu_service",
    side_effect=RuntimeError("socket unavailable"),
)
@override_settings(TRANSLATION_ENGINE="ctranslate2_cpu")
def test_cpu_service_failure_returns_original_text(translate_with_cpu_service):
    """A daemon failure preserves the existing fail-open behavior."""
    translator = TranslationService(target_language="en")

    result = translator.translate_if_needed("Un regalo", content_language="es")

    assert result == "Un regalo"
