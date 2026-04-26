"""Development-specific settings for crushme_project.

Imported automatically by ``settings.py`` when ``DJANGO_ENV != 'production'``.
"""

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
