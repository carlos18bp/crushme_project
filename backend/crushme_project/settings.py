"""Django base settings for crushme_project.

Shared settings used by both development and production environments.
Environment-specific overrides are auto-imported at the end of this file.
Tests use the explicit ``settings_test`` module so they never inherit
deployment resources.
"""

import os
from datetime import timedelta
from pathlib import Path

from decouple import Csv, config
from django.core.exceptions import ImproperlyConfigured
from huey import RedisHuey

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_NAME = 'crushme_project'

# ---------------------------------------------------------------------------
# Environment detection
# ---------------------------------------------------------------------------
DJANGO_ENV = config('DJANGO_ENV', default='development')
IS_PRODUCTION = DJANGO_ENV == 'production'
IS_TEST = DJANGO_ENV in {'test', 'e2e'}

# Argos remains available only as an explicit stage-1 rollback engine. Its
# unsafe Stanza model loader stays unreachable while rollback is available.
ARGOS_CHUNK_TYPE = config('ARGOS_CHUNK_TYPE', default='MINISBD').upper()
ARGOS_DEVICE_TYPE = config('ARGOS_DEVICE_TYPE', default='cpu').lower()
if ARGOS_CHUNK_TYPE != 'MINISBD':
    raise ImproperlyConfigured('ARGOS_CHUNK_TYPE must remain MINISBD')
if ARGOS_DEVICE_TYPE != 'cpu':
    raise ImproperlyConfigured('ARGOS_DEVICE_TYPE must remain cpu')
os.environ['ARGOS_CHUNK_TYPE'] = ARGOS_CHUNK_TYPE
os.environ['ARGOS_DEVICE_TYPE'] = ARGOS_DEVICE_TYPE

TRANSLATION_ENGINE = config('TRANSLATION_ENGINE', default='argos').lower()
if TRANSLATION_ENGINE not in {'argos', 'ctranslate2_cpu'}:
    raise ImproperlyConfigured(
        'TRANSLATION_ENGINE must be argos or ctranslate2_cpu'
    )
TRANSLATION_RUNTIME_ENABLED = True
TRANSLATION_SOCKET_PATH = config(
    'TRANSLATION_SOCKET_PATH',
    default='/run/crushme-translation/translation.sock',
)
TRANSLATION_MODEL_DIR = config(
    'TRANSLATION_MODEL_DIR',
    default=str(Path.home() / '.local/share/crushme/translation-models'),
)
TRANSLATION_TIMEOUT_SECONDS = config(
    'TRANSLATION_TIMEOUT_SECONDS', default=30.0, cast=float
)
if TRANSLATION_TIMEOUT_SECONDS <= 0 or TRANSLATION_TIMEOUT_SECONDS > 60:
    raise ImproperlyConfigured(
        'TRANSLATION_TIMEOUT_SECONDS must be greater than 0 and at most 60'
    )

# ---------------------------------------------------------------------------
# Core Django settings
# ---------------------------------------------------------------------------
SECRET_KEY = config('DJANGO_SECRET_KEY', default='change-me')
DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_CACHE_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'crushme',
        'TIMEOUT': 3600,
    }
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'rest_framework',
    'easy_thumbnails',
    'django_attachments',
    'crushme_app',
    'django_cleanup.apps.CleanupConfig',
    # Operations
    'dbbackup',
    'huey.contrib.djhuey',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'crushme_app.middleware.currency_middleware.CurrencyMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://127.0.0.1:5173,http://localhost:5173',
    cast=Csv(),
)

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://127.0.0.1:5173,http://localhost:5173',
    cast=Csv(),
)

# Configuraciones adicionales de CORS para desarrollo
CORS_ALLOW_CREDENTIALS = True

# Gateway widgets embed third-party content; they do not need to frame CrushMe.
X_FRAME_OPTIONS = 'DENY'

# Development keeps gateway popup communication available.
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

# Additional CORS settings for popups and payment gateways
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-currency',  # Custom header for currency
]

