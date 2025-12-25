import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Category, Product

table_names = connection.introspection.table_names()
print("Table Names in DB:")
for name in sorted(table_names):
    print(f" - {name}")

has_categories = 'categories' in table_names or 'shop_category' in table_names
has_products = 'products' in table_names or 'shop_product' in table_names

print(f"\nhas_categories: {has_categories}")
print(f"has_products: {has_products}")

popular_categories = list(Category.objects.filter(
    status='active'
).prefetch_related('subcategories').order_by('display_order')[:6])

print(f"Popular Categories Count: {len(popular_categories)}")
for c in popular_categories:
    print(f" - {c.name} ({c.slug}) | Active Subcats: {c.subcategories.filter(status='active').count()}")

featured_products = list(Product.objects.filter(
    status='active'
).select_related('category').order_by('-created_at')[:6])

print(f"Featured Products Count: {len(featured_products)}")
for p in featured_products:
    print(f" - {p.name} ({p.slug})")
