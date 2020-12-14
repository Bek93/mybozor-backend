from .base import *
from decouple import config
DEBUG = True
ALLOWED_HOSTS = ['*']

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': ''
    }
}

STRIPE_PUBLIC_KEY = ''
STRIPE_SECRET_KEY = ''