CORS_EXPOSE_HEADERS = [
    'content-type',
    'x-currency',
]

# Allow all HTTP methods for CORS
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

ROOT_URLCONF = 'crushme_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'crushme_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': config('DJANGO_DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DJANGO_DB_NAME', default=str(BASE_DIR / 'db.sqlite3')),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
    'dbbackup': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
        'OPTIONS': {
            'location': config('BACKUP_STORAGE_PATH', default='/var/backups/crushme_project'),
            'file_permissions_mode': 0o600,
            'directory_permissions_mode': 0o700,
        },
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'crushme_app.User'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'auth_login': config('THROTTLE_AUTH_LOGIN', default='10/min'),
        'auth_registration': config('THROTTLE_AUTH_REGISTRATION', default='5/hour'),
        'auth_verification': config('THROTTLE_AUTH_VERIFICATION', default='10/hour'),
        'auth_password_reset': config('THROTTLE_AUTH_PASSWORD_RESET', default='5/hour'),
        'auth_token_refresh': config('THROTTLE_AUTH_TOKEN_REFRESH', default='30/hour'),
        'payment_create': config('THROTTLE_PAYMENT_CREATE', default='20/hour'),
        'payment_confirm': config('THROTTLE_PAYMENT_CONFIRM', default='60/hour'),
        'payment_webhook': config('THROTTLE_PAYMENT_WEBHOOK', default='120/min'),
        'upload': config('THROTTLE_UPLOAD', default='30/hour'),
        'public_write': config('THROTTLE_PUBLIC_WRITE', default='20/hour'),
        'public_search': config('THROTTLE_PUBLIC_SEARCH', default='60/min'),
    },
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=config('JWT_ACCESS_TOKEN_MINUTES', default=15, cast=int)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=config('JWT_REFRESH_TOKEN_DAYS', default=7, cast=int)
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Upload limits are enforced again at serializer level after content inspection.
MAX_IMAGE_UPLOAD_SIZE = config(
    'MAX_IMAGE_UPLOAD_SIZE',
    default=5 * 1024 * 1024,
    cast=int,
)
MAX_IMAGE_PIXELS = config('MAX_IMAGE_PIXELS', default=25_000_000, cast=int)
DATA_UPLOAD_MAX_MEMORY_SIZE = config(
    'DATA_UPLOAD_MAX_MEMORY_SIZE',
    default=10 * 1024 * 1024,
    cast=int,
)
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_IMAGE_UPLOAD_SIZE
DATA_UPLOAD_MAX_NUMBER_FIELDS = config(
    'DATA_UPLOAD_MAX_NUMBER_FIELDS',
    default=200,
    cast=int,
)
DATA_UPLOAD_MAX_NUMBER_FILES = config(
    'DATA_UPLOAD_MAX_NUMBER_FILES',
    default=12,
    cast=int,
)
MAX_GALLERY_UPLOADS_PER_REQUEST = config(
    'MAX_GALLERY_UPLOADS_PER_REQUEST',
    default=10,
    cast=int,
)
DROPSHIPPING_PRODUCT_ID = config('DROPSHIPPING_PRODUCT_ID', default=48500, cast=int)

# Email settings
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtpout.secureserver.net')
EMAIL_PORT = config('EMAIL_PORT', default=465, cast=int)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = f"CrushMe Support <{config('EMAIL_HOST_USER', default='support@crushme.com.co')}>"
SERVER_EMAIL = config('EMAIL_HOST_USER', default='support@crushme.com.co')

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL = config('DJANGO_LOG_LEVEL', default='INFO')

(BASE_DIR / 'logs').mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'crushme_app': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# Thumbnail settings
THUMBNAIL_ALIASES = {
    '': {
        'avatar': {'size': (200, 200), 'crop': True},
        'small': {'size': (100, 100), 'crop': True},
    },
}

