import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Category, Product

with open('dist_output_fixed.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total Products: {Product.objects.count()}\n")
    for cat in Category.objects.all():
        f.write(f"Category: {cat.name} ({cat.slug}) | Prods: {cat.products.count()}\n")
