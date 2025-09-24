"""
Django management command to create fake carts for testing
Based on gym_project pattern using Faker library
Usage: python manage.py create_fake_carts [--num_carts 20]
"""
from django.core.management.base import BaseCommand
from faker import Faker
from crushme_app.models import User, Product, Cart, CartItem
import random


class Command(BaseCommand):
    help = 'Create fake carts for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--num_carts',
            type=int,
            default=20,
            help='Number of carts to create (default: 20)'
        )

    def handle(self, *args, **options):
        fake = Faker()
        num_carts = options['num_carts']

        # Get existing users and products
        users = list(User.objects.all())
        products = list(Product.objects.filter(is_active=True))

        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first with: python manage.py create_fake_users'))
            return

        if not products:
            self.stdout.write(self.style.ERROR('No active products found. Please create products first with: python manage.py create_fake_products'))
            return

        self.stdout.write(f'Creating {num_carts} fake carts...')

        for i in range(num_carts):
            # Select a random user
            user = random.choice(users)
            
            # Create or get existing cart for user
            cart, created = Cart.objects.get_or_create(user=user)
            
            if not created:
                # Clear existing cart items to avoid duplicates
                cart.items.all().delete()
            
            # Add random products to cart
            num_items = random.randint(1, 5)  # 1 to 5 items per cart
            selected_products = random.sample(products, min(num_items, len(products)))
            
            for product in selected_products:
                quantity = random.randint(1, 3)
                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price
                )
            
            self.stdout.write(self.style.SUCCESS(f'Cart created for {user.email} with {num_items} items'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_carts} fake carts'))