import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Product, Subcategory

with open('image_cases_output.txt', 'w', encoding='utf-8') as f:
    f.write("Checking subcategory image cases:\n")
    for sc in Subcategory.objects.filter(status='active')[:20]:
        f.write(f"Subcat: {sc.name} | Image URL: {sc.image_url}\n")

    f.write("\nChecking some product image cases:\n")
    for p in Product.objects.filter(status='active', subcategory__slug='bolsas-regalo')[:10]:
        f.write(f"Product: {p.name} | Base Image URL: {p.base_image_url}\n")
