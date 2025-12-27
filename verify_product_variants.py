import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Product, ProductVariant

def check_variants():
    product_slug = 'elevate-men-s-omi-short-sleeve-tech-t-shirt'
    try:
        product = Product.objects.get(slug=product_slug)
        print(f"Product: {product.name}")
    except Product.DoesNotExist:
        print("Product not found")
        return

    variants = product.variant_options.all()
    print(f"Total variants: {variants.count()}")

    for variant in variants:
        print(f"Option: {variant.option.name} (Key: {variant.option.key})")
        values = variant.get_available_values()
        print(f"  Values ({values.count()}):")
        for val in values:
            print(f"    - {val.value} (Display: {val.display_name})")

if __name__ == '__main__':
    check_variants()
