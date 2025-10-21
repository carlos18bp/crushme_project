"""
Management command to setup price margins for all categories
"""
from django.core.management.base import BaseCommand
from crushme_app.models import WooCommerceCategory, CategoryPriceMargin, DefaultPriceMargin


class Command(BaseCommand):
    help = 'Setup price margins for all categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--margin',
            type=float,
            default=30.0,
            help='Default margin percentage to apply (default: 30)'
        )
        parser.add_argument(
            '--default-only',
            action='store_true',
            help='Only create default margin, not category margins'
        )

    def handle(self, *args, **options):
        margin_percentage = options['margin']
        default_only = options['default_only']
        
        self.stdout.write(self.style.WARNING('🔧 Setting up price margins...'))
        
        # Create or update default margin
        default_margin, created = DefaultPriceMargin.objects.get_or_create(
            defaults={
                'margin_percentage': margin_percentage,
                'is_active': True,
                'notes': 'Default margin for products without specific category margin'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Created default margin: {margin_percentage}%'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'ℹ️  Default margin already exists: {default_margin.margin_percentage}%'
                )
            )
        
        if default_only:
            self.stdout.write(self.style.SUCCESS('\n✅ Default margin setup complete!'))
            return
        
        # Create margins for all categories that don't have one
        categories = WooCommerceCategory.objects.all()
        created_count = 0
        existing_count = 0
        
        for category in categories:
            margin, created = CategoryPriceMargin.objects.get_or_create(
                category=category,
                defaults={
                    'margin_percentage': margin_percentage,
                    'is_active': True,
                    'notes': f'Auto-generated margin for {category.name}'
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    f'  ✅ Created margin for: {category.name} (+{margin_percentage}%)'
                )
            else:
                existing_count += 1
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Created {created_count} new margins'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                f'ℹ️  {existing_count} categories already had margins'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'📊 Total categories with margins: {created_count + existing_count}'
            )
        )
        self.stdout.write('\n' + self.style.SUCCESS('✅ Setup complete!'))
