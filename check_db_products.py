import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Product, Category, Subcategory

print(f"Total Products: {Product.objects.count()}")
print(f"Active Products: {Product.objects.filter(status='active').count()}")
print(f"Inactive Products: {Product.objects.filter(status='inactive').count()}")

print("\n--- Categories Status ---")
for c in Category.objects.all():
    print(f"Category: {c.name} ({c.slug}) | Status: {c.status} | Products: {c.products.count()} | Active Subcats: {c.subcategories.filter(status='active').count()}")

print("\n--- All Subcategories ---")
for sc in Subcategory.objects.all():
    print(f"Subcat: {sc.name} ({sc.slug}) | Status: {sc.status} | Active Prods: {sc.products.filter(status='active').count()}")

# Check one random product's absolute URL logic
p = Product.objects.filter(status='active').first()
if p:
    print(f"\n--- URL Check ---")
    print(f"Product: {p.name}")
    print(f"Cat Slug: {p.category_id}")
    print(f"Subcat Slug: {p.subcategory_id if p.subcategory else 'None'}")
    try:
        print(f"Absolute URL: {p.get_absolute_url()}")
    except Exception as e:
        print(f"Error getting URL: {e}")
