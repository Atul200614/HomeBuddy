"""
Django settings for HomeBuddy project.
TYBSc Computer Science Mini Project — Atul Patel
Stack: Python + Django + MySQL + Bootstrap 5

Security model
--------------
* Secrets come from the environment (.env). Nothing sensitive is committed.
* DEBUG defaults to False (secure by default) and must be opted into.
* Cookies, HSTS and SSL redirect are enabled automatically when DEBUG=False.
* CORS is an explicit allow-list, never '*'.
"""

import os
from decimal import Decimal
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Detect Vercel serverless environment reliably
IS_VERCEL = os.path.exists('/var/task') or bool(os.environ.get('VERCEL'))

# Load environment variables from .env (never committed to version control)
load_dotenv(BASE_DIR / '.env')


def env_bool(name, default=False):
    """Read a boolean environment variable with a sane default."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {'1', 'true', 'yes', 'on'}


def env_list(name, default=''):
    """Read a comma separated environment variable into a list."""
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(',') if item.strip()]


# ---------------------------------------------------------------------------
# Core security
# ---------------------------------------------------------------------------
DEBUG = env_bool('DEBUG', False)

SECRET_KEY = os.getenv('SECRET_KEY', '').strip()
if not SECRET_KEY:
    if DEBUG:
        # Development-only fallback so a fresh clone can boot without a .env
        SECRET_KEY = 'django-insecure-dev-only-homebuddy-never-use-in-production'
    else:
        raise ImproperlyConfigured(
            "SECRET_KEY is not set. Create your .env file first:\n"
            "    cp .env.example .env\n"
            "then set SECRET_KEY to a long random string.\n"
            "Generate one with:\n"
            "    python -c \"import secrets; print(secrets.token_urlsafe(64))\""
        )

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', '.vercel.app,localhost,127.0.0.1,[::1]')

CSRF_TRUSTED_ORIGINS = env_list(
    'CSRF_TRUSTED_ORIGINS',
    'https://*.vercel.app,http://localhost:8000,http://127.0.0.1:8000',
)

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.humanize',

    # Third-party apps
    'corsheaders',
    'rest_framework',

    # HomeBuddy domain applications
    'apps.core',
    'apps.accounts',
    'apps.customers',
    'apps.professionals',
    'apps.services',
    'apps.bookings',
    'apps.payments',
    'apps.reviews',
    'apps.complaints',
    'apps.messaging',
    'apps.notifications',
    'apps.admin_dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'apps.core.context_processors.global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# ---------------------------------------------------------------------------
# Database: MySQL 8.0 by default, SQLite fallback (writable /tmp on Vercel)
# ---------------------------------------------------------------------------
DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite').lower()
USE_SQLITE_FALLBACK = env_bool('USE_SQLITE_FALLBACK', True)

if DB_ENGINE == 'mysql' and not USE_SQLITE_FALLBACK and not IS_VERCEL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'homebuddy_db'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/db.sqlite3' if IS_VERCEL else BASE_DIR / 'homebuddy.sqlite3',
        }
    }

# Custom User Model (Accounts app)
AUTH_USER_MODEL = 'accounts.User'

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:role_redirect'
LOGOUT_REDIRECT_URL = 'core:home'

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media
# ---------------------------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/tmp/media' if IS_VERCEL else BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Upload guard rails (KYC docs, work proof photos, avatars)
MAX_UPLOAD_SIZE_MB = int(os.getenv('MAX_UPLOAD_SIZE_MB', '5'))
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# ---------------------------------------------------------------------------
# Messages -> Bootstrap 5 alert classes
# ---------------------------------------------------------------------------
from django.contrib.messages import constants as messages  # noqa: E402

MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# ---------------------------------------------------------------------------
# REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/hour',
        'user': '1000/hour',
    },
}

# ---------------------------------------------------------------------------
# CORS — explicit allow-list
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env_list(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000',
)
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Razorpay (test mode)
# ---------------------------------------------------------------------------
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '').strip()
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '').strip()
RAZORPAY_WEBHOOK_SECRET = os.getenv('RAZORPAY_WEBHOOK_SECRET', '').strip()
RAZORPAY_CURRENCY = os.getenv('RAZORPAY_CURRENCY', 'INR').strip() or 'INR'

RAZORPAY_DEMO_MODE = env_bool(
    'RAZORPAY_DEMO_MODE',
    not (RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET),
)

# Platform business rules
PLATFORM_COMMISSION_RATE = Decimal(os.getenv('PLATFORM_COMMISSION_RATE', '10.00'))
MIN_PAYOUT_AMOUNT = Decimal(os.getenv('MIN_PAYOUT_AMOUNT', '100.00'))

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'no-reply@homebuddy.local')
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)

# ---------------------------------------------------------------------------
# Caching & logging
# ---------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'homebuddy-cache',
        'TIMEOUT': 300,
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
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
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'homebuddy': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ---------------------------------------------------------------------------
# Hardening (active whenever DEBUG is off)
# ---------------------------------------------------------------------------
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 60 * 60 * 12  # 12 hours

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', False if IS_VERCEL else True)
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Admin branding
ADMIN_SITE_HEADER = 'HomeBuddy Platform Administration'
ADMIN_SITE_TITLE = 'HomeBuddy Admin'
ADMIN_INDEX_TITLE = 'Marketplace Operations'