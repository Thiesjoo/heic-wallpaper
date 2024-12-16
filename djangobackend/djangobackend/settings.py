"""
Django settings for djangobackend project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

class S3Config:
    def __init__(self, name):
        self.name = name
        self.S3_URL = os.environ.get(f"{name}_S3_URL")
        self.BUCKET = os.environ.get(f"{name}_S3_BUCKET")
        self.S3_ACCESS_KEY = os.environ.get(f"{name}_S3_ACCESS_KEY")
        self.S3_SECRET_KEY = os.environ.get(f"{name}_S3_SECRET_KEY")
        self.S3_REGION = os.environ.get(f"{name}_S3_REGION") or "eu-central-003"

class AppConfig:
    UPLOAD = S3Config("UPLOAD")
    RESULT = S3Config("RESULT")

    PUBLIC_URL = os.environ.get("PUBLIC_URL")
    PUBLIC_ASSET_URL = os.environ.get("PUBLIC_ASSET_URL")
    AUTHENTIK_TOKEN = os.environ.get("AUTHENTIK_TOKEN")
    AUTHENTIK_API_URL = os.environ.get("AUTHENTIK_API_URL")
    AUTHENTIK_CLIENT_ID = os.environ.get("AUTHENTIK_CLIENT_ID")

    @staticmethod
    def validate():
        for s3 in [AppConfig.UPLOAD, AppConfig.RESULT]:
            for attr in ["S3_URL", "BUCKET", "S3_ACCESS_KEY", "S3_SECRET_KEY"]:
                if getattr(s3, attr) is None:
                    raise ValueError(f"{attr} is required for {s3.name}")
        if AppConfig.PUBLIC_URL is None:
            raise ValueError("PUBLIC_URL is required")
        if AppConfig.PUBLIC_ASSET_URL is None:
            raise ValueError("PUBLIC_ASSET_URL is required")
        if AppConfig.AUTHENTIK_TOKEN is None:
            raise ValueError("AUTHENTIK_TOKEN is required")
        if AppConfig.AUTHENTIK_API_URL is None:
            raise ValueError("AUTHENTIK_API_URL is required")

AppConfig.validate()
CONFIG = AppConfig()

CELERY_BROKER_URL = os.environ.get("BROKER_URL")
CELERY_RESULT_BACKEND = os.environ.get("BROKER_URL")

if CELERY_BROKER_URL is None or CELERY_RESULT_BACKEND is None:
    raise ValueError("BROKER_URL and BROKER_URL are required")

DEBUG = os.environ.get("DEV") == "true"

MAX_AGE_FOR_PENDING_WALLPAPERS = timedelta(hours=1)  # 1h
CLEANUP_INTERVAL_FOR_PENDING_WALLPAPERS = 30 if DEBUG else 60 * 60 * 12


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
SECRET_KEY = os.environ.get("SECRET_KEY")


if DEBUG:
    ALLOWED_HOSTS = []
else:
    CSRF_COOKIE_SECURE = True
    ALLOWED_HOSTS = [
        "wallpaper.thies.dev"
    ]


# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django_filters',
    'rest_framework',
    'core',
    'api'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'djangobackend.urls'

TEMPLATES = []

AUTHENTICATION_BACKENDS = []

WSGI_APPLICATION = 'djangobackend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DB_NAME = os.environ.get("DB_NAME")
DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT = os.environ.get("DB_PORT") or 5432


if (not (DB_USER and DB_PASSWORD and DB_HOST and DB_NAME)):
    raise ValueError("Please specify db creds")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'HOST': DB_HOST,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'PORT': DB_PORT
    }
}

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'core.authentication.AuthViaAuthentik',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'djangobackend.pagination.CustomPagination',
    'PAGE_SIZE': 100,
    'ORDERING_PARAM': 'sort'
}

AUTH_USER_MODEL = 'core.User'