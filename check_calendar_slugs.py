
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Product, Subcategory

with open('slugs_output_utf8.txt', 'w', encoding='utf-8') as f:
    try:
        sub = Subcategory.objects.get(slug='calendarios')
        f.write(f"Subcategory: {sub.name} ({sub.slug})\n")
        products = Product.objects.filter(subcategory=sub)
        for p in products:
            f.write(f" - Product: {p.name}, Slug: {p.slug}\n")
    except Subcategory.DoesNotExist:
        f.write("Subcategory 'calendarios' not found\n")
