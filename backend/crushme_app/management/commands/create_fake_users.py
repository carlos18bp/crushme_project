"""
Django management command to create fake users for testing
Based on gym_project pattern using Faker library
Usage: python manage.py create_fake_users [--num_users 20]
"""
from django.core.management.base import BaseCommand
from faker import Faker
from crushme_app.models import User

class Command(BaseCommand):
    help = 'Create fake users for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--num_users',
            type=int,
            default=20,
            help='Number of users to create (default: 20)'
        )

    def handle(self, *args, **options):
        fake = Faker()
        num_users = options['num_users']

        self.stdout.write(f'Creating {num_users} fake users...')

        # Create fake users
        for i in range(num_users):
            # Generate unique email
            counter = 1
            first_name = fake.first_name()
            last_name = fake.last_name()
            base_email = f'{first_name.lower()}.{last_name.lower()}@example.com'
            email = base_email
            
            while User.objects.filter(email=email).exists():
                email = f'{first_name.lower()}.{last_name.lower()}{counter}@example.com'
                counter += 1

            user = User.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            user.set_password('password123')  # Default password for testing
            user.save()
            
            self.stdout.write(self.style.SUCCESS(f'User created: {user.email}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_users} fake users'))
