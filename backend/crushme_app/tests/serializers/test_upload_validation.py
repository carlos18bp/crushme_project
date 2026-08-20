"""Validation tests for user-supplied images."""

from io import BytesIO

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image

from crushme_app.validators import validate_image_upload


def _image_upload(image_format='PNG', size=(2, 2), content_type='image/png'):
    stream = BytesIO()
    Image.new('RGB', size, color='red').save(stream, format=image_format)
    return SimpleUploadedFile(
        f'image.{image_format.lower()}',
        stream.getvalue(),
        content_type=content_type,
    )


def test_image_upload_accepts_verified_raster_content():
    """A supported raster image passes content validation."""
    upload = _image_upload()

    assert validate_image_upload(upload) is upload


def test_image_upload_rejects_disguised_non_image_content():
    """An image extension cannot disguise arbitrary bytes."""
    upload = SimpleUploadedFile(
        'fake.png',
        b'not-an-image',
        content_type='image/png',
    )

    with pytest.raises(ValidationError):
        validate_image_upload(upload)


@override_settings(MAX_IMAGE_UPLOAD_SIZE=10)
def test_image_upload_rejects_oversized_file():
    """Files larger than the configured limit are rejected."""
    upload = SimpleUploadedFile(
        'large.png',
        b'x' * 11,
        content_type='image/png',
    )

    with pytest.raises(ValidationError, match='size limit'):
        validate_image_upload(upload)


@override_settings(MAX_IMAGE_PIXELS=3)
def test_image_upload_rejects_excessive_pixel_count():
    """Pixel dimensions are bounded independently from file size."""
    upload = _image_upload(size=(2, 2))

    with pytest.raises(ValidationError, match='dimensions'):
        validate_image_upload(upload)
