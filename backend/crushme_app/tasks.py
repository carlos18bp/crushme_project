"""Asynchronous application tasks."""

import logging

from huey.contrib.djhuey import db_task

from .models import Order
from .services.woocommerce_order_service import woocommerce_order_service


logger = logging.getLogger(__name__)


@db_task()
def sync_order_to_woocommerce(order_id, shipping_cost='0'):
    """Send a committed local order to WooCommerce outside the request cycle."""
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        logger.warning('[WOOCOMMERCE SYNC] Order %s no longer exists', order_id)
        return {'success': False, 'error': 'order_not_found'}

    result = woocommerce_order_service.send_order(
        order,
        shipping_cost=shipping_cost,
    )
    if not result.get('success'):
        logger.error('[WOOCOMMERCE SYNC] Order %s synchronization failed', order_id)
        return {'success': False, 'error': 'synchronization_failed'}

    Order.objects.filter(id=order_id).update(
        woocommerce_order_id=result.get('woocommerce_order_id')
    )
    logger.info('[WOOCOMMERCE SYNC] Order %s synchronized', order_id)
    return {
        'success': True,
        'woocommerce_order_id': result.get('woocommerce_order_id'),
    }
