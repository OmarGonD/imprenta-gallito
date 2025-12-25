import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Product, Subcategory

print("Checking subcategory image cases:")
for sc in Subcategory.objects.filter(status='active')[:10]:
    print(f"Subcat: {sc.name} | Image URL: {sc.image_url}")

print("\nChecking some product image cases:")
for p in Product.objects.filter(status='active')[:10]:
    print(f"Product: {p.name} | Base Image URL: {p.base_image_url}")
