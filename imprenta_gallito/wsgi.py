import os
import sys

# Add your project directory to the sys.path
PROJECT_PATH = "/home/ogonzales/imprenta_gallito"
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

# Django settings module
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "imprenta_gallito.settings"
)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()