"""
Django management command to create fake orders for testing
Based on gym_project pattern using Faker library
Usage: python manage.py create_fake_orders [--num_orders 30]
"""
from django.core.management.base import BaseCommand
from faker import Faker
from crushme_app.models import User, Product, Order, OrderItem
from django.utils import timezone
import random
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create fake orders for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--num_orders',
            type=int,
            default=30,
            help='Number of orders to create (default: 30)'
        )

    def handle(self, *args, **options):
        fake = Faker()
        num_orders = options['num_orders']

        # Get existing users and products
        users = list(User.objects.all())
        products = list(Product.objects.filter(is_active=True))

        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first with: python manage.py create_fake_users'))
            return

        if not products:
            self.stdout.write(self.style.ERROR('No active products found. Please create products first with: python manage.py create_fake_products'))
            return

        self.stdout.write(f'Creating {num_orders} fake orders...')

        # Order statuses with weights (more pending and delivered orders)
        status_choices = [
            ('pending', 2),
            ('processing', 3),
            ('shipped', 2),
            ('delivered', 4),
            ('cancelled', 1),
            ('refunded', 1)
        ]
        
        statuses = []
        for status, weight in status_choices:
            statuses.extend([status] * weight)

        for i in range(num_orders):
            # Select a random user
            user = random.choice(users)
            
            # Generate order data
            status = random.choice(statuses)
            
            # Create order
            order = Order.objects.create(
                user=user,
                total=Decimal('0.00'),  # Will be calculated after adding items
                shipping_address=fake.street_address(),
                shipping_city=fake.city(),
                shipping_state=fake.state(),
                shipping_postal_code=fake.postcode(),
                shipping_country=fake.country(),
                phone_number=fake.phone_number()[:20],  # Limit to 20 chars
                status=status,
                notes=fake.text(max_nb_chars=200) if random.choice([True, False]) else '',
            )
            
            # Add random products to order
            num_items = random.randint(1, 4)  # 1 to 4 items per order
            selected_products = random.sample(products, min(num_items, len(products)))
            total = Decimal('0.00')
            
            for product in selected_products:
                quantity = random.randint(1, 2)
                unit_price = product.price
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_description=product.description[:200],  # Limit description
                    quantity=quantity,
                    unit_price=unit_price
                )
                
                total += unit_price * quantity
            
            # Update order total
            order.total = total
            
            # Set timestamps based on status
            if status in ['shipped', 'delivered']:
                order.shipped_at = fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.get_current_timezone())
            
            if status == 'delivered':
                order.delivered_at = fake.date_time_between(start_date=order.shipped_at, end_date='now', tzinfo=timezone.get_current_timezone())
            
            order.save()
            
            self.stdout.write(self.style.SUCCESS(f'Order {order.order_number} created for {user.email} (${total:.2f})'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_orders} fake orders'))