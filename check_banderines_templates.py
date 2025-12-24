import os
import sys
import django

# Setup Django
sys.path.append(r'D:\web_proyects\imprenta_gallito')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import DesignTemplate, Product

print("="*80)
print("CHECKING BANDERINES TEMPLATES")
print("="*80)

# Check templates for banderines
print("\n1. Checking templates with 'banderines' in path:")
templates = DesignTemplate.objects.filter(thumbnail_url__icontains='banderines')
print(f"   Found {templates.count()} templates")

if templates.count() > 0:
    print("\n   First 5 templates:")
    for t in templates[:5]:
        print(f"   - {t.name}")
        print(f"     URL: {t.thumbnail_url}")
else:
    print("\n2. Checking templates with 'banderas' in path:")
    templates = DesignTemplate.objects.filter(thumbnail_url__icontains='banderas')
    print(f"   Found {templates.count()} templates")
    if templates.count() > 0:
        print("\n   First 5 templates:")
        for t in templates[:5]:
            print(f"   - {t.name}")
            print(f"     URL: {t.thumbnail_url}")
            
print("\n3. Checking for product 'banderines':")
products = Product.objects.filter(slug__icontains='banderin')
print(f"   Found {products.count()} products")
for p in products:
    print(f"   - {p.name} (slug: {p.slug})")
    print(f"     Category: {p.category.slug if p.category else 'None'}")
    print(f"     Subcategory: {p.subcategory.slug if p.subcategory else 'None'}")

print("\n" + "="*80)
