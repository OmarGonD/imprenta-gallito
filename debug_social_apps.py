import os
import django
import sys

# Add project root to sys.path
sys.path.append('d:\\web_proyects\\imprenta_gallito')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

print("--- SITES ---")
for site in Site.objects.all():
    print(f"ID: {site.id}, Domain: {site.domain}, Name: {site.name}")

print("\n--- SOCIAL APPS ---")
apps = SocialApp.objects.all()
if not apps:
    print("No SocialApps found.")
else:
    for app in apps:
        print(f"Provider: {app.provider}, Name: {app.name}, Sites: {list(app.sites.values_list('id', flat=True))}")
