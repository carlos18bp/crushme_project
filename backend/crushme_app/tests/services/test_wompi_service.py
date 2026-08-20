import hashlib

from django.test import override_settings

from crushme_app.services.wompi_service import WompiService


def _signed_event(secret='events-secret'):
    event = {
        'event': 'transaction.updated',
        'data': {
            'transaction': {
                'id': 'txn-123',
                'status': 'APPROVED',
                'amount_in_cents': 4490000,
            }
        },
        'environment': 'test',
        'signature': {
            'properties': [
                'transaction.id',
                'transaction.status',
                'transaction.amount_in_cents',
            ],
        },
        'timestamp': 1530291411,
    }
    signed_value = f'txn-123APPROVED4490000{event["timestamp"]}{secret}'
    event['signature']['checksum'] = hashlib.sha256(
        signed_value.encode('utf-8')
    ).hexdigest().upper()
    return event


@override_settings(WOMPI_EVENTS_SECRET='events-secret')
def test_verify_signature_accepts_dynamic_properties_in_declared_order():
    event = _signed_event()

    assert WompiService().verify_signature(event) is True


@override_settings(WOMPI_EVENTS_SECRET='events-secret')
def test_verify_signature_accepts_matching_header_checksum():
    event = _signed_event()

    assert WompiService().verify_signature(
        event, event['signature']['checksum'].lower()
    ) is True


@override_settings(WOMPI_EVENTS_SECRET='events-secret')
def test_verify_signature_rejects_tampered_transaction_data():
    event = _signed_event()
    event['data']['transaction']['amount_in_cents'] = 1

    assert WompiService().verify_signature(event) is False


@override_settings(WOMPI_EVENTS_SECRET='events-secret')
def test_verify_signature_rejects_missing_declared_property():
    event = _signed_event()
    event['signature']['properties'].append('transaction.missing')

    assert WompiService().verify_signature(event) is False


@override_settings(WOMPI_EVENTS_SECRET='')
def test_verify_signature_fails_closed_without_events_secret():
    event = _signed_event()

    assert WompiService().verify_signature(event) is False
