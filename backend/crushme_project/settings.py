import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-n@6c1wwji_s(xko^a!p75$obp5y$(a3hvh9^qixhva755#)otg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'crushme.com.co', 'www.crushme.com.co']

# Cache Configuration
# IMPORTANT: Use Redis in production for webhook data persistence across workers
# Using django-redis for better performance and features
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'crushme',
        'TIMEOUT': 3600,  # 1 hour default
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

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "https://crushme.com.co",
    "https://www.crushme.com.co",
]

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "https://crushme.com.co",
    "https://www.crushme.com.co",
]

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
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'crushme',
        'USER': 'crushme_user',
        'PASSWORD': 'CrushM3_S3cur3_P@ss2025!',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
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
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=60),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Email settings - GoDaddy SMTP Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtpout.secureserver.net'  # GoDaddy SMTP server
EMAIL_PORT = 465  # SSL port for GoDaddy
EMAIL_USE_SSL = True  # GoDaddy uses SSL instead of TLS
EMAIL_HOST_USER = 'support@crushme.com.co'
EMAIL_HOST_PASSWORD = 'cRu$hM3/2025'
DEFAULT_FROM_EMAIL = 'CrushMe Support <support@crushme.com.co>'
SERVER_EMAIL = 'support@crushme.com.co'  # For error emails

# Logging configuration
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
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'crushme_app': {
            'handlers': ['console'],
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

# WooCommerce API settings
WOOCOMMERCE_CONSUMER_KEY = 'ck_2997c6fc6d68b3d998045a33002b2e88cce81682'
WOOCOMMERCE_CONSUMER_SECRET = 'cs_51006180ee1f5999d5cae68d3091e3313174c9c9'
WOOCOMMERCE_API_URL = 'https://desarrollo.distrisex.com/wp-json/wc/v3'

# PayPal API settings
# TODO: Mover estas credenciales a variables de entorno en producción
PAYPAL_CLIENT_ID = 'AXOC4gQsXk_e8NhrrZRorJzU3rld7lOJP5_2S8RYDKUgjkDT-2wfc-1Eu1AqYQseWTcJA_VBEnGUUGCQ'
PAYPAL_CLIENT_SECRET = 'EK58LGYfmckc4T0TKyE7_mMWKWcNW8B47s2fQYqhOLe3_zIOZUiixU11r1LBnIe3P3PTGOLcVTW8NHwG'
PAYPAL_MODE = 'live'  # Cambiar a 'live' en producción

# Wompi API settings (Colombian payment gateway - COP only)
# TODO: Mover estas credenciales a variables de entorno en producción
# Obtener credenciales en: https://comercios.wompi.co/
# Documentación: https://docs.wompi.co/
WOMPI_PUBLIC_KEY = os.environ.get('WOMPI_PUBLIC_KEY', 'pub_test_lHrCKMGf7JVnO4DgnYrdDPgj1DSqJ0OR')
WOMPI_PRIVATE_KEY = os.environ.get('WOMPI_PRIVATE_KEY', 'prv_test_KfwGaDHAt9QikBRArROhTFbUFobB8dnn')
WOMPI_EVENTS_SECRET = os.environ.get('WOMPI_EVENTS_SECRET', 'test_events_yfttSa6ec6puxj8Ld6YTzbzdqY4w47gk')
WOMPI_INTEGRITY_KEY = os.environ.get('WOMPI_INTEGRITY_KEY', 'test_integrity_Zjk5ESr4C6fLn2vH3JA8G2MPTqHIsPy1')  # Para firmar transacciones
WOMPI_BASE_URL = 'https://sandbox.wompi.co/v1'  # Sandbox API para testing
WOMPI_CHECKOUT_URL = 'https://checkout.wompi.co'  # Mismo checkout para sandbox y producción (diferencia por llaves)
WOMPI_ENVIRONMENT = 'test'  # 'test' o 'production'

# Production/Development environment flag
# Set to True in production, False in development
PRODUCTION = True

# Frontend URLs based on environment
if PRODUCTION:
    FRONTEND_URL = 'https://crushme.com.co'
else:
    FRONTEND_URL = 'http://localhost:5173'
