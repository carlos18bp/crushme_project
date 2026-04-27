"""Django base settings for crushme_project.

Shared settings used by both development and production environments.
Environment-specific overrides are auto-imported at the end of this file
from ``settings_dev.py`` or ``settings_prod.py`` based on the
``DJANGO_ENV`` environment variable.
"""

import os
from datetime import timedelta
from pathlib import Path

from decouple import Csv, config
from huey import RedisHuey

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Environment detection
# ---------------------------------------------------------------------------
DJANGO_ENV = config('DJANGO_ENV', default='development')
IS_PRODUCTION = DJANGO_ENV == 'production'

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

# Allow popups and iframes for payment gateways (PayPal, Wompi)
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Allow iframes from same origin

# Security headers - Allow popups
SECURE_CROSS_ORIGIN_OPENER_POLICY = None  # Allow popups to communicate

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
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=60),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

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
        'backup_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'backups.log',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 3,
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
        'backups': {
            'handlers': ['backup_file', 'console'],
            'level': 'INFO',
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
WOOCOMMERCE_API_URL = 'https://distrisexcolombia.com/wp-json/wc/v3'

PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID', default='')
PAYPAL_CLIENT_SECRET = config('PAYPAL_CLIENT_SECRET', default='')
PAYPAL_MODE = config('PAYPAL_MODE', default='live')

WOMPI_PUBLIC_KEY = config('WOMPI_PUBLIC_KEY', default='')
WOMPI_PRIVATE_KEY = config('WOMPI_PRIVATE_KEY', default='')
WOMPI_EVENTS_SECRET = config('WOMPI_EVENTS_SECRET', default='')
WOMPI_INTEGRITY_KEY = config('WOMPI_INTEGRITY_KEY', default='')
WOMPI_BASE_URL = config('WOMPI_BASE_URL', default='https://production.wompi.co/v1')
WOMPI_ENVIRONMENT = config('WOMPI_ENVIRONMENT', default='production')

FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:5173')

# ---------------------------------------------------------------------------
# Huey — task queue
# ---------------------------------------------------------------------------
HUEY = RedisHuey(
    name='crushme_project',
    url=config('REDIS_URL', default='redis://localhost:6379/2'),
    immediate=not IS_PRODUCTION,
)

# ---------------------------------------------------------------------------
# Backups (django-dbbackup)
# ---------------------------------------------------------------------------
# Storage is configured via STORAGES['dbbackup'] above (new-style API).
DBBACKUP_COMPRESS = True
DBBACKUP_CLEANUP_KEEP = 4

# Backups: permite desactivar la tarea programada en staging via .env
BACKUPS_ENABLED = config('BACKUPS_ENABLED', default=True, cast=bool)
# Slow queries report: solo tiene sentido con tráfico real (desactivar en staging)
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
