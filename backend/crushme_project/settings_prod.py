"""Production-specific settings for crushme_project.

Imported automatically by ``settings.py`` when ``DJANGO_ENV == 'production'``.
"""

from decouple import config as _config

# ---------------------------------------------------------------------------
# DEBUG — hardcoded to False, never from environment
# ---------------------------------------------------------------------------
DEBUG = False

# ---------------------------------------------------------------------------
# Required settings — fail fast if missing
# ---------------------------------------------------------------------------
if not _config('DJANGO_SECRET_KEY', default=''):
    raise ValueError('DJANGO_SECRET_KEY is required in production')
if not _config('DJANGO_ALLOWED_HOSTS', default=''):
    raise ValueError('DJANGO_ALLOWED_HOSTS is required in production')

_required_integrations = (
    'WOOCOMMERCE_CONSUMER_KEY',
    'WOOCOMMERCE_CONSUMER_SECRET',
    'WOOCOMMERCE_API_URL',
    'PAYPAL_CLIENT_ID',
    'PAYPAL_CLIENT_SECRET',
    'PAYPAL_MODE',
    'WOMPI_PUBLIC_KEY',
    'WOMPI_PRIVATE_KEY',
    'WOMPI_EVENTS_SECRET',
    'WOMPI_INTEGRITY_KEY',
    'WOMPI_BASE_URL',
    'WOMPI_ENVIRONMENT',
)
_missing_integrations = [
    name for name in _required_integrations if not _config(name, default='').strip()
]
if _missing_integrations:
    raise ValueError(
        'Production integration settings are required: '
        + ', '.join(_missing_integrations)
    )

if _config('PAYPAL_MODE').lower() != 'live':
    raise ValueError('PAYPAL_MODE must be live in production')
if _config('WOMPI_ENVIRONMENT').lower() != 'production':
    raise ValueError('WOMPI_ENVIRONMENT must be production in production')
if not _config('WOMPI_BASE_URL').startswith('https://production.wompi.co/'):
    raise ValueError('WOMPI_BASE_URL must use Wompi production over HTTPS')
if not _config('WOOCOMMERCE_API_URL').startswith('https://'):
    raise ValueError('WOOCOMMERCE_API_URL must use HTTPS in production')

# ---------------------------------------------------------------------------
# Security hardening
# ---------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Lax'
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'
X_FRAME_OPTIONS = 'DENY'

# ---------------------------------------------------------------------------
# Database — MySQL
# ---------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': _config('DB_NAME'),
        'USER': _config('DB_USER'),
        'PASSWORD': _config('DB_PASSWORD'),
        'HOST': _config('DB_HOST', default='localhost'),
        'PORT': _config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ---------------------------------------------------------------------------
# Email — SMTP (GoDaddy)
# ---------------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
