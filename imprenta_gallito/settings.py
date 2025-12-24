import os
from pathlib import Path
from decouple import AutoConfig

# ------------------------------------------------------------------
# BASE
# ------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
config = AutoConfig()

SECRET_KEY = config("SECRET_KEY", default="unsafe-dev-key-change-me")

# ------------------------------------------------------------------
# ENVIRONMENT (PythonAnywhere only)
# ------------------------------------------------------------------

IS_PYTHONANYWHERE = "PYTHONANYWHERE_DOMAIN" in os.environ

if IS_PYTHONANYWHERE:
    DEBUG = False
    ALLOWED_HOSTS = ["ogonzales.pythonanywhere.com"]
else:
    DEBUG = True
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# ------------------------------------------------------------------
# APPLICATIONS
# ------------------------------------------------------------------

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Project apps
    "shop",
    "cart",
    "order",
    "marketing",

    # Utils
    "django.contrib.humanize",
    "crispy_forms",
    "crispy_bootstrap4",

    # Auth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
]

SITE_ID = 1

# ------------------------------------------------------------------
# MIDDLEWARE
# ------------------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# ------------------------------------------------------------------
# URLS / WSGI
# ------------------------------------------------------------------

ROOT_URLCONF = "imprenta_gallito.urls"
WSGI_APPLICATION = "imprenta_gallito.wsgi.application"

# ------------------------------------------------------------------
# TEMPLATES
# ------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "shop.context_processor.menu_links",
                "shop.context_processor.nav_categories",
                "cart.context_processor.cart_items_counter",
            ],
        },
    },
]

# ------------------------------------------------------------------
# DATABASE (SQLite – PythonAnywhere Free)
# ------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ------------------------------------------------------------------
# AUTH / ALLAUTH
# ------------------------------------------------------------------

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/ingresar/"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_AUTHENTICATION_METHOD = "username_email"

# ------------------------------------------------------------------
# INTERNATIONALIZATION
# ------------------------------------------------------------------

LANGUAGE_CODE = "es-pe"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True

# ------------------------------------------------------------------
# STATIC FILES (PythonAnywhere)
# ------------------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

# WHITENOISE_KEEP_ONLY_HASHED_FILES = True  # Disabled with CompressedStaticFilesStorage

# ------------------------------------------------------------------
# MEDIA FILES
# ------------------------------------------------------------------

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ------------------------------------------------------------------
# SECURITY
# ------------------------------------------------------------------

SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
DEBUG_PROPAGATE_EXCEPTIONS = False

# ------------------------------------------------------------------
# EMAIL
# ------------------------------------------------------------------

EMAIL_HOST = config("EMAIL_HOST", default="smtp.example.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

# ------------------------------------------------------------------
# CRISPY
# ------------------------------------------------------------------

CRISPY_TEMPLATE_PACK = "bootstrap4"

# ------------------------------------------------------------------
# FLAGS
# ------------------------------------------------------------------

PACKS3X2 = os.environ.get("PACKS3X2", True)
COMPRESS_ENABLED = os.environ.get("COMPRESS_ENABLED", False)

# ------------------------------------------------------------------
# DEFAULT PK
# ------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
