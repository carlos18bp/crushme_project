import hashlib
from decimal import Decimal

import pytest
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from crushme_app.models import Order, PaymentSession, User
from crushme_app.views import order_helpers, paypal_order_views, wompi_order_views


pytestmark = pytest.mark.django_db


def _order():
    user = User.objects.create_user(
        username='buyer',
        email='buyer@example.com',
        password='unused',
    )
    return Order.objects.create(
        user=user,
        email=user.email,
        name='Buyer',
        total=Decimal('10.00'),
        address_line_1='Street 1',
        city='Medellin',
        state='Antioquia',
        zipcode='050001',
        country='CO',
        phone='+573001234567',
        transaction_id='CAPTURE-1',
        payment_provider='paypal',
        status='processing',
    )


def _paypal_session(amount='10.00'):
    return PaymentSession.objects.create(
        provider=PaymentSession.PROVIDER_PAYPAL,
        reference='PAYPAL-ORDER-1',
        external_id='PAYPAL-ORDER-1',
        expected_amount=amount,
        currency='USD',
        order_data={
            'customer_name': 'Canonical buyer',
            'language': 'en',
            'items': [{'woocommerce_product_id': 1, 'quantity': 1}],
        },
    )


def _wompi_session(amount='100.00'):
    return PaymentSession.objects.create(
        provider=PaymentSession.PROVIDER_WOMPI,
        reference='WOMPI-REF-1',
        expected_amount=amount,
        currency='COP',
        order_data={
            'customer_name': 'Canonical buyer',
            'language': 'es',
            'items': [{'woocommerce_product_id': 1, 'quantity': 1}],
        },
    )


def _wompi_event(amount_in_cents=10000, secret='events-secret'):
    event = {
        'event': 'transaction.updated',
        'data': {'transaction': {
            'id': 'WOMPI-TXN-1',
            'status': 'APPROVED',
            'reference': 'WOMPI-REF-1',
            'amount_in_cents': amount_in_cents,
            'currency': 'COP',
            'customer_email': 'payer@example.com',
        }},
        'environment': 'test',
        'signature': {'properties': [
            'transaction.id',
            'transaction.status',
            'transaction.amount_in_cents',
        ]},
        'timestamp': 1530291411,
    }
    signed = f'WOMPI-TXN-1APPROVED{amount_in_cents}{event["timestamp"]}{secret}'
    event['signature']['checksum'] = hashlib.sha256(signed.encode()).hexdigest()
    return event


def test_paypal_capture_processes_persisted_order_data(monkeypatch):
    session = _paypal_session()
    order = _order()
    received = {}
    monkeypatch.setattr(
        paypal_order_views.paypal_service,
        'capture_order',
        lambda _order_id: {
            'success': True,
            'status': 'COMPLETED',
            'capture_id': 'CAPTURE-1',
            'captured_amount': '10.00',
            'currency': 'USD',
        },
    )

    def fake_process(**kwargs):
        received.update(kwargs['request_data'])
        return Response({'order': {'id': order.id}}, status=201)

    monkeypatch.setattr(order_helpers, 'process_order_after_payment', fake_process)
    request = APIRequestFactory().post(
        '/api/orders/paypal/capture/',
        {
            'paypal_order_id': 'PAYPAL-ORDER-1',
            'customer_name': 'Tampered buyer',
            'total': '0.01',
        },
        format='json',
    )

    response = paypal_order_views.capture_paypal_order(request)

    assert response.status_code == 201
    assert received['customer_name'] == 'Canonical buyer'
    session.refresh_from_db()
    assert session.status == PaymentSession.STATUS_PROCESSED


def test_paypal_capture_rejects_mismatched_amount(monkeypatch):
    _paypal_session()
    monkeypatch.setattr(
        paypal_order_views.paypal_service,
        'capture_order',
        lambda _order_id: {
            'success': True,
            'status': 'COMPLETED',
            'capture_id': 'CAPTURE-1',
            'captured_amount': '0.01',
            'currency': 'USD',
        },
    )
    request = APIRequestFactory().post(
        '/api/orders/paypal/capture/',
        {'paypal_order_id': 'PAYPAL-ORDER-1'},
        format='json',
    )

    response = paypal_order_views.capture_paypal_order(request)

    assert response.status_code == 400


def test_wompi_webhook_rejects_invalid_signature(monkeypatch):
    _wompi_session()
    monkeypatch.setattr(wompi_order_views.wompi_service, 'events_secret', 'events-secret')
    event = _wompi_event()
    event['signature']['checksum'] = 'invalid'
    request = APIRequestFactory().post(
        '/api/orders/wompi/webhook/',
        event,
        format='json',
    )

    response = wompi_order_views.wompi_webhook(request)

    assert response.status_code == 401


def test_wompi_webhook_rejects_mismatched_amount(monkeypatch):
    _wompi_session()
    monkeypatch.setattr(wompi_order_views.wompi_service, 'events_secret', 'events-secret')
    request = APIRequestFactory().post(
        '/api/orders/wompi/webhook/',
        _wompi_event(amount_in_cents=1),
        format='json',
    )

    response = wompi_order_views.wompi_webhook(request)

    assert response.status_code == 400


def test_wompi_webhook_marks_payment_session_processed(monkeypatch):
    session = _wompi_session()
    order = _order()
    order.transaction_id = 'WOMPI-TXN-1'
    order.payment_provider = 'wompi'
    order.save(update_fields=['transaction_id', 'payment_provider'])
    monkeypatch.setattr(wompi_order_views.wompi_service, 'events_secret', 'events-secret')
    monkeypatch.setattr(
        wompi_order_views,
        'process_order_after_payment',
        lambda **_kwargs: Response({'order': {'id': order.id}}, status=201),
    )
    request = APIRequestFactory().post(
        '/api/orders/wompi/webhook/',
        _wompi_event(),
        format='json',
    )

    response = wompi_order_views.wompi_webhook(request)

    assert response.status_code == 200
    session.refresh_from_db()
    assert session.status == PaymentSession.STATUS_PROCESSED
