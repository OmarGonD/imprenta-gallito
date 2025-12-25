import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Category, Product

table_names = connection.introspection.table_names()

with open('view_logic_output_fixed.txt', 'w', encoding='utf-8') as f:
    f.write("Table Names in DB:\n")
    for name in sorted(table_names):
        f.write(f" - {name}\n")

    has_categories = 'categories' in table_names or 'shop_category' in table_names
    has_products = 'products' in table_names or 'shop_product' in table_names

    f.write(f"\nhas_categories: {has_categories}\n")
    f.write(f"has_products: {has_products}\n")

    popular_categories = list(Category.objects.filter(
        status='active'
    ).prefetch_related('subcategories').order_by('display_order')[:6])

    f.write(f"Popular Categories Count: {len(popular_categories)}\n")
    for c in popular_categories:
        f.write(f" - {c.name} ({c.slug}) | Active Subcats: {c.subcategories.filter(status='active').count()}\n")

    featured_products = list(Product.objects.filter(
        status='active'
    ).select_related('category').order_by('-created_at')[:6])

    f.write(f"Featured Products Count: {len(featured_products)}\n")
    for p in featured_products:
        f.write(f" - {p.name} ({p.slug})\n")
