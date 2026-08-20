from decimal import Decimal

import pytest

from crushme_app import tasks
from crushme_app.models import Order, User


pytestmark = pytest.mark.django_db


def _order():
    user = User.objects.create_user(
        username='task-buyer',
        email='task-buyer@example.com',
        password='unused',
    )
    return Order.objects.create(
        user=user,
        email=user.email,
        name='Task buyer',
        total=Decimal('10.00'),
        address_line_1='Street 1',
        city='Medellin',
        state='Antioquia',
        zipcode='050001',
        country='CO',
        phone='+573001234567',
        status='processing',
    )


def test_sync_order_to_woocommerce_persists_remote_identifier(monkeypatch):
    order = _order()
    received = {}

    def fake_send(current_order, shipping_cost):
        received['order_id'] = current_order.id
        received['shipping_cost'] = shipping_cost
        return {'success': True, 'woocommerce_order_id': 9876}

    monkeypatch.setattr(tasks.woocommerce_order_service, 'send_order', fake_send)

    result = tasks.sync_order_to_woocommerce.call_local(order.id, '10.50')

    order.refresh_from_db()
    assert result['success'] is True
    assert order.woocommerce_order_id == 9876
    assert received == {'order_id': order.id, 'shipping_cost': '10.50'}


def test_sync_order_to_woocommerce_preserves_pending_state_on_failure(monkeypatch):
    order = _order()
    monkeypatch.setattr(
        tasks.woocommerce_order_service,
        'send_order',
        lambda *_args, **_kwargs: {'success': False},
    )

    result = tasks.sync_order_to_woocommerce.call_local(order.id, '10.50')

    order.refresh_from_db()
    assert result['success'] is False
    assert order.woocommerce_order_id is None
