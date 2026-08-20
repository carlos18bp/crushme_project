"""Persistence tests for generated translation metadata."""

from unittest.mock import patch

import pytest
from django.test import override_settings

from crushme_app.models import TranslatedContent
from crushme_app.services.translation_batch_service import TranslationBatchService


@pytest.mark.django_db
@patch(
    "crushme_app.services.translation_batch_service.TranslationService.translate",
    return_value="A gift",
)
@override_settings(TRANSLATION_ENGINE="ctranslate2_cpu")
def test_generated_translation_records_cpu_engine(translate):
    """New cached content records the engine that generated its text."""
    service = TranslationBatchService()

    service._translate_field(
        content_type=TranslatedContent.CONTENT_TYPE_PRODUCT_NAME,
        object_id=4815,
        source_text="Un regalo",
    )

    translated = TranslatedContent.objects.get(object_id=4815)
    assert translated.translated_text == "A gift"
    assert translated.translation_engine == "ctranslate2-cpu-int8"
