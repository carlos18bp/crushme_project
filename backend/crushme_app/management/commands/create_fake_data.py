"""
Master command to create all fake data for CrushMe e-commerce platform
Based on gym_project pattern
Usage: python manage.py create_fake_data [--users 20] [--products 50] [--carts 15] [--orders 30] [--wishlists 25]
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand

from crushme_app.fake_data_guard import ensure_fake_data_allowed


class Command(BaseCommand):
    help = 'Create comprehensive fake data for the CrushMe e-commerce platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=20,
            help='Number of fake users to create (default: 20)'
        )
        parser.add_argument(
            '--products',
            type=int,
            default=50,
            help='Number of fake products to create (default: 50)'
        )
        parser.add_argument(
            '--carts',
            type=int,
            default=15,
            help='Number of fake carts to create (default: 15)'
        )
        parser.add_argument(
            '--orders',
            type=int,
            default=30,
            help='Number of fake orders to create (default: 30)'
        )
        parser.add_argument(
            '--wishlists',
            type=int,
            default=25,
            help='Number of fake wishlists to create (default: 25)'
        )

    def handle(self, *args, **options):
        ensure_fake_data_allowed('create_fake_data')
        users = options['users']
        products = options['products']
        carts = options['carts']
        orders = options['orders']
        wishlists = options['wishlists']
        
        self.stdout.write(self.style.SUCCESS('🚀 Starting CrushMe fake data creation...'))
        self.stdout.write('')
        
        # Create data in logical order (dependencies matter)
        self.stdout.write('👥 Creating fake users...')
        call_command('create_fake_users', '--num_users', users)
        self.stdout.write('')
        
        self.stdout.write('📦 Creating fake products...')
        call_command('create_fake_products', '--num_products', products)
        self.stdout.write('')
        
        self.stdout.write('🛒 Creating fake carts...')
        call_command('create_fake_carts', '--num_carts', carts)
        self.stdout.write('')
        
        self.stdout.write('📋 Creating fake orders...')
        call_command('create_fake_orders', '--num_orders', orders)
        self.stdout.write('')
        
        self.stdout.write('💝 Creating fake wishlists...')
        call_command('create_fake_wishlists', '--num_wishlists', wishlists)
        self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('✅ Fake data creation completed successfully!'))
        self.stdout.write('')
        self.stdout.write('📊 Summary:')
        self.stdout.write(f'   • {users} users created')
        self.stdout.write(f'   • {products} products created')
        self.stdout.write(f'   • {carts} carts created')
        self.stdout.write(f'   • {orders} orders created')
        self.stdout.write(f'   • {wishlists} wishlists created')
        self.stdout.write('')
        self.stdout.write('🎉 Your CrushMe platform is now ready for testing!')
