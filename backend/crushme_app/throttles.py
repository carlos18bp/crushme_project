"""Named DRF throttles for public and resource-intensive surfaces."""

from rest_framework.throttling import UserRateThrottle


class LoginRateThrottle(UserRateThrottle):
    scope = 'auth_login'


class RegistrationRateThrottle(UserRateThrottle):
    scope = 'auth_registration'


class VerificationRateThrottle(UserRateThrottle):
    scope = 'auth_verification'


class PasswordResetRateThrottle(UserRateThrottle):
    scope = 'auth_password_reset'


class TokenRefreshRateThrottle(UserRateThrottle):
    scope = 'auth_token_refresh'


class PaymentCreateRateThrottle(UserRateThrottle):
    scope = 'payment_create'


class PaymentConfirmRateThrottle(UserRateThrottle):
    scope = 'payment_confirm'


class PaymentWebhookRateThrottle(UserRateThrottle):
    scope = 'payment_webhook'


class UploadRateThrottle(UserRateThrottle):
    scope = 'upload'


class PublicWriteRateThrottle(UserRateThrottle):
    scope = 'public_write'


class PublicSearchRateThrottle(UserRateThrottle):
    scope = 'public_search'
