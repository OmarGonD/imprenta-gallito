import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Subcategory

subs = Subcategory.objects.all()
count = 0
for s in subs:
    if s.image_url and s.image_url.startswith('/'):
        s.image_url = s.image_url[1:]
        s.save()
        count += 1

print(f"Normalized {count} subcategory image paths (removed leading slash).")
