"""
Django management command to create fake wishlists for testing
Based on gym_project pattern using Faker library
Usage: python manage.py create_fake_wishlists [--num_wishlists 25]
"""
from django.core.management.base import BaseCommand
from faker import Faker
from crushme_app.models import User, Product, WishList, WishListItem, FavoriteWishList
import random


class Command(BaseCommand):
    help = 'Create fake wishlists for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--num_wishlists',
            type=int,
            default=25,
            help='Number of wishlists to create (default: 25)'
        )

    def handle(self, *args, **options):
        fake = Faker()
        num_wishlists = options['num_wishlists']

        # Get existing users and products
        users = list(User.objects.all())
        products = list(Product.objects.filter(is_active=True))

        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first with: python manage.py create_fake_users'))
            return

        if not products:
            self.stdout.write(self.style.ERROR('No active products found. Please create products first with: python manage.py create_fake_products'))
            return

        self.stdout.write(f'Creating {num_wishlists} fake wishlists...')

        # Wishlist priorities
        priorities = ['low', 'medium', 'high']
        
        # Sample wishlist names
        wishlist_names = [
            'Birthday Wishlist', 'Christmas List', 'Wedding Registry', 'Baby Shower',
            'Home Essentials', 'Tech Gadgets', 'Fashion Favorites', 'Gift Ideas',
            'Dream Items', 'Back to School', 'Summer Vacation', 'Workout Gear',
            'Kitchen Must-Haves', 'Book Club Picks', 'Gaming Collection'
        ]

        for i in range(num_wishlists):
            # Select a random user
            user = random.choice(users)
            
            # Generate wishlist data
            name = random.choice(wishlist_names) + f" #{i+1}"
            is_public = random.choice([True, False])
            
            # Create wishlist
            wishlist = WishList.objects.create(
                user=user,
                name=name,
                description=fake.text(max_nb_chars=300),
                is_active=random.choice([True, True, True, False]),  # 75% active
                is_public=is_public
            )
            
            # Optionally add shipping data for some wishlists
            if random.choice([True, False]):
                wishlist.set_shipping_data(
                    name=user.get_full_name(),
                    address=fake.address().replace('\n', ', '),
                    phone=fake.phone_number()[:20],
                    email=user.email
                )
            
            # Add random products to wishlist
            num_items = random.randint(1, 6)  # 1 to 6 items per wishlist
            selected_products = random.sample(products, min(num_items, len(products)))
            
            for product in selected_products:
                priority = random.choice(priorities)
                notes = fake.sentence() if random.choice([True, False]) else ''
                
                WishListItem.objects.create(
                    wishlist=wishlist,
                    product=product,
                    notes=notes,
                    priority=priority
                )
            
            self.stdout.write(self.style.SUCCESS(f'Wishlist "{name}" created for {user.email} with {num_items} items'))

        # Create some favorite relationships between users and public wishlists
        public_wishlists = WishList.objects.filter(is_public=True)
        if public_wishlists.exists() and len(users) > 1:
            self.stdout.write('Creating favorite wishlist relationships...')
            
            favorites_created = 0
            for _ in range(min(20, len(users) * 2)):  # Create up to 20 favorites
                user = random.choice(users)
                wishlist = random.choice(public_wishlists)
                
                # Don't let users favorite their own wishlists
                if wishlist.user != user:
                    try:
                        FavoriteWishList.objects.get_or_create(user=user, wishlist=wishlist)
                        favorites_created += 1
                    except:
                        pass  # Skip if validation fails
            
            self.stdout.write(self.style.SUCCESS(f'Created {favorites_created} favorite relationships'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_wishlists} fake wishlists'))