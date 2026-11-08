"""
Django settings for the ALI TRAVEL backend.

Everything that differs between a laptop and a live server comes from environment variables, or from a `backend/.env` file
(see `.env.example`). With no variables set the site runs in development mode exactly as before.
"""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_file(path):
    """Read KEY=value lines from a .env file without overriding variables that are already set."""
    if not path.exists():
        return
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file(BASE_DIR / '.env')


def env(name, default=''):
    return os.environ.get(name, default)


def env_bool(name, default=False):
    return env(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


def env_list(name, default=''):
    return [item.strip() for item in env(name, default).split(',') if item.strip()]


DEBUG = env_bool('DEBUG', True)

_DEV_SECRET = 'django-insecure-t2jrayn*0bd45gthe+e%b&c(temylmdp)&#v8*!v8j&j&p78#i'
SECRET_KEY = env('SECRET_KEY', _DEV_SECRET)
if not DEBUG and SECRET_KEY == _DEV_SECRET:
    raise ImproperlyConfigured('Set a private SECRET_KEY in the environment before running with DEBUG=false.')

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1' if DEBUG else '')
if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured('Set ALLOWED_HOSTS (comma-separated domain names) when DEBUG is false.')

# The public address of the website (used in e-mails, the sitemap and links back to the site).
SITE_URL = env('SITE_URL', 'http://localhost:5173').rstrip('/')


# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'api',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'api.market.MarketMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database: SQLite by default; set DB_NAME (and DB_USER, DB_PASSWORD, DB_HOST, DB_PORT) to use PostgreSQL (needs `pip install psycopg[binary]`).
if env('DB_NAME'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST', 'localhost'),
            'PORT': env('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


# E-mail: printed to the console until EMAIL_HOST is set; then sent through that SMTP server.
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', 'ALI TRAVEL <alitravel004@gmail.com>')
SERVER_EMAIL = DEFAULT_FROM_EMAIL
if env('EMAIL_HOST'):
    _use_ssl = env_bool('EMAIL_USE_SSL', False)
    MAILERS = {
        'default': {
            'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'OPTIONS': {
                'host': env('EMAIL_HOST'),
                'port': int(env('EMAIL_PORT', '465' if _use_ssl else '587')),
                'username': env('EMAIL_HOST_USER'),
                'password': env('EMAIL_HOST_PASSWORD'),
                'use_tls': env_bool('EMAIL_USE_TLS', not _use_ssl),
                'use_ssl': _use_ssl,
                'timeout': 10,
            },
        },
    }
else:
    MAILERS = {'default': {'BACKEND': 'django.core.mail.backends.console.EmailBackend'}}

# Who is told about new bookings, messages and reviews (defaults to the site e-mail), and the optional Telegram bot.
NOTIFY_EMAILS = env_list('NOTIFY_EMAILS', 'alitravel004@gmail.com')

# Octo payments for the booking deposit (api/payments.py). Empty = test mode: no money moves.
OCTO_SHOP_ID = env('OCTO_SHOP_ID', '')
OCTO_SECRET = env('OCTO_SECRET', '')
OCTO_UNIQUE_KEY = env('OCTO_UNIQUE_KEY', '')   # signs Octo's payment notifications
OCTO_TEST = env_bool('OCTO_TEST', False)       # true: Octo's own test transactions
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = env('TELEGRAM_CHAT_ID')  # optional extra chat; normally leave empty
# Telegram accounts that receive the team alerts. Only these accounts (and nobody else who talks to the bot) are told about
# bookings. Each one must open the bot once and press Start so that Telegram lets the bot write to them.
TELEGRAM_TEAM_USERNAMES = env_list('TELEGRAM_TEAM_USERNAMES', 'Al1_travel')
NOTIFY_ASYNC = env_bool('NOTIFY_ASYNC', True)  # send in the background so a slow mail server never delays a booking

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.TokenAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    # Number of reverse proxies (nginx) in front of Django. Rate limits then use the visitor's own address from X-Forwarded-For;
    # without it every visitor behind nginx would look like 127.0.0.1 and share one limit.
    'NUM_PROXIES': int(env('NUM_PROXIES', '0' if DEBUG else '1')),
}

CORS_ALLOWED_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173'] + env_list('CORS_ORIGINS')
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')

# Let Django give out the built website (frontend/dist) and the uploaded photos itself: one process is then enough on a small server.
# Default: on when DEBUG is off. Set SERVE_FRONTEND=false when nginx serves those files.
SERVE_FRONTEND = env_bool('SERVE_FRONTEND', not DEBUG)
FRONTEND_DIST = Path(env('FRONTEND_DIST', str(BASE_DIR.parent / 'frontend' / 'dist')))

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
X_FRAME_OPTIONS = 'SAMEORIGIN'

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(env('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_CONTENT_TYPE_NOSNIFF = True
