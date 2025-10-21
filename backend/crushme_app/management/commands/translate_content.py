"""
Django management command to translate all synchronized content
"""
from django.core.management.base import BaseCommand, CommandError
from crushme_app.services.translation_batch_service import translation_batch_service
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Pre-translate all products and categories for fast delivery'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-translation of already translated content',
        )
        parser.add_argument(
            '--product-id',
            type=int,
            help='Translate only a specific product by WooCommerce ID',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌐 Starting content translation...'))
        
        try:
            # Traducir producto específico
            if options['product_id']:
                product_id = options['product_id']
                self.stdout.write(f'Translating product {product_id}...')
                
                success = translation_batch_service.translate_product(
                    product_id=product_id,
                    force_retranslate=options['force']
                )
                
                if success:
                    self.stdout.write(self.style.SUCCESS(
                        f'✅ Product {product_id} translated successfully'
                    ))
                else:
                    raise CommandError(f'Failed to translate product {product_id}')
            
            # Traducir todo
            else:
                force = options['force']
                if force:
                    self.stdout.write('Force mode: Re-translating all content...')
                else:
                    self.stdout.write('Translating new content only (use --force to re-translate)...')
                
                result = translation_batch_service.translate_all(
                    force_retranslate=force
                )
                
                if result['success']:
                    stats = result['stats']
                    self.stdout.write(self.style.SUCCESS(
                        f"\n✅ Translation completed!\n"
                        f"   📦 Products: {stats['products_translated']}\n"
                        f"   📁 Categories: {stats['categories_translated']}\n"
                        f"   📝 Total fields: {stats['fields_translated']}\n"
                        f"   ⚠️  Errors: {stats['errors']}\n"
                        f"   ⏭️  Skipped: {stats['skipped']}"
                    ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f"❌ Translation failed: {result.get('error', 'Unknown error')}"
                    ))
                    raise CommandError('Translation failed')
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            raise CommandError(f'Translation error: {str(e)}')
