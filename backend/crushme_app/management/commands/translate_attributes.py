"""
Django management command to translate product attributes
"""
from django.core.management.base import BaseCommand
from crushme_app.services.translation_batch_service import translation_batch_service
from crushme_app.models import WooCommerceProduct
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Translate product attributes (names and values) for variable products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-translation of already translated attributes',
        )
        parser.add_argument(
            '--product-id',
            type=int,
            help='Translate attributes for a specific product ID',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        product_id = options.get('product_id')
        
        self.stdout.write(self.style.SUCCESS('🔄 Starting attribute translation...'))
        
        if product_id:
            # Traducir un producto específico
            try:
                product = WooCommerceProduct.objects.get(wc_id=product_id)
                if not product.is_variable:
                    self.stdout.write(self.style.WARNING(
                        f'⚠️  Product {product_id} is not a variable product'
                    ))
                    return
                
                self.stdout.write(f'📦 Translating attributes for product: {product.name}')
                translation_batch_service._translate_product_attributes(product, force)
                self.stdout.write(self.style.SUCCESS('✅ Product attributes translated!'))
                
            except WooCommerceProduct.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Product {product_id} not found'))
                return
        else:
            # Traducir todos los productos variables
            products = WooCommerceProduct.objects.filter(
                status='publish',
                product_type=WooCommerceProduct.TYPE_VARIABLE
            )
            total = products.count()
            
            self.stdout.write(f'📦 Found {total} variable products')
            
            translated = 0
            errors = 0
            
            for idx, product in enumerate(products, 1):
                try:
                    if idx % 10 == 0 or idx == total:
                        self.stdout.write(f'   Progress: {idx}/{total} ({(idx/total*100):.1f}%)')
                    
                    translation_batch_service._translate_product_attributes(product, force)
                    translated += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'❌ Error translating product {product.wc_id}: {str(e)}'
                    ))
                    errors += 1
            
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Translation completed!\n'
                f'   Products processed: {translated}\n'
                f'   Errors: {errors}'
            ))
