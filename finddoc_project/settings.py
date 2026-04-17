# D:\BMI\finddoc_project\settings.py - YAKUNIY VA TUZATILGAN SOZLAMALAR

from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
import dj_database_url
import cloudinary

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-q+0&h8j+p*q-0i1b_2y20(q!+k9_n^0-v61y79b&_n8g5t+c')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

AUTHENTICATION_BACKENDS = [
    'core.backends.EmailOrPhoneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_spectacular',
    'corsheaders',
    
    # Uchinchi tomon ilovalari
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'drf_yasg',
    
    # Loyiha ilovalari
    'core.apps.CoreConfig',
    'cloudinary',
    'cloudinary_storage',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',  # Token Autentifikatsiyasi uchun O'chirildi
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'finddoc_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'finddoc_project.wsgi.application'


# Database
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )
}

# Password validation
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
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


# Static files
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ====================================================================
# CORS SOZLAMALARI
# ====================================================================
CORS_ALLOW_ALL_ORIGINS = True


# ====================================================================
# DRF (Django REST Framework) SOZLAMALARI
# ====================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ]
}

# =========================================================================
# MEDIA FILE CONFIGURATION
# =========================================================================
BASE_DIR_STR = str(BASE_DIR)

SPECTACULAR_SETTINGS = {
    'TITLE': 'FINDDOC API',
    'DESCRIPTION': 'Klinikalar, Shifokorlar va Navbatlarni boshqarish tizimi.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# =========================================================================
# CLOUDINARY SOZLAMALARI (To'g'ri tartibda)
# =========================================================================

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dkdix8nws',
    'API_KEY': '987429467786655',
    'API_SECRET': 'n3Sv0QuiAGUT6zHz0xufP1daU50',
}

# Cloudinary ni asosiy storage sifatida belgilash
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Media URL ni Cloudinary ga yo'naltirish
MEDIA_URL = f"https://res.cloudinary.com/{CLOUDINARY_STORAGE['dkdix8nws']}/"

# Cloudinary konfiguratsiyasi

cloudinary.config(
    cloud_name = CLOUDINARY_STORAGE['dkdix8nws'],
    api_key = CLOUDINARY_STORAGE['987429467786655'],
    api_secret = CLOUDINARY_STORAGE['n3Sv0QuiAGUT6zHz0xufP1daU50']
)

# Cloudinary storage ni INSTALLED_APPS ga qo'shish (allaqachon qo'shilgan)