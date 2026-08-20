"""Install or verify the pinned CPU-only translation model bundle."""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from crushme_app.services.translation_manifest import (
    TranslationModelError,
    install_model_bundle,
    validate_model_bundle,
)


class Command(BaseCommand):
    help = "Install or verify the pinned CTranslate2 ES/EN model bundle"

    def add_arguments(self, parser):
        mode = parser.add_mutually_exclusive_group(required=True)
        mode.add_argument("--source-dir", type=Path)
        mode.add_argument("--check", action="store_true")
        parser.add_argument("--force", action="store_true")

    def handle(self, *args, **options):
        destination = Path(settings.TRANSLATION_MODEL_DIR)
        if options["check"] and options["force"]:
            raise CommandError("--force requires --source-dir")
        try:
            if options["check"]:
                validate_model_bundle(destination)
            else:
                install_model_bundle(
                    options["source_dir"],
                    destination,
                    force=options["force"],
                )
        except TranslationModelError as error:
            raise CommandError(str(error)) from error

        self.stdout.write(
            self.style.SUCCESS(f"Translation models verified: {destination}")
        )
