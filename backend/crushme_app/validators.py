"""Reusable validation for user-supplied files."""

from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError


ALLOWED_IMAGE_FORMATS = {'GIF', 'JPEG', 'PNG', 'WEBP'}
ALLOWED_IMAGE_CONTENT_TYPES = {
    'image/gif',
    'image/jpeg',
    'image/png',
    'image/webp',
}


def validate_image_upload(upload):
    """Reject oversized, malformed, or unsupported image uploads."""
    if upload.size > settings.MAX_IMAGE_UPLOAD_SIZE:
        raise ValidationError('Image exceeds the configured size limit.')

    content_type = getattr(upload, 'content_type', None)
    if content_type and content_type.lower() not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise ValidationError('Unsupported image content type.')

    try:
        position = upload.tell()
        image = Image.open(upload)
        image_format = image.format
        width, height = image.size
        image.verify()
    except (Image.DecompressionBombError, UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValidationError('Upload is not a valid image.') from exc
    finally:
        try:
            upload.seek(position if 'position' in locals() else 0)
        except (AttributeError, OSError):
            pass

    if image_format not in ALLOWED_IMAGE_FORMATS:
        raise ValidationError('Unsupported image format.')
    if width * height > settings.MAX_IMAGE_PIXELS:
        raise ValidationError('Image dimensions are too large.')

    return upload
