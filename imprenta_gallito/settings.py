import os
import secrets
from pathlib import Path
from decouple import AutoConfig  # Use AutoConfig instead of Config

config = AutoConfig()  # Automatically loads the .env file

import dj_database_url
from decouple import config

# SITE_ROOT = root()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!


SECRET_KEY = config('SECRET_KEY', default='your-default-secret-key')
# Remove this line:
# ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# The `DYNO` env var is set on Heroku CI, but it's not a real Heroku app, so we have to
# also explicitly exclude CI:
# https://devcenter.heroku.com/articles/heroku-ci#immutable-environment-variables
IS_HEROKU_APP = "DYNO" in os.environ and not "CI" in os.environ

if IS_HEROKU_APP:
    DEBUG = True
    ALLOWED_HOSTS = ["*"]
else:
    DEBUG = True
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Application definition


INSTALLED_APPS = [
    # Use WhiteNoise's runserver implementation instead of the Django default, for dev-prod parity.
    "whitenoise.runserver_nostatic",
    # Uncomment this and the entry in `urls.py` if you wish to use the Django admin feature:
    # https://docs.djangoproject.com/en/4.2/ref/contrib/admin/
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'shop',
    'cart',
    'order',
    'marketing',
    'django.contrib.humanize',
    'crispy_forms',
    'crispy_bootstrap4',
    'storages',
    'django.contrib.sites',  # Required for allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Django doesn't support serving static assets in a production-ready way, so we use the
    # excellent WhiteNoise package to do so instead. The WhiteNoise middleware must be listed
    # after Django's `SecurityMiddleware` so that security redirects are still performed.
    # See: https://whitenoise.readthedocs.io
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",  # Allauth middleware
]

ROOT_URLCONF = 'imprenta_gallito.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),
                 os.path.join(BASE_DIR, 'shop', 'templates/'),
                 os.path.join(BASE_DIR, 'search_app', 'templates/'),
                 os.path.join(BASE_DIR, 'cart', 'templates/'),
                 os.path.join(BASE_DIR, 'order', 'templates/'), ]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shop.context_processor.menu_links',
                'shop.context_processor.nav_categories',
                #'shop.context_processor.has_shop',
                # 'cart.context_processor.current_time',
                'cart.context_processor.cart_items_counter'
            ],
        },
    },
]

WSGI_APPLICATION = 'imprenta_gallito.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if IS_HEROKU_APP:
    # In production on Heroku the database configuration is derived from the `DATABASE_URL`
    # environment variable by the dj-database-url package. `DATABASE_URL` will be set
    # automatically by Heroku when a database addon is attached to your Heroku app. See:
    # https://devcenter.heroku.com/articles/provisioning-heroku-postgres
    # https://github.com/jazzband/dj-database-url
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('HEROKU_POSTGRESQL_NAME'),
            'USER': config('HEROKU_POSTGRESQL_USER'),
            'PASSWORD': config('HEROKU_POSTGRESQL_PASSWORD'),
            'HOST': config('HEROKU_POSTGRESQL_HOST'),
            'PORT': config('HEROKU_POSTGRESQL_PORT'),
        }
    }

else:
    # When running locally in development or in CI, a sqlite database file will be used instead
    # to simplify initial setup. Longer term it's recommended to use Postgres locally too.
    SECURE_SSL_REDIRECT = False

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }

    }

### HEROKU POSTGRESS ACCESS
# DATABASES = {
#    'default': {
#       'ENGINE': 'django.db.backends.postgresql',
#        'NAME': config('HEROKU_POSTGRESQL_NAME'),
#        'USER': config('HEROKU_POSTGRESQL_USER'),
#        'PASSWORD': config('HEROKU_POSTGRESQL_PASSWORD'),
#        'HOST': config('HEROKU_POSTGRESQL_HOST'),
#        'PORT': config('HEROKU_POSTGRESQL_PORT'),
#    }
# }


####

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# Allauth Settings
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/ingresar/'

# Social Account Providers config (optional, keys usually in DB)
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'name',
            'name_format',
            'picture',
            'short_name'
        ],
        'EXCHANGE_TOKEN': True,
        'VERIFIED_EMAIL': False,
        'VERSION': 'v13.0',
    }
}

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

LANGUAGE_CODE = 'es-PE'

TIME_ZONE = 'UTC'

USE_THOUSAND_SEPARATOR = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Ensure this points to your static directory
]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {  # <-- this key must be 'staticfiles'
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Don't store the original (un-hashed filename) version of static files, to reduce slug size:
# https://whitenoise.readthedocs.io/en/latest/django.html#WHITENOISE_KEEP_ONLY_HASHED_FILES
WHITENOISE_KEEP_ONLY_HASHED_FILES = True

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

### Acaba Heroku Docs

# MEDIAFILES_LOCATION = 'media'

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'static', 'media')


CRISPY_TEMPLATE_PACK = 'bootstrap4'


### AMAZON ###


AWS_S3_OBJECT_PARAMETERS = {
    'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
    'CacheControl': 'max-age=94608000',
}

# AWS_STORAGE_BUCKET_NAME = ''#os.environ['AWS_STORAGE_BUCKET_NAME']
# AWS_S3_REGION_NAME = 'os'#os.environ['AWS_S3_REGION_NAME']
# Tell django-storages the domain to use to refer to static files.
# AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

# AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
# AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']


### MAILGUN - EMAIL MESSAGE SETTINGS ###

EMAIL_HOST = config('EMAIL_HOST', default='smtp.example.com')  # Placeholder for email host
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)  # Placeholder for email port
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)  # Placeholder for TLS setting
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='user@example.com')  # Placeholder for email user
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='password')  # Placeholder for email password

### BREVO CONFIGURATION ###
BREVO_API_KEY = config('BREVO_API_KEY', default='YOUR_BREVO_API_KEY')
BREVO_SENDER_EMAIL = config('BREVO_SENDER_EMAIL', default='imprentagallito@imprentagallito.pe') # Use a valid verified sender
BREVO_SENDER_NAME = config('BREVO_SENDER_NAME', default='Imprenta Gallito')

### manage.py check --deploy

SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

### Promociones ###

PACKS3X2 = os.environ.get('PACKS3X2', True)  # Replace 'default_value' with an appropriate placeholder

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] ' +
                       'pathname=%(pathname)s lineno=%(lineno)s ' +
                       'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'testlogger': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

DEBUG_PROPAGATE_EXCEPTIONS = False
COMPRESS_ENABLED = os.environ.get('COMPRESS_ENABLED', False)
