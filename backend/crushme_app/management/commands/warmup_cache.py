"""
Management command to warmup WooCommerce cache
Usage: python manage.py warmup_cache
"""
from django.core.management.base import BaseCommand
from crushme_app.services.cache_warmup_service import warmup_all_cache


class Command(BaseCommand):
    help = 'Pre-calentar caché de WooCommerce para mejorar rendimiento'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔥 Iniciando pre-calentamiento de caché...'))
        
        results = warmup_all_cache()
        
        # Mostrar resultados
        for key, success in results.items():
            if success:
                self.stdout.write(self.style.SUCCESS(f'  ✅ {key}: OK'))
            else:
                self.stdout.write(self.style.ERROR(f'  ❌ {key}: FAILED'))
        
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        
        if success_count == total_count:
            self.stdout.write(self.style.SUCCESS(f'\n✅ Caché pre-calentado exitosamente ({success_count}/{total_count})'))
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠️  Caché pre-calentado parcialmente ({success_count}/{total_count})'))
