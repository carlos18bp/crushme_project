from django.apps import AppConfig


class CrushmeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crushme_app'

    def ready(self):
        import crushme_project.tasks  # noqa: F401 — Huey periodic task discovery
