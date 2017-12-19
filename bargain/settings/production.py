from .base import *
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['.herokuapp.com', 'localhost']
SITE_ID = 3
DATABASES = {'default': dj_database_url.config()}

DEBUG_TOOLBAR_PATCH_SETTINGS = False 

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# STATIC_ROOT = 'staticfiles'

STATIC_ROOT= os.path.join(BASE_DIR,'staticfiles')

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'gbolly_01'
EMAIL_HOST_PASSWORD = 'pastor01'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
