import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Category, Subcategory

print(f"Total subcategories: {Subcategory.objects.count()}")
for sub in Subcategory.objects.all()[:5]:
    print(f"Sub: {sub.name}, Cat: {sub.category.name}")
