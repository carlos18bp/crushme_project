"""Runtime safety tests for offline translation configuration."""

from types import SimpleNamespace

from argostranslate import settings as argos_settings
from argostranslate.sbd import MiniSBDSentencizer
from argostranslate.translate import PackageTranslation
from django.conf import settings


def test_argos_uses_minisbd_sentencizer_without_stanza_model_loader(tmp_path):
    """Argos never selects the vulnerable Stanza model loader."""
    package = SimpleNamespace(
        from_code='en',
        package_path=tmp_path,
        packaged_sbd_path=tmp_path / 'stanza',
    )

    translation = PackageTranslation(object(), object(), package)

    assert settings.ARGOS_CHUNK_TYPE == 'MINISBD'
    assert argos_settings.chunk_type is argos_settings.ChunkType.MINISBD
    assert isinstance(translation.sentencizer, MiniSBDSentencizer)
