"""
Django settings for BuFuu project.
"""

from pathlib import Path
import os
from django.contrib.messages import constants as messages
import pymysql

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad
SECRET_KEY = 'django-insecure-&$n#fb3&2f+l4w(wrtq1kq!d4yc3e1+dhf#qxmu)pu_5)okucw'
DEBUG = True
ALLOWED_HOSTS = []

# Apps instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.humanize',
    'rest_framework',

    'BuFuuApp',
    'FuuApps2',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'BuFuu.urls'

# Templates
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
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

WSGI_APPLICATION = 'BuFuu.wsgi.application'

# Base de datos - MySQL
pymysql.install_as_MySQLdb()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'DJANGO_TIENDA_3',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',  # o '127.0.0.1'
        'PORT': '3306',
    }
}

# Validación de contraseñas
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

# Internacionalización
LANGUAGE_CODE = 'es-es'
TIME_ZONE = "America/Santiago"   # o 'America/Santiago' si quieres
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Archivos de media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login / Logout redirects
LOGIN_REDIRECT_URL = 'inicio'
LOGOUT_REDIRECT_URL = 'inicio'

# Estilos de mensajes
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}


# settings.py


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR / "sent_emails"

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587  # Puerto estándar para TLS
EMAIL_USE_TLS = True # Usar Transport Layer Security (recomendado)


EMAIL_HOST_USER = 'BuFuuGrowShop@gmail.com' 
EMAIL_HOST_PASSWORD = 'argw eftt icxl fxbl' 
# (IMPORTANTE: ¡NO USAR TU CONTRASEÑA PRINCIPAL!)

# Dirección de correo que aparecerá en el campo "De:"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER



"""
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587 
    EMAIL_USE_TLS = True 
    EMAIL_HOST_USER = 'bufuugrowshop@gmail.com'
    EMAIL_HOST_PASSWORD = 'argw eftt icxl fxbl'
    DEFAULT_FROM_EMAIL = 'bufuugrowshop@gmail.com'
"""