"""
Wompi Order Views
Handles Wompi payment integration for order creation (Colombian market - COP only)
"""
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.conf import settings
from decimal import Decimal, InvalidOperation
import logging

from ..models import Order, PaymentSession
from ..serializers.order_serializers import OrderDetailSerializer
from ..services.checkout_service import build_checkout_order
from ..services.payment_session_service import (
    mark_session_paid,
    mark_session_processed,
    payment_matches_session,
)
from ..services.wompi_service import wompi_service
from ..throttles import (
    PaymentConfirmRateThrottle,
    PaymentCreateRateThrottle,
    PaymentWebhookRateThrottle,
    PublicSearchRateThrottle,
)
from .order_helpers import process_order_after_payment

logger = logging.getLogger(__name__)


def _amount_from_cents(value):
    try:
        return Decimal(str(value)) / Decimal('100')
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError('Invalid amount in cents') from exc


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([PaymentCreateRateThrottle])
def create_wompi_transaction(request):
    """Create signed Wompi widget data from a server-authoritative checkout."""
    try:
        language = request.headers.get('Accept-Language', 'en')
        order_data = build_checkout_order(
            request.data,
            currency='COP',
            authenticated_user=request.user,
            language=language,
        )
        amount_in_cents = int(Decimal(order_data['total']) * 100)
        reference = Order.generate_order_number()
        redirect_url = f'{settings.FRONTEND_URL}/checkout/wompi/success'

        wompi_result = wompi_service.create_transaction(
            amount_in_cents=amount_in_cents,
            reference=reference,
            customer_email=order_data['customer_email'],
            customer_name=order_data['customer_name'],
            redirect_url=redirect_url,
            phone_number=order_data['phone_number'],
            currency='COP',
        )
        if not wompi_result['success']:
            return Response(
                {'error': 'Failed to create Wompi transaction'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        PaymentSession.objects.create(
            provider=PaymentSession.PROVIDER_WOMPI,
            reference=reference,
            expected_amount=order_data['total'],
            currency='COP',
            order_data=order_data,
        )
        logger.info('[WOMPI] Created payment session for reference %s', reference)
        return Response({
            'success': True,
            'message': 'Wompi widget data prepared successfully',
            'widget_data': wompi_result['widget_data'],
            'reference': reference,
            'total': order_data['total'],
            'amount_in_cents': amount_in_cents,
            'items_count': len(order_data['items']),
            'discount_applied': bool(order_data['discount_code']),
        }, status=status.HTTP_201_CREATED)
    except ValidationError as exc:
        return Response({
            'error': 'Invalid checkout data',
            'fields': exc.detail,
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        logger.exception('[WOMPI] Failed to create payment session')
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([PaymentConfirmRateThrottle])
def confirm_wompi_payment(request):
    """Verify a Wompi transaction and process its persisted checkout session."""
    transaction_id = request.data.get('transaction_id')
    if not transaction_id:
        return Response(
            {'error': 'Wompi transaction ID is required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    verification = wompi_service.get_transaction(transaction_id)
    if not verification['success']:
        return Response({
            'error': 'Payment verification failed',
            'wompi_status': 'FAILED',
        }, status=status.HTTP_400_BAD_REQUEST)

    payment_status = verification.get('status')
    if payment_status != 'APPROVED':
        return Response({
            'error': 'Payment was not approved',
            'status': payment_status,
            'transaction_id': transaction_id,
        }, status=status.HTTP_400_BAD_REQUEST)

    reference = verification.get('reference')
    try:
        session = PaymentSession.objects.select_related('order').get(
            provider=PaymentSession.PROVIDER_WOMPI,
            reference=reference,
        )
    except PaymentSession.DoesNotExist:
        return Response(
            {'error': 'Payment session not found'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if session.status == PaymentSession.STATUS_PROCESSED and session.order:
        return Response({
            'success': True,
            'message': 'Order already processed',
            'order': OrderDetailSerializer(session.order).data,
            'payment': {
                'provider': PaymentSession.PROVIDER_WOMPI,
                'transaction_id': transaction_id,
                'status': payment_status,
            },
        }, status=status.HTTP_200_OK)

    try:
        paid_amount = _amount_from_cents(verification.get('amount_in_cents'))
    except ValueError:
        return Response(
            {'error': 'Invalid transaction amount'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not payment_matches_session(session, paid_amount, verification.get('currency')):
        logger.error('[WOMPI] Rejected confirmation with mismatched amount or currency')
        return Response(
            {'error': 'Payment does not match checkout session'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not mark_session_paid(session, external_id=transaction_id):
        return Response(
            {'error': 'Payment session conflict'},
            status=status.HTTP_409_CONFLICT,
        )

    payment_info = {
        'transaction_id': transaction_id,
        'status': payment_status,
        'payer_email': verification.get('customer_email'),
        'payer_name': session.order_data.get('customer_name', 'Guest'),
    }
    result = process_order_after_payment(
        request_data=session.order_data,
        payment_info=payment_info,
        payment_provider=PaymentSession.PROVIDER_WOMPI,
        lang=session.order_data.get('language', 'en'),
    )
    if result.status_code in {status.HTTP_200_OK, status.HTTP_201_CREATED}:
        if not mark_session_processed(session, result):
            return Response(
                {'error': 'Payment was approved but order finalization failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    return result


@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([PublicSearchRateThrottle])
def get_wompi_config(request):
    """
    Get Wompi configuration for frontend (PUBLIC ENDPOINT)
    Returns public_key needed for Wompi SDK
    """
    return Response({
        'public_key': settings.WOMPI_PUBLIC_KEY,
        'currency': 'COP',  # Wompi solo soporta COP
        'environment': getattr(settings, 'WOMPI_ENVIRONMENT', 'production')
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([PaymentConfirmRateThrottle])
def check_payment_status(request, reference):
    """Return the durable processing state for a Wompi checkout reference."""
    try:
        session = PaymentSession.objects.select_related('order').get(
            provider=PaymentSession.PROVIDER_WOMPI,
            reference=reference,
        )
    except PaymentSession.DoesNotExist:
        return Response({
            'status': 'pending',
            'message': 'Payment is being processed',
        }, status=status.HTTP_200_OK)

    if session.status == PaymentSession.STATUS_PROCESSED and session.order:
        return Response({
            'status': 'success',
            'order_id': session.order_id,
            'order_number': session.order.order_number,
            'transaction_id': session.external_id,
            'total': str(session.order.total),
            'message': 'Payment processed successfully',
        }, status=status.HTTP_200_OK)
    if session.status == PaymentSession.STATUS_FAILED:
        return Response({
            'status': 'error',
            'message': 'Payment was not approved',
        }, status=status.HTTP_200_OK)
    return Response({
        'status': 'pending',
        'message': 'Payment is being processed',
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([PaymentWebhookRateThrottle])
def wompi_webhook(request):
    """Authenticate a Wompi event before applying its payment transition."""
    try:
        checksum = request.headers.get('X-Event-Checksum')
        if not wompi_service.verify_signature(request.data, checksum):
            return Response(
                {'error': 'Invalid webhook signature'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        event_type = request.data.get('event')
        if event_type != 'transaction.updated':
            logger.info('[WOMPI WEBHOOK] Ignored signed event type: %s', event_type)
            return Response({
                'success': True,
                'message': 'Event received but not processed',
            }, status=status.HTTP_200_OK)

        expected_environment = (
            'prod'
            if getattr(settings, 'WOMPI_ENVIRONMENT', 'production').lower()
            in {'prod', 'production', 'live'}
            else 'test'
        )
        if request.data.get('environment') != expected_environment:
            logger.warning('[WOMPI WEBHOOK] Rejected event from unexpected environment')
            return Response(
                {'error': 'Invalid webhook environment'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transaction_data = request.data.get('data', {}).get('transaction', {})
        transaction_id = transaction_data.get('id')
        payment_status = transaction_data.get('status')
        reference = transaction_data.get('reference')
        if not all([transaction_id, payment_status, reference]):
            return Response(
                {'error': 'Invalid transaction event'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(
            '[WOMPI WEBHOOK] transaction=%s status=%s reference=%s',
            transaction_id,
            payment_status,
            reference,
        )
        try:
            session = PaymentSession.objects.select_related('order').get(
                provider=PaymentSession.PROVIDER_WOMPI,
                reference=reference,
            )
        except PaymentSession.DoesNotExist:
            return Response(
                {'error': 'Payment session not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            paid_amount = _amount_from_cents(
                transaction_data.get('amount_in_cents')
            )
        except ValueError:
            return Response(
                {'error': 'Invalid transaction amount'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not payment_matches_session(
            session,
            paid_amount,
            transaction_data.get('currency'),
        ):
            logger.error('[WOMPI WEBHOOK] Rejected mismatched amount or currency')
            return Response(
                {'error': 'Payment does not match checkout session'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if session.status == PaymentSession.STATUS_PROCESSED and session.order:
            return Response({
                'success': True,
                'message': 'Order already processed',
            }, status=status.HTTP_200_OK)

        if payment_status != 'APPROVED':
            if payment_status in {'DECLINED', 'VOIDED', 'ERROR'}:
                session.status = PaymentSession.STATUS_FAILED
                session.save(update_fields=['status', 'updated_at'])
            return Response({
                'success': True,
                'message': 'Event received but not processed',
            }, status=status.HTTP_200_OK)

        if not mark_session_paid(session, external_id=transaction_id):
            return Response(
                {'error': 'Payment session conflict'},
                status=status.HTTP_409_CONFLICT,
            )

        payment_info = {
            'transaction_id': transaction_id,
            'status': payment_status,
            'payer_email': transaction_data.get('customer_email'),
            'payer_name': session.order_data.get('customer_name', 'Guest'),
        }
        result = process_order_after_payment(
            request_data=session.order_data,
            payment_info=payment_info,
            payment_provider=PaymentSession.PROVIDER_WOMPI,
            lang=session.order_data.get('language', 'en'),
        )
        if result.status_code not in {status.HTTP_200_OK, status.HTTP_201_CREATED}:
            return Response(
                {'error': 'Order processing failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        if not mark_session_processed(session, result):
            return Response(
                {'error': 'Order finalization failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({
            'success': True,
            'message': 'Webhook processed successfully',
        }, status=status.HTTP_200_OK)
    except Exception:
        logger.exception('[WOMPI WEBHOOK] Unexpected processing failure')
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
