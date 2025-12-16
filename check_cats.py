import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Category

print(f"Total categories: {Category.objects.count()}")
for cat in Category.objects.all():
    print(f"Name: {cat.name}, Slug: {cat.slug}, Status: {cat.status}")
