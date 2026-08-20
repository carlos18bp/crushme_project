"""Durable payment intents used to verify gateway callbacks and captures."""

from django.db import models


class PaymentSession(models.Model):
    PROVIDER_PAYPAL = 'paypal'
    PROVIDER_WOMPI = 'wompi'
    PROVIDER_CHOICES = [
        (PROVIDER_PAYPAL, 'PayPal'),
        (PROVIDER_WOMPI, 'Wompi'),
    ]

    STATUS_CREATED = 'created'
    STATUS_PAID = 'paid'
    STATUS_PROCESSED = 'processed'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_CREATED, 'Created'),
        (STATUS_PAID, 'Paid'),
        (STATUS_PROCESSED, 'Processed'),
        (STATUS_FAILED, 'Failed'),
    ]

    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    reference = models.CharField(max_length=64, unique=True)
    external_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    expected_amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3)
    order_data = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
    )
    order = models.OneToOneField(
        'Order',
        on_delete=models.SET_NULL,
        related_name='payment_session',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.provider}:{self.reference} ({self.status})'
