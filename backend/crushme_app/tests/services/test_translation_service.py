"""Behavior tests for translation engine loading."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from crushme_app.services.translation_service import TranslationService


def test_importing_service_does_not_load_argos():
    """Importing the service must leave the heavyweight engine unloaded."""
    command = (
        "import sys; "
        "import crushme_app.services.translation_service; "
        "raise SystemExit('argostranslate.translate' in sys.modules)"
    )

    result = subprocess.run(
        [sys.executable, "-c", command],
        cwd=Path(__file__).parents[3],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


@patch("crushme_app.services.translation_service._translate_with_argos")
def test_same_language_does_not_load_translation_engine(translate_with_argos):
    """Same-language content must bypass the translation engine."""
    translator = TranslationService(target_language="es")

    result = translator.translate_if_needed("Un regalo", content_language="es")

    assert result == "Un regalo"
    translate_with_argos.assert_not_called()


@patch(
    "crushme_app.services.translation_service._translate_with_argos",
    return_value="A gift",
)
def test_different_language_uses_translation_engine(translate_with_argos):
    """Different-language content must retain offline translation behavior."""
    translator = TranslationService(target_language="en")

    result = translator.translate_if_needed("Un regalo", content_language="es")

    assert result == "A gift"
    translate_with_argos.assert_called_once_with("Un regalo", "es", "en")
