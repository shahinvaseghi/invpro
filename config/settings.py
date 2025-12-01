"""
Base Django settings for the invproj platform.
"""

from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------

env = environ.Env(
    DJANGO_DEBUG=(bool, True),
    DJANGO_ALLOWED_HOSTS=(list, []),
    DJANGO_TIME_ZONE=(str, "UTC"),
)

environ.Env.read_env(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str(
    "DJANGO_SECRET_KEY",
    default="django-insecure-change-me-please",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG")

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]
    
# CSRF Configuration
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read CSRF token if needed
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third-party apps
    'rest_framework',
    'django_filters',
    'corsheaders',

    # Local apps
    'shared',
    'inventory',
    'production',
    'qc',
    'ticketing',
    'accounting',
    'sales',
    'hr',
    'office_automation',
    'transportation',
    'procurement',
    'ui',
]

MIDDLEWARE = [
    'shared.middleware.EditLockCleanupMiddleware',  # Clean up stale edit locks
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
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
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ui.context_processors.active_module',
                'shared.context_processors.active_company',
                'accounting.context_processors.active_fiscal_year',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'fa'

LANGUAGES = [
    ("fa", "Persian"),
    ("en", "English"),
]

TIME_ZONE = env.str("DJANGO_TIME_ZONE")

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Language prefix in URLs
# If False, the default language (fa) won't have a prefix in URLs
# If True, all languages including default will have prefixes (e.g., /fa/, /en/)
# Setting to False means /dashboard/ will be Persian, /en/dashboard/ will be English
USE_L10N = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'shared.User'

# Authentication URLs
LOGIN_URL = '/login/'
# Use '/' to let Django's i18n_patterns handle language prefix automatically
# This respects user's language preference and works with both /fa/ and /en/
LOGIN_REDIRECT_URL = '/'  # Redirect to root, Django will add language prefix automatically
LOGOUT_REDIRECT_URL = '/login/'


# ---------------------------------------------------------------------------
# Django REST framework
# ---------------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
}


# ---------------------------------------------------------------------------
# Session configuration
# ---------------------------------------------------------------------------

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 1 day
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'


# ---------------------------------------------------------------------------
# CORS configuration
# ---------------------------------------------------------------------------

CORS_ALLOW_ALL_ORIGINS = env.bool("DJANGO_CORS_ALLOW_ALL", default=True)
CORS_ALLOWED_ORIGINS = env.list("DJANGO_CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOWED_ORIGIN_REGEXES = env.list("DJANGO_CORS_ALLOWED_ORIGIN_REGEXES", default=[])


# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

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
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'inventory': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'inventory.views': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'inventory.views.master_data': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'inventory.forms': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'inventory.forms.master_data': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
