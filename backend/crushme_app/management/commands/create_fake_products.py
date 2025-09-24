"""
Django management command to create fake products with real images for testing
Based on caropa_project pattern using real images from media/temp/
Usage: python manage.py create_fake_products [--num_products 50]
"""
import os
import random
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from faker import Faker
from django_attachments.models import Library, Attachment
from crushme_app.models import Product


class Command(BaseCommand):
    help = 'Create fake products with real gallery images for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--num_products',
            type=int,
            default=50,
            help='Number of products to create (default: 50)'
        )

    def handle(self, *args, **options):
        fake = Faker()
        num_products = options['num_products']

        self.stdout.write(f'Creating {num_products} fake products with real images...')

        # List of test images (relative to MEDIA_ROOT)
        test_images = [
            'temp/product/product/image_temp1.webp',
            'temp/product/product/image_temp2.webp',
            'temp/product/product/image_temp3.webp',
            'temp/product/product/image_temp4.webp',
        ]

        # Verify that test images exist
        media_root = settings.MEDIA_ROOT
        for image_path in test_images:
            full_path = os.path.join(media_root, image_path)
            if not os.path.isfile(full_path):
                self.stdout.write(
                    self.style.ERROR(f'Image file {full_path} not found. Please ensure images exist in media/temp/')
                )
                return

        # Categories available in our model
        categories = ['electronics', 'clothing', 'home', 'books', 'sports', 'toys', 'beauty', 'automotive', 'other']
        
        # Product name templates by category
        product_names = {
            'electronics': [
                'Smart Phone Pro', 'Wireless Headphones', 'Gaming Laptop', 'Smart TV 4K', 
                'Bluetooth Speaker', 'Tablet Pro', 'Digital Camera', 'Smart Watch',
                'Gaming Console', 'Wireless Mouse', 'Mechanical Keyboard', 'Power Bank'
            ],
            'clothing': [
                'Cotton T-Shirt', 'Denim Jeans', 'Running Shoes', 'Winter Jacket',
                'Casual Dress', 'Sports Hoodie', 'Leather Boots', 'Summer Shorts',
                'Polo Shirt', 'Sneakers', 'Baseball Cap', 'Yoga Pants'
            ],
            'home': [
                'Coffee Maker', 'Vacuum Cleaner', 'Air Purifier', 'Desk Lamp',
                'Throw Pillow', 'Wall Clock', 'Storage Box', 'Plant Pot',
                'Kitchen Scale', 'Cutting Board', 'Candle Set', 'Picture Frame'
            ],
            'books': [
                'Mystery Novel', 'Cookbook', 'Self-Help Guide', 'History Book',
                'Science Fiction', 'Biography', 'Art Book', 'Travel Guide',
                'Programming Manual', 'Poetry Collection', 'Children\'s Book', 'Dictionary'
            ],
            'sports': [
                'Yoga Mat', 'Dumbbells', 'Running Shoes', 'Tennis Racket',
                'Basketball', 'Fitness Tracker', 'Water Bottle', 'Gym Bag',
                'Resistance Bands', 'Jump Rope', 'Exercise Ball', 'Protein Shaker'
            ],
            'toys': [
                'Building Blocks', 'Action Figure', 'Board Game', 'Puzzle',
                'Remote Control Car', 'Doll House', 'Art Set', 'Musical Toy',
                'Educational Game', 'Stuffed Animal', 'Model Kit', 'Science Kit'
            ],
            'beauty': [
                'Face Cream', 'Lipstick', 'Shampoo', 'Perfume',
                'Makeup Brush Set', 'Nail Polish', 'Face Mask', 'Body Lotion',
                'Hair Dryer', 'Makeup Mirror', 'Skincare Set', 'Essential Oil'
            ],
            'automotive': [
                'Car Phone Mount', 'Dash Cam', 'Car Charger', 'Floor Mats',
                'Air Freshener', 'Tire Gauge', 'Jump Starter', 'Car Cover',
                'Seat Covers', 'Steering Wheel Cover', 'Car Vacuum', 'Tool Kit'
            ],
            'other': [
                'Gift Card', 'Storage Solution', 'Office Supplies', 'Pet Toy',
                'Garden Tool', 'Cleaning Supply', 'Travel Accessory', 'Tech Gadget'
            ]
        }
        
        for i in range(num_products):
            # Select category and appropriate product name
            category = random.choice(categories)
            product_name = random.choice(product_names[category])
            
            # Add some variation to the name
            variations = ['Pro', 'Plus', 'Premium', 'Deluxe', 'Classic', 'Modern', 'Essential']
            if random.choice([True, False]):
                product_name += f' {random.choice(variations)}'
            
            # Create a gallery (library) for the product
            gallery = Library.objects.create(title=f"Gallery for {product_name}")
            
            # Add random images to the gallery (1-4 images per product)
            num_images = random.randint(1, 4)
            selected_images = random.sample(test_images, num_images)
            
            for rank, image_path in enumerate(selected_images):
                full_path = os.path.join(media_root, image_path)
                try:
                    with open(full_path, 'rb') as image_file:
                        attachment = Attachment.objects.create(
                            library=gallery,
                            file=File(image_file, name=os.path.basename(image_path)),
                            original_name=os.path.basename(image_path),
                            rank=rank
                        )
                        # Set the first image as primary
                        if rank == 0:
                            gallery.primary_attachment = attachment
                            gallery.save()
                            
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Failed to add image {image_path}: {str(e)}')
                    )
            
            # Generate realistic product data
            product = Product.objects.create(
                name=product_name,
                description=fake.text(max_nb_chars=500),
                price=round(random.uniform(10.99, 999.99), 2),
                category=category,
                stock_quantity=random.randint(0, 100),
                is_active=random.choice([True, True, True, False]),  # 75% chance of being active
                gallery=gallery
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Product created: {product.name} (${product.price}) with {num_images} images'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {num_products} fake products with real images!')
        )