import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Product, ProductImage

def check_images():
    product_slug = 'elevate-men-s-omi-short-sleeve-tech-t-shirt'
    try:
        product = Product.objects.get(slug=product_slug)
        print(f"Product: {product.name} ({product.slug})")
    except Product.DoesNotExist:
        print("Product not found")
        return

    print(f"Base Image URL: {product.base_image_url}")
    
    # Check directly assigned images
    images = product.images.all()
    print(f"Total direct images: {images.count()}")
    
    for img in images:
        val_str = "None"
        if img.option_value:
            val_str = f"{img.option_value.value} ({img.option_value.option.key})"
        
        print(f" - Image ID: {img.id}")
        print(f"   URL: {img.image_url}")
        print(f"   Option Value: {val_str}")
        print(f"   Is Primary: {img.is_primary}")
        print("-" * 20)

if __name__ == '__main__':
    check_images()
