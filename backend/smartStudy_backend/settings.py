import os
import sys
from pathlib import Path

from celery.schedules import crontab
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security & Debug
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2'
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.postgres',
    'django_extensions',
    'corsheaders',
    'rest_framework',
    'social_django',
    'sslserver',
    'channels',
    'silk',

    'core',
    'users',
    'courses',
    'users_calendar',
    'notifications',
]

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(os.getenv('REDIS_HOST'), int(os.getenv('REDIS_PORT')))],
            'password': os.getenv('REDIS_PASSWORD', ''),
        },
    },
}

# Middleware
MIDDLEWARE = [
    "silk.middleware.SilkyMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'common.middleware.LanguageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'common.middleware.RateLimitMiddleware',
    'common.middleware.SessionSecurityMiddleware',
    'common.middleware.SecurityHeadersMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://localhost:5173",
    "http://127.0.0.1:5173",
    "https://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = [
    'content-type',
    'content-disposition',
    'etag',
    'last-modified',
]

from corsheaders.defaults import default_headers

CORS_ALLOW_HEADERS = list(default_headers) + [
    'if-none-match',
    'if-modified-since',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

# URLs & WSGI
ROOT_URLCONF = 'smartStudy_backend.urls'
WSGI_APPLICATION = 'smartStudy_backend.wsgi.application'
ASGI_APPLICATION = 'smartStudy_backend.asgi.application'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# Database
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE'),
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),

        'CONN_MAX_AGE': 60,
    }
}

# Cache Configuration
CACHES = {
    "default": {  # for user and auth
        "BACKEND": os.getenv("BACKEND"),
        "LOCATION": f"redis://:{os.getenv('REDIS_PASSWORD', '')}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/0",
        "OPTIONS": {
            "CLIENT_CLASS": os.getenv("CLIENT_CLASS"),
            "IGNORE_EXCEPTIONS": True,
        }
    },
    "sessions": {
        "BACKEND": os.getenv("BACKEND"),
        "LOCATION": f"redis://:{os.getenv('REDIS_PASSWORD', '')}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/1",
        "OPTIONS": {
            "CLIENT_CLASS": os.getenv("CLIENT_CLASS"),
            "IGNORE_EXCEPTIONS": True,
        }
    },
    "courses_get": {
        "BACKEND": os.getenv("BACKEND"),
        "LOCATION": f"redis://:{os.getenv('REDIS_PASSWORD', '')}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/2",
        "OPTIONS": {
            "CLIENT_CLASS": os.getenv("CLIENT_CLASS"),
            "IGNORE_EXCEPTIONS": True,
        }
    },
    "calendar_events": {
        "BACKEND": os.getenv("BACKEND"),
        "LOCATION": f"redis://:{os.getenv('REDIS_PASSWORD', '')}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/3",
        "OPTIONS": {
            "CLIENT_CLASS": os.getenv("CLIENT_CLASS"),
            "IGNORE_EXCEPTIONS": True,
        }
    },
    "public_tests_get": {
        "BACKEND": os.getenv("BACKEND"),
        "LOCATION": f"redis://:{os.getenv('REDIS_PASSWORD', '')}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/4",
        "OPTIONS": {
            "CLIENT_CLASS": os.getenv("CLIENT_CLASS"),
            "IGNORE_EXCEPTIONS": True,
        }
    },
}

MONGO_URI = os.getenv('MONGO_DB_URI')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
SUPABASE_USERS_PROFILE_PICTURES_BUCKET = os.getenv("SUPABASE_USERS_PROFILE_PICTURES_BUCKET")
SUPABASE_COURSES_COVER_PICTURES_BUCKET = os.getenv("SUPABASE_COURSES_COVER_PICTURES_BUCKET")

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "sessions"

# Authentication
AUTH_USER_MODEL = 'users.CustomUser'
LOGIN_REDIRECT_URL = '/'

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

# Internationalization & Localization
LANGUAGES = [
    ('en', 'English'),
    ('uk', 'Українська'),
]

LANGUAGE_CODE = 'en'
TIME_ZONE = 'Europe/Kiev'

USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

CSRF_TRUSTED_ORIGINS = [
    'https://localhost:5173',
    'https://localhost:8000',
    'https://127.0.0.1:5173',
    'https://127.0.0.1:8000',
]

CELERY_BEAT_SCHEDULE = {
    'train-ml-model-every-night': {
        'task': 'courses.tasks.train_course_recommendations',
        'schedule': crontab(hour=3, minute=0),
    },
    'daily-morning-reminder': {
        'task': 'notifications.tasks.send_daily_reminders_task',
        'schedule': crontab(hour=15, minute=42),
    },
}

# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

# Defaults
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# HTTPS & Security Settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
else:
    SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('GOOGLE_CLIENT_ID')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email', 'profile']

SOCIAL_AUTH_FACEBOOK_KEY = os.getenv('FACEBOOK_APP_ID')
SOCIAL_AUTH_FACEBOOK_SECRET = os.getenv('FACEBOOK_APP_SECRET')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'public_profile']

CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_NAME = 'csrftoken'

BASE_URL = 'https://127.0.0.1:8000'
DEFAULT_FROM_EMAIL = 'noreply@smartstudy.com'
FRONTEND_URL = "https://localhost:5173"
ALLOWED_ROLES = ['admin', 'student', 'teacher']

SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = False

LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 365 * 24 * 60 * 60
LANGUAGE_COOKIE_PATH = '/'
LANGUAGE_COOKIE_SECURE = SESSION_COOKIE_SECURE
LANGUAGE_COOKIE_SAMESITE = 'Lax'

TESTING = 'test' in sys.argv or 'pytest' in sys.modules

if TESTING:
    SUPABASE_USERS_PROFILE_PICTURES_BUCKET = os.getenv("SUPABASE_BUCKET")

    MIDDLEWARE = [
        m for m in MIDDLEWARE
        if not any(skip in m.lower() for skip in ['silk'])
    ]

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'test_smartstudy',
            'USER': 'test_user',
            'PASSWORD': 'test_pass',
            'HOST': 'localhost',
            'PORT': '5433',
            'TEST': {
                'NAME': 'test_smartstudy_test',
            }
        }
    }

# CELERY SETTINGS
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Kiev'
