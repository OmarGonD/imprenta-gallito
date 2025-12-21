
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Category, Subcategory

try:
    cat = Category.objects.get(slug='calendarios-regalos')
    print(f"Category: {cat.name} ({cat.slug})")
    subs = Subcategory.objects.filter(category=cat)
    for s in subs:
        print(f"  - Subcategory: {s.name}, Slug: '{s.slug}'")
except Category.DoesNotExist:
    print("Category 'calendarios-regalos' not found.")
