"""
Django management command to sync WooCommerce data to local database
"""
from django.core.management.base import BaseCommand, CommandError
from crushme_app.services.woocommerce_sync_service import woocommerce_sync_service
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Synchronize products, categories, and variations from WooCommerce'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Perform full synchronization (categories, products, variations)',
        )
        parser.add_argument(
            '--categories',
            action='store_true',
            help='Sync only categories',
        )
        parser.add_argument(
            '--products',
            action='store_true',
            help='Sync only products',
        )
        parser.add_argument(
            '--variations',
            action='store_true',
            help='Sync only variations',
        )
        parser.add_argument(
            '--stock',
            action='store_true',
            help='Quick sync: update only stock and prices',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting WooCommerce synchronization...'))
        
        sync_service = woocommerce_sync_service
        
        try:
            # Full sync
            if options['full']:
                self.stdout.write('Running full synchronization...')
                result = sync_service.sync_all()
                
                if result['success']:
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ Full sync completed!\n"
                        f"   Categories: {result['categories']}\n"
                        f"   Products: {result['products']}\n"
                        f"   Variations: {result['variations']}\n"
                        f"   Log ID: {result['log_id']}"
                    ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f"❌ Full sync failed: {result['error']}"
                    ))
                    raise CommandError(f"Sync failed: {result['error']}")
            
            # Categories only
            elif options['categories']:
                self.stdout.write('Syncing categories...')
                count = sync_service.sync_categories()
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Synced {count} categories"
                ))
            
            # Products only
            elif options['products']:
                self.stdout.write('Syncing products...')
                count = sync_service.sync_products()
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Synced {count} products"
                ))
            
            # Variations only
            elif options['variations']:
                self.stdout.write('Syncing variations...')
                count = sync_service.sync_variations()
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Synced {count} variations"
                ))
            
            # Stock and prices quick sync
            elif options['stock']:
                self.stdout.write('Updating stock and prices...')
                count = sync_service.sync_stock_and_prices()
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Updated {count} products"
                ))
            
            # Default: full sync
            else:
                self.stdout.write('No option specified, running full sync...')
                result = sync_service.sync_all()
                
                if result['success']:
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ Full sync completed!\n"
                        f"   Categories: {result['categories']}\n"
                        f"   Products: {result['products']}\n"
                        f"   Variations: {result['variations']}\n"
                        f"   Log ID: {result['log_id']}"
                    ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f"❌ Full sync failed: {result['error']}"
                    ))
                    raise CommandError(f"Sync failed: {result['error']}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {str(e)}"))
            raise CommandError(f"Synchronization error: {str(e)}")
