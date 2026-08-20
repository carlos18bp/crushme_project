from crushme_app.services.paypal_service import PayPalService


def test_extract_capture_result_returns_verified_amount():
    payload = {
        'status': 'COMPLETED',
        'payer': {
            'email_address': 'buyer@example.com',
            'name': {'given_name': 'Ada', 'surname': 'Lovelace'},
        },
        'purchase_units': [{
            'payments': {
                'captures': [{
                    'id': 'CAPTURE-1',
                    'status': 'COMPLETED',
                    'amount': {'value': '19.25', 'currency_code': 'USD'},
                }]
            }
        }],
    }

    result = PayPalService._extract_capture_result(payload, 'ORDER-1')

    assert result['success'] is True
    assert result['captured_amount'] == '19.25'
    assert result['currency'] == 'USD'
    assert result['capture_id'] == 'CAPTURE-1'


def test_extract_capture_result_rejects_incomplete_capture():
    payload = {
        'status': 'APPROVED',
        'purchase_units': [{'payments': {'captures': []}}],
    }

    result = PayPalService._extract_capture_result(payload, 'ORDER-1')

    assert result['success'] is False
