from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class CrushmeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crushme_app'
    
    def ready(self):
        """
        Código que se ejecuta cuando Django está listo
        Aquí iniciamos el scheduler de caché automático
        """
        # Importar aquí para evitar circular imports
        import sys
        
        # Solo iniciar scheduler en el proceso principal
        # (no en migraciones, tests, etc.)
        if 'runserver' in sys.argv or 'gunicorn' in sys.argv[0]:
            try:
                from . import scheduler
                scheduler.start_scheduler()
            except Exception as e:
                logger.error(f"Error starting scheduler: {str(e)}")
