"""Pinned model metadata and integrity checks for offline translation."""

from __future__ import annotations

import hashlib
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

ENGINE_ID = "ctranslate2-cpu-int8"
MANIFEST_VERSION = 1


class TranslationModelError(RuntimeError):
    """Raised when a translation model bundle is absent or invalid."""


@dataclass(frozen=True)
class ModelSpec:
    source_language: str
    target_language: str
    directory: str
    source_model: str
    source_revision: str
    files: MappingProxyType[str, str]

    @property
    def pair(self) -> tuple[str, str]:
        return self.source_language, self.target_language


MODEL_SPECS = MappingProxyType(
    {
        ("es", "en"): ModelSpec(
            source_language="es",
            target_language="en",
            directory="es-en",
            source_model="Helsinki-NLP/opus-mt-es-en",
            source_revision="c96e2c5399ebfae4fc43d9669556b9afa74bb69d",  # pragma: allowlist secret
            files=MappingProxyType(
                {
                    "config.json": "8f6496adfc930cbfecbe8281112197705c488fab47d34b4829b06d7f478909af",  # pragma: allowlist secret
                    "model.bin": "44c5adc2c680f27c14c991e5ab7f74f38b41597153f7123bc8f6455f09a3b38b",  # pragma: allowlist secret
                    "shared_vocabulary.json": "040e48c9d00734f48506e052695837720bd1f6aa01c70636cde83038362baf19",  # pragma: allowlist secret
                    "source.spm": "e236ee6d866b635c0142114f8647f39831f9d92534aa2aad75c942f6a78ad0e3",  # pragma: allowlist secret
                    "target.spm": "4dd547c24816a335e7b0b2e63376a8f1b3cbfc671eda5ab808dd44fdadaa8791",  # pragma: allowlist secret
                }
            ),
        ),
        ("en", "es"): ModelSpec(
            source_language="en",
            target_language="es",
            directory="en-es",
            source_model="Helsinki-NLP/opus-mt-en-es",
            source_revision="5bc4493d463cf000c1f0b50f8d56886a392ed4ab",  # pragma: allowlist secret
            files=MappingProxyType(
                {
                    "config.json": "8f6496adfc930cbfecbe8281112197705c488fab47d34b4829b06d7f478909af",  # pragma: allowlist secret
                    "model.bin": "30c5c2de08329c61860777fbe471e2dd413f64adbde543b2848b5ac3b5d6f865",  # pragma: allowlist secret
                    "shared_vocabulary.json": "040e48c9d00734f48506e052695837720bd1f6aa01c70636cde83038362baf19",  # pragma: allowlist secret
                    "source.spm": "4dd547c24816a335e7b0b2e63376a8f1b3cbfc671eda5ab808dd44fdadaa8791",  # pragma: allowlist secret
                    "target.spm": "e236ee6d866b635c0142114f8647f39831f9d92534aa2aad75c942f6a78ad0e3",  # pragma: allowlist secret
                }
            ),
        ),
    }
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as model_file:
        for chunk in iter(lambda: model_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_model(root: Path, spec: ModelSpec) -> None:
    """Verify every runtime file for one pinned translation model."""
    model_dir = root / spec.directory
    if not model_dir.is_dir():
        raise TranslationModelError(f"Missing model directory: {model_dir}")

    expected_files = set(spec.files)
    actual_files = {path.name for path in model_dir.iterdir() if path.is_file()}
    if actual_files != expected_files:
        raise TranslationModelError(
            f"Unexpected model files for {spec.directory}: "
            f"expected={sorted(expected_files)} actual={sorted(actual_files)}"
        )

    for filename, expected_hash in spec.files.items():
        model_file = model_dir / filename
        if model_file.is_symlink() or not model_file.is_file():
            raise TranslationModelError(f"Invalid model file: {model_file}")
        actual_hash = _sha256(model_file)
        if actual_hash != expected_hash:
            raise TranslationModelError(
                f"Checksum mismatch for {model_file}: {actual_hash}"
            )


def validate_model_bundle(root: Path) -> None:
    """Verify the complete ES/EN model bundle."""
    root = root.expanduser().resolve()
    for spec in MODEL_SPECS.values():
        validate_model(root, spec)


def install_model_bundle(source: Path, destination: Path, *, force: bool) -> None:
    """Copy a verified bundle into place with rollback-safe directory swaps."""
    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve()
    validate_model_bundle(source)

    if destination.exists() and not force:
        validate_model_bundle(destination)
        return

    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o750)
    staging = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}-", dir=destination.parent)
    )
    backup = destination.with_name(f".{destination.name}.previous")

    try:
        for spec in MODEL_SPECS.values():
            shutil.copytree(source / spec.directory, staging / spec.directory)
        validate_model_bundle(staging)

        if backup.exists():
            shutil.rmtree(backup)
        if destination.exists():
            destination.rename(backup)
        staging.rename(destination)
        if backup.exists():
            shutil.rmtree(backup)
    except Exception:
        if not destination.exists() and backup.exists():
            backup.rename(destination)
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)
