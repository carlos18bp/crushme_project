"""State transitions and integrity checks for durable payment sessions."""

from decimal import Decimal, InvalidOperation

from ..models import Order, PaymentSession


def payment_matches_session(session, amount, currency):
    try:
        received_amount = Decimal(str(amount)).quantize(Decimal('0.01'))
    except (InvalidOperation, TypeError, ValueError):
        return False
    return (
        received_amount == session.expected_amount
        and str(currency).upper() == session.currency
    )


def mark_session_paid(session, external_id=None):
    if external_id:
        if session.external_id and session.external_id != external_id:
            return False
        session.external_id = external_id
    session.status = PaymentSession.STATUS_PAID
    session.save(update_fields=['external_id', 'status', 'updated_at'])
    return True


def mark_session_processed(session, result):
    order_data = result.data.get('order', {}) if hasattr(result, 'data') else {}
    order_id = order_data.get('id')
    if not order_id:
        return False

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return False

    session.order = order
    session.status = PaymentSession.STATUS_PROCESSED
    session.order_data = {}
    session.save(update_fields=['order', 'status', 'order_data', 'updated_at'])
    return True