# ---------------------------------------------------------------------------
# Payment gateways and external APIs
# ---------------------------------------------------------------------------
WOOCOMMERCE_CONSUMER_KEY = config('WOOCOMMERCE_CONSUMER_KEY', default='')
WOOCOMMERCE_CONSUMER_SECRET = config('WOOCOMMERCE_CONSUMER_SECRET', default='')
WOOCOMMERCE_API_URL = config('WOOCOMMERCE_API_URL', default='')

PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID', default='')
PAYPAL_CLIENT_SECRET = config('PAYPAL_CLIENT_SECRET', default='')
PAYPAL_MODE = config('PAYPAL_MODE', default='sandbox')

WOMPI_PUBLIC_KEY = config('WOMPI_PUBLIC_KEY', default='')
WOMPI_PRIVATE_KEY = config('WOMPI_PRIVATE_KEY', default='')
WOMPI_EVENTS_SECRET = config('WOMPI_EVENTS_SECRET', default='')
WOMPI_INTEGRITY_KEY = config('WOMPI_INTEGRITY_KEY', default='')
WOMPI_BASE_URL = config('WOMPI_BASE_URL', default='https://sandbox.wompi.co/v1')
WOMPI_ENVIRONMENT = config('WOMPI_ENVIRONMENT', default='sandbox')

FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:5173')

# ---------------------------------------------------------------------------
# Huey — task queue
# ---------------------------------------------------------------------------
HUEY = RedisHuey(
    name='crushme_project',
    url=config('REDIS_URL', default='redis://localhost:6379/2'),
    immediate=not IS_PRODUCTION,
)

# Destructive seed commands additionally reject production and protected
# database names. This flag is opt-in outside local development and tests.
FAKE_DATA_ALLOWED = config(
    'FAKE_DATA_ALLOWED',
    default=DJANGO_ENV in {'development', 'test', 'e2e'},
    cast=bool,
)
FAKE_DATA_PROTECTED_DATABASES = config(
    'FAKE_DATA_PROTECTED_DATABASES',
    default='crushme,crushme_db,crushme_production',
    cast=Csv(),
)

# ---------------------------------------------------------------------------
# Backups (django-dbbackup)
# ---------------------------------------------------------------------------
# Storage is configured via STORAGES['dbbackup'] above (new-style API).
DBBACKUP_COMPRESS = True
DBBACKUP_CLEANUP_KEEP = 4

# El reporte de queries lentas solo tiene sentido con trafico real.
ENABLE_SLOW_QUERIES_REPORT = config('ENABLE_SLOW_QUERIES_REPORT', default=True, cast=bool)
DBBACKUP_CLEANUP_KEEP_MEDIA = 4

# ==============================================================================
# SILK — query profiling (enabled via ENABLE_SILK env flag)
# ==============================================================================

ENABLE_SILK = config('ENABLE_SILK', default=False, cast=bool)

if ENABLE_SILK:
    INSTALLED_APPS.append('silk')
    MIDDLEWARE.insert(0, 'silk.middleware.SilkyMiddleware')

    SILKY_PYTHON_PROFILER = False
    SILKY_PYTHON_PROFILER_BINARY = False
    SILKY_META = False
    SILKY_ANALYZE_QUERIES = True

    SILKY_AUTHENTICATION = True
    SILKY_AUTHORISATION = True

    def silk_permissions(user):
        return user.is_staff

    SILKY_PERMISSIONS = silk_permissions

    SILKY_MAX_RECORDED_REQUESTS = 10_000
    SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 10
    SILKY_INTERCEPT_PERCENT = 50

    SILKY_IGNORE_PATHS = ['/admin/', '/static/', '/media/', '/silk/']

    SILKY_MAX_REQUEST_BODY_SIZE = 0
    SILKY_MAX_RESPONSE_BODY_SIZE = 0

    SLOW_QUERY_THRESHOLD_MS = 500
    N_PLUS_ONE_THRESHOLD = 10


# ---------------------------------------------------------------------------
# Environment-specific settings (auto-imported)
# ---------------------------------------------------------------------------
if IS_PRODUCTION:
    from .settings_prod import *  # noqa: F401, F403
else:
    from .settings_dev import *  # noqa: F401, F403
