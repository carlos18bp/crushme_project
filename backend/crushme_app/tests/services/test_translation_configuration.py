"""Runtime safety tests for offline translation configuration."""

import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from argostranslate import settings as argos_settings
from argostranslate.sbd import MiniSBDSentencizer
from argostranslate.translate import PackageTranslation
from django.conf import settings


def _load_settings_with(**overrides):
    environment = os.environ.copy()
    environment.update(
        {
            "DJANGO_SETTINGS_MODULE": "crushme_project.settings_test",
            **overrides,
        }
    )
    return subprocess.run(
        [
            sys.executable,
            "-c",
            "from django.conf import settings; settings.INSTALLED_APPS",
        ],
        cwd=Path(__file__).parents[3],
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )


def test_argos_uses_minisbd_sentencizer_without_stanza_model_loader(tmp_path):
    """Argos never selects the vulnerable Stanza model loader."""
    package = SimpleNamespace(
        from_code="en",
        package_path=tmp_path,
        packaged_sbd_path=tmp_path / "stanza",
    )

    translation = PackageTranslation(object(), object(), package)

    assert settings.ARGOS_CHUNK_TYPE == "MINISBD"
    assert argos_settings.chunk_type is argos_settings.ChunkType.MINISBD
    assert isinstance(translation.sentencizer, MiniSBDSentencizer)


def test_settings_reject_unknown_translation_engine():
    """An unknown engine cannot bypass the explicit runtime allowlist."""
    result = _load_settings_with(TRANSLATION_ENGINE="cuda")

    assert result.returncode != 0
    assert "TRANSLATION_ENGINE must be argos or ctranslate2_cpu" in result.stderr


def test_settings_reject_non_cpu_argos_device():
    """The rollback engine cannot be configured to use a GPU."""
    result = _load_settings_with(ARGOS_DEVICE_TYPE="cuda")

    assert result.returncode != 0
    assert "ARGOS_DEVICE_TYPE must remain cpu" in result.stderr
