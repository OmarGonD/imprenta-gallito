import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Category, Product

print(f"Total Products: {Product.objects.count()}")
for cat in Category.objects.all():
    print(f"Category: {cat.name} ({cat.slug}) | Prods: {cat.products.count()}")
