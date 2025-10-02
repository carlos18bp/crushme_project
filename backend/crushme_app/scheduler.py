"""
APScheduler configuration for automatic cache warmup
Runs cache refresh every 50 minutes to prevent cache expiration
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Scheduler instance
scheduler = None


def start_scheduler():
    """
    Iniciar el scheduler en segundo plano
    Se ejecuta automáticamente cuando Django inicia
    """
    global scheduler
    
    if scheduler is not None:
        logger.warning("⚠️  Scheduler already running")
        return
    
    try:
        from crushme_app.services.cache_warmup_service import warmup_all_cache
        
        scheduler = BackgroundScheduler()
        
        # Configurar tarea: ejecutar cada 50 minutos
        # (antes de que expire el caché de 60 minutos)
        scheduler.add_job(
            warmup_all_cache,
            trigger=IntervalTrigger(minutes=50),
            id='warmup_woocommerce_cache',
            name='WooCommerce Cache Warmup',
            replace_existing=True,
            max_instances=1  # Solo una instancia a la vez
        )
        
        # Ejecutar inmediatamente al iniciar (opcional)
        # scheduler.add_job(
        #     warmup_all_cache,
        #     id='warmup_woocommerce_cache_startup',
        #     name='WooCommerce Cache Warmup (Startup)',
        #     replace_existing=True
        # )
        
        scheduler.start()
        
        logger.info("=" * 80)
        logger.info("✅ APScheduler started successfully")
        logger.info("🔥 Cache warmup scheduled every 50 minutes")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Error starting scheduler: {str(e)}")


def stop_scheduler():
    """
    Detener el scheduler
    """
    global scheduler
    
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("🛑 APScheduler stopped")



