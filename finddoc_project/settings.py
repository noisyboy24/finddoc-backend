CORS_ALLOW_ALL_ORIGINS = True
# D:\BMI\finddoc_project\settings.py - YAKUNIY VA TUZATILGAN SOZLAMALAR

from pathlib import Path
import os # MEDIA sozlamalari uchun qo'shildi
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-q+0&h8j+p*q-0i1b_2y20(q!+k9_n^0-v61y79b&_n8g5t+c'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']  # Yulduzcha hamma degani


# Application definition

AUTHENTICATION_BACKENDS = [
    'core.backends.EmailOrPhoneBackend', # Biz yozgan yangi logika
    'django.contrib.auth.backends.ModelBackend', # Standart logika (zaxira uchun)
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
    'rest_framework', # DRF asosiy kutubxonasi
    'rest_framework.authtoken', # Token asosida autentifikatsiya
    'django_filters', # Filtrlash uchun (FAQAT BIR MARTA!)
    'drf_yasg', # Swagger/Redoc uchun
    
    # Loyiha ilovalari
    'core.apps.CoreConfig', # core ilovasi
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',  # Token Autentifikatsiyasi uchun O'chirildi
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
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


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
    # MUHIM YANGILANISH: drf-spectacular ni default schema sifatida belgilash
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema', # <<< BU QATORNI QO'SHING
    
    # Filtrlar
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ]
}

# =========================================================================
# MEDIA FILE CONFIGURATION (Rasm va Yuklangan fayllar uchun)
# =========================================================================

# Django yuklangan fayllarni (rasmlar) qaerdan qidirishini aytadi.
# BASE_DIR allaqachon Path obyekti, shuning uchun uni stringga o'giramiz:
BASE_DIR_STR = str(BASE_DIR)

# Yuklangan fayllarni saqlash uchun asosiy URL manzili
MEDIA_URL = '/media/'

# Yuklangan fayllar serverda fizik jihatdan qayerda saqlanishi
MEDIA_ROOT = os.path.join(BASE_DIR_STR, 'media')

SPECTACULAR_SETTINGS = {
    'TITLE': 'FINDDOC API',
    'DESCRIPTION': 'Klinikalar, Shifokorlar va Navbatlarni boshqarish tizimi.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,  # Schema faylini alohida taqdim etish
    # 'SCHEMA_PATH_PREFIX': '/api/', # Bu kerak emas, chunki biz hamma API'larni bog'laymiz
}

import os

# Media fayllar uchun sozlamalar
# Media fayllar saqlanadigan asosiy katalog
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Brauzerda media fayllarga kirish uchun ishlatiladigan URL
MEDIA_URL = '/media/'