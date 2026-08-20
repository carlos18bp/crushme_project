"""Integrity tests for pinned translation model files."""

import hashlib
from types import MappingProxyType

import pytest

from crushme_app.services.translation_manifest import (
    ModelSpec,
    TranslationModelError,
    validate_model,
)


def _model_spec(expected_hash):
    return ModelSpec(
        source_language="es",
        target_language="en",
        directory="es-en",
        source_model="test/model",
        source_revision="test-revision",
        files=MappingProxyType({"model.bin": expected_hash}),
    )


def test_valid_model_checksum_passes(tmp_path):
    """A model matching its pinned digest is accepted."""
    model_dir = tmp_path / "es-en"
    model_dir.mkdir()
    model_file = model_dir / "model.bin"
    model_file.write_bytes(b"verified model")
    expected_hash = hashlib.sha256(b"verified model").hexdigest()

    result = validate_model(tmp_path, _model_spec(expected_hash))

    assert result is None


def test_modified_model_checksum_is_rejected(tmp_path):
    """A changed model file is rejected before inference."""
    model_dir = tmp_path / "es-en"
    model_dir.mkdir()
    (model_dir / "model.bin").write_bytes(b"modified model")
    expected_hash = hashlib.sha256(b"verified model").hexdigest()

    with pytest.raises(TranslationModelError, match="Checksum mismatch"):
        validate_model(tmp_path, _model_spec(expected_hash))


def test_unexpected_model_file_is_rejected(tmp_path):
    """Unpinned files invalidate an otherwise matching model directory."""
    model_dir = tmp_path / "es-en"
    model_dir.mkdir()
    (model_dir / "model.bin").write_bytes(b"verified model")
    (model_dir / "unexpected.bin").write_bytes(b"unexpected")
    expected_hash = hashlib.sha256(b"verified model").hexdigest()

    with pytest.raises(TranslationModelError, match="Unexpected model files"):
        validate_model(tmp_path, _model_spec(expected_hash))
