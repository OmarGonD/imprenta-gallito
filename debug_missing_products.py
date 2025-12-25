import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Product, Category, Subcategory

print(f"Total Products: {Product.objects.count()}")

for cat in Category.objects.all():
    print(f"\nCategory: {cat.name} ({cat.slug}) | Status: {cat.status}")
    active_subcats = cat.subcategories.filter(status='active')
    print(f"  Active Subcategories: {active_subcats.count()}")
    
    # Products with Active Subcategory
    prods_with_active_sub = Product.objects.filter(category=cat, subcategory__in=active_subcats, status='active').count()
    print(f"  Products with Active Subcategory: {prods_with_active_sub}")
    
    # Products with Inactive Subcategory
    inactive_subcats = cat.subcategories.exclude(status='active')
    prods_with_inactive_sub = Product.objects.filter(category=cat, subcategory__in=inactive_subcats, status='active').count()
    print(f"  Products with Inactive Subcategory: {prods_with_inactive_sub}")
    
    # Products without Subcategory
    prods_no_sub = Product.objects.filter(category=cat, subcategory__isnull=True, status='active').count()
    print(f"  Products without Subcategory: {prods_no_sub}")

    if cat.slug == 'tarjetas-presentacion':
        print("  --- Debugging Tarjetas ---")
        for sc in cat.subcategories.all():
            print(f"    Subcat: {sc.name} ({sc.slug}) | Status: {sc.status} | Prods: {sc.products.count()}")
