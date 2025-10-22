"""
WooCommerce Synchronization Service
Syncs products, categories, and variations from WooCommerce to local database
"""
import logging
from datetime import datetime, timezone as dt_timezone
from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive
from django.utils import timezone

from ..models import (
    WooCommerceCategory,
    WooCommerceProduct,
    WooCommerceProductImage,
    WooCommerceProductVariation,
    ProductSyncLog
)
from .woocommerce_service import woocommerce_service

logger = logging.getLogger(__name__)


class WooCommerceSyncService:
    """
    Service to synchronize WooCommerce data to local database.
    """
    
    def __init__(self):
        self.wc_service = woocommerce_service
        self.sync_log = None
    
    def sync_all(self):
        """
        Full synchronization: categories, products, variations, and images.
        """
        self.sync_log = ProductSyncLog.objects.create(
            sync_type=ProductSyncLog.SYNC_TYPE_FULL
        )
        
        try:
            logger.info("🚀 Starting full WooCommerce synchronization...")
            
            # 1. Sync categories first
            categories_count = self.sync_categories()
            logger.info(f"✅ Synced {categories_count} categories")
            
            # 2. Sync products
            products_count = self.sync_products()
            logger.info(f"✅ Synced {products_count} products")
            
            # 3. Sync variations for variable products
            variations_count = self.sync_variations()
            logger.info(f"✅ Synced {variations_count} variations")
            
            self.sync_log.mark_completed(status='success')
            logger.info(f"🎉 Full sync completed successfully!")
            
            return {
                'success': True,
                'categories': categories_count,
                'products': products_count,
                'variations': variations_count,
                'log_id': self.sync_log.id
            }
            
        except Exception as e:
            logger.error(f"❌ Full sync failed: {str(e)}")
            self.sync_log.add_error(str(e))
            self.sync_log.mark_completed(status='failed')
            return {
                'success': False,
                'error': str(e),
                'log_id': self.sync_log.id
            }
    
    def sync_categories(self):
        """
        Sync all categories from WooCommerce.
        """
        logger.info("📁 Syncing categories...")
        synced_count = 0
        page = 1
        per_page = 100
        
        while True:
            result = self.wc_service.get_categories(per_page=per_page, page=page)
            
            if not result['success']:
                logger.error(f"Failed to fetch categories page {page}")
                break
            
            categories = result['data']
            if not categories:
                break
            
            for cat_data in categories:
                try:
                    self._sync_category(cat_data)
                    synced_count += 1
                except Exception as e:
                    logger.error(f"Error syncing category {cat_data.get('id')}: {str(e)}")
                    if self.sync_log:
                        self.sync_log.add_error(f"Category {cat_data.get('id')}: {str(e)}")
            
            if len(categories) < per_page:
                break
            
            page += 1
        
        # Update parent relationships after all categories are synced
        self._update_category_parents()
        
        if self.sync_log:
            self.sync_log.categories_synced = synced_count
            self.sync_log.save()
        
        return synced_count
    
    @transaction.atomic
    def _sync_category(self, cat_data):
        """
        Sync a single category.
        """
        wc_id = cat_data['id']
        
        category, created = WooCommerceCategory.objects.update_or_create(
            wc_id=wc_id,
            defaults={
                'name': cat_data.get('name', ''),
                'slug': cat_data.get('slug', ''),
                'description': cat_data.get('description', ''),
                'wc_parent_id': cat_data.get('parent', 0),
                'product_count': cat_data.get('count', 0),
                'image_url': cat_data.get('image', {}).get('src', '') if cat_data.get('image') else '',
                'display_order': cat_data.get('menu_order', 0),
            }
        )
        
        action = "Created" if created else "Updated"
        logger.debug(f"  {action} category: {category.name} (ID: {wc_id})")
        
        return category
    
    def _update_category_parents(self):
        """
        Update parent relationships after all categories are synced.
        """
        logger.info("🔗 Updating category parent relationships...")
        
        for category in WooCommerceCategory.objects.filter(wc_parent_id__gt=0):
            try:
                parent = WooCommerceCategory.objects.get(wc_id=category.wc_parent_id)
                category.parent = parent
                category.save(update_fields=['parent'])
            except WooCommerceCategory.DoesNotExist:
                logger.warning(f"Parent category {category.wc_parent_id} not found for {category.name}")
    
    def sync_products(self):
        """
        Sync all products from WooCommerce.
        """
        logger.info("📦 Syncing products...")
        synced_count = 0
        page = 1
        per_page = 100
        
        while True:
            result = self.wc_service.get_products(per_page=per_page, page=page)
            
            if not result['success']:
                logger.error(f"Failed to fetch products page {page}")
                break
            
            products = result['data']
            if not products:
                break
            
            for product_data in products:
                try:
                    self._sync_product(product_data)
                    synced_count += 1
                except Exception as e:
                    logger.error(f"Error syncing product {product_data.get('id')}: {str(e)}")
                    if self.sync_log:
                        self.sync_log.add_error(f"Product {product_data.get('id')}: {str(e)}")
            
            logger.info(f"  Synced page {page} ({len(products)} products)")
            
            if len(products) < per_page:
                break
            
            page += 1
        
        if self.sync_log:
            self.sync_log.products_synced = synced_count
            self.sync_log.save()
        
        return synced_count
    
    @transaction.atomic
    def _sync_product(self, product_data):
        """
        Sync a single product with its images.
        """
        wc_id = product_data['id']
        
        # Parse dates and make them timezone-aware
        date_created = parse_datetime(product_data.get('date_created', '')) if product_data.get('date_created') else None
        if date_created and is_naive(date_created):
            date_created = make_aware(date_created)
        
        date_modified = parse_datetime(product_data.get('date_modified', '')) if product_data.get('date_modified') else None
        if date_modified and is_naive(date_modified):
            date_modified = make_aware(date_modified)
        
        # Create/update product
        product, created = WooCommerceProduct.objects.update_or_create(
            wc_id=wc_id,
            defaults={
                'name': product_data.get('name', ''),
                'slug': product_data.get('slug', ''),
                'permalink': product_data.get('permalink', ''),
                'product_type': product_data.get('type', 'simple'),
                'short_description': product_data.get('short_description', ''),
                'description': product_data.get('description', ''),
                'price': product_data.get('price') or None,
                'regular_price': product_data.get('regular_price') or None,
                'sale_price': product_data.get('sale_price') or None,
                'on_sale': product_data.get('on_sale', False),
                'stock_status': product_data.get('stock_status', 'instock'),
                'stock_quantity': product_data.get('stock_quantity'),
                'manage_stock': product_data.get('manage_stock', False),
                'attributes': product_data.get('attributes', []),
                'default_attributes': product_data.get('default_attributes', []),
                'weight': product_data.get('weight', ''),
                'length': product_data.get('dimensions', {}).get('length', ''),
                'width': product_data.get('dimensions', {}).get('width', ''),
                'height': product_data.get('dimensions', {}).get('height', ''),
                'average_rating': product_data.get('average_rating', 0),
                'rating_count': product_data.get('rating_count', 0),
                'total_sales': product_data.get('total_sales', 0),
                'status': product_data.get('status', 'publish'),
                'featured': product_data.get('featured', False),
                'parent_id': product_data.get('parent_id', 0),
                'date_created_wc': date_created,
                'date_modified_wc': date_modified,
            }
        )
        
        action = "Created" if created else "Updated"
        logger.debug(f"  {action} product: {product.name} (ID: {wc_id})")
        
        # Sync categories
        if product_data.get('categories'):
            category_ids = [cat['id'] for cat in product_data['categories']]
            categories = WooCommerceCategory.objects.filter(wc_id__in=category_ids)
            product.categories.set(categories)
        
        # Sync images
        self._sync_product_images(product, product_data.get('images', []))
        
        return product
    
    def _sync_product_images(self, product, images_data):
        """
        Sync product images.
        """
        if not images_data:
            return
        
        # Delete old images
        product.images.all().delete()
        
        # Create new images
        images_synced = 0
        for img_data in images_data:
            try:
                WooCommerceProductImage.objects.create(
                    product=product,
                    wc_id=img_data.get('id', 0),
                    src=img_data.get('src', ''),
                    thumbnail=img_data.get('thumbnail', ''),
                    name=img_data.get('name', ''),
                    alt=img_data.get('alt', ''),
                    position=img_data.get('position', 0),
                )
                images_synced += 1
            except Exception as e:
                logger.error(f"Error syncing image for product {product.wc_id}: {str(e)}")
        
        if self.sync_log and images_synced > 0:
            self.sync_log.images_synced += images_synced
            self.sync_log.save()
    
    def sync_variations(self):
        """
        Sync variations for all variable products.
        """
        logger.info("🎨 Syncing product variations...")
        synced_count = 0
        
        variable_products = WooCommerceProduct.objects.filter(
            product_type=WooCommerceProduct.TYPE_VARIABLE
        )
        
        logger.info(f"  Found {variable_products.count()} variable products")
        
        for product in variable_products:
            try:
                count = self._sync_product_variations(product)
                synced_count += count
            except Exception as e:
                logger.error(f"Error syncing variations for product {product.wc_id}: {str(e)}")
                if self.sync_log:
                    self.sync_log.add_error(f"Variations for product {product.wc_id}: {str(e)}")
        
        if self.sync_log:
            self.sync_log.variations_synced = synced_count
            self.sync_log.save()
        
        return synced_count
    
    @transaction.atomic
    def _sync_product_variations(self, product):
        """
        Sync variations for a single variable product.
        """
        synced_count = 0
        page = 1
        per_page = 100
        
        while True:
            result = self.wc_service.get_product_variations(
                product_id=product.wc_id,
                per_page=per_page,
                page=page
            )
            
            if not result['success']:
                logger.error(f"Failed to fetch variations for product {product.wc_id}")
                break
            
            variations = result['data']
            if not variations:
                break
            
            for var_data in variations:
                try:
                    self._sync_variation(product, var_data)
                    synced_count += 1
                except Exception as e:
                    logger.error(f"Error syncing variation {var_data.get('id')}: {str(e)}")
            
            if len(variations) < per_page:
                break
            
            page += 1
        
        logger.debug(f"  Synced {synced_count} variations for {product.name}")
        return synced_count
    
    def _sync_variation(self, product, var_data):
        """
        Sync a single product variation.
        """
        wc_id = var_data['id']
        
        # Parse dates and make them timezone-aware
        # WooCommerce dates come as strings like "2023-09-04T17:25:53"
        date_created_str = var_data.get('date_created', '')
        if date_created_str:
            date_created = parse_datetime(date_created_str)
            if date_created and is_naive(date_created):
                date_created = make_aware(date_created, timezone=dt_timezone.utc)
        else:
            date_created = None
        
        date_modified_str = var_data.get('date_modified', '')
        if date_modified_str:
            date_modified = parse_datetime(date_modified_str)
            if date_modified and is_naive(date_modified):
                date_modified = make_aware(date_modified, timezone=dt_timezone.utc)
        else:
            date_modified = None
        
        # Parse attributes
        attributes = {}
        for attr in var_data.get('attributes', []):
            attributes[attr.get('name', '')] = attr.get('option', '')
        
        # Create/update variation
        variation, created = WooCommerceProductVariation.objects.update_or_create(
            wc_id=wc_id,
            defaults={
                'wc_product_id': product.wc_id,
                'product': product,
                'permalink': var_data.get('permalink', ''),
                'price': var_data.get('price') or None,
                'regular_price': var_data.get('regular_price') or None,
                'sale_price': var_data.get('sale_price') or None,
                'on_sale': var_data.get('on_sale', False),
                'stock_status': var_data.get('stock_status', 'instock'),
                'stock_quantity': var_data.get('stock_quantity'),
                'manage_stock': var_data.get('manage_stock', False),
                'attributes': attributes,
                'image_url': var_data.get('image', {}).get('src', '') if var_data.get('image') else '',
                'weight': var_data.get('weight', ''),
                'length': var_data.get('dimensions', {}).get('length', ''),
                'width': var_data.get('dimensions', {}).get('width', ''),
                'height': var_data.get('dimensions', {}).get('height', ''),
                'status': var_data.get('status', 'publish'),
                'date_created_wc': date_created,
                'date_modified_wc': date_modified,
            }
        )
        
        return variation
    
    def sync_stock_and_prices(self, product_ids=None):
        """
        Quick sync: only update stock and prices for specified products.
        This should be called frequently (every 5-10 minutes).
        
        Args:
            product_ids: List of WooCommerce product IDs to sync. If None, sync all.
        """
        logger.info("💰 Syncing stock and prices...")
        
        if product_ids:
            products = WooCommerceProduct.objects.filter(wc_id__in=product_ids)
        else:
            products = WooCommerceProduct.objects.filter(status='publish')
        
        updated_count = 0
        
        for product in products:
            try:
                result = self.wc_service.get_product_by_id(product.wc_id)
                
                if result['success']:
                    product_data = result['data']
                    product.price = product_data.get('price') or None
                    product.regular_price = product_data.get('regular_price') or None
                    product.sale_price = product_data.get('sale_price') or None
                    product.on_sale = product_data.get('on_sale', False)
                    product.stock_status = product_data.get('stock_status', 'instock')
                    product.stock_quantity = product_data.get('stock_quantity')
                    product.manage_stock = product_data.get('manage_stock', False)
                    product.save(update_fields=[
                        'price', 'regular_price', 'sale_price', 'on_sale',
                        'stock_status', 'stock_quantity', 'manage_stock', 'synced_at'
                    ])
                    updated_count += 1
            except Exception as e:
                logger.error(f"Error updating stock/price for product {product.wc_id}: {str(e)}")
        
        logger.info(f"✅ Updated stock/prices for {updated_count} products")
        return updated_count


# Singleton instance
woocommerce_sync_service = WooCommerceSyncService()
