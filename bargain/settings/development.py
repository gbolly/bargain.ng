from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SITE_ID = 3

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bargain',
        'USER': 'bargain',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}

STATIC_ROOT = 'staticfiles'

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'gbolly_01'
EMAIL_HOST_PASSWORD = 'notreal-forsmallmanofGodlevel1'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
