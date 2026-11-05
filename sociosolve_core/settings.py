"""
Django settings for SocioSolve project.
"""

from pathlib import Path
import os
import urllib.parse
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    'django-insecure-sociosolve-default-dev-key-change-in-production-1234567890'
)

DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

allowed_hosts_str = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',') if host.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # SocioSolve core apps
    'accounts.apps.AccountsConfig',
    'challenges.apps.ChallengesConfig',
    'solutions.apps.SolutionsConfig',
    'collaboration.apps.CollaborationConfig',
    'partnerships.apps.PartnershipsConfig',
    'impact.apps.ImpactConfig',
    'ai_services.apps.AiServicesConfig',
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

ROOT_URLCONF = 'sociosolve_core.urls'

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
                'accounts.context_processors.user_roles_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'sociosolve_core.wsgi.application'

# Database configuration: SQLite default, PostgreSQL if DATABASE_URL is configured
DATABASE_URL = os.getenv('DATABASE_URL', '').strip()

if DATABASE_URL and (DATABASE_URL.startswith('postgres://') or DATABASE_URL.startswith('postgresql://')):
    url = urllib.parse.urlparse(DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': url.path[1:],
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port or 5432,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Authentication URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:dashboard'
LOGOUT_REDIRECT_URL = 'challenges:landing'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files for user-uploaded problem images and avatars
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File upload limits (5MB maximum)
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Mistral AI Service Configurations
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY', '').strip()
MISTRAL_MODEL = os.getenv('MISTRAL_MODEL', 'mistral-small-latest')
MISTRAL_EMBEDDING_MODEL = os.getenv('MISTRAL_EMBEDDING_MODEL', 'mistral-embed')
AI_RATE_LIMIT_PER_USER_PER_HOUR = int(os.getenv('AI_RATE_LIMIT_PER_USER_PER_HOUR', '15'))
