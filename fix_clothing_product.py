import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Product, ProductOption, ProductOptionValue, ProductVariant, ProductImage
from django.conf import settings

def fix_product():
    product_slug = 'elevate-men-s-omi-short-sleeve-tech-t-shirt'
    try:
        product = Product.objects.get(slug=product_slug)
        print(f"✅ Found product: {product.name}")
    except Product.DoesNotExist:
        print(f"❌ Product not found: {product_slug}")
        return

    # 1. DELETE EXISTING CORRUPTED DATA
    print("🧹 Clearing existing variants and images...")
    product.images.all().delete()
    product.variant_options.all().delete()
    
    # 2. LOCATE IMAGES IN FILESYSTEM
    base_dir = os.path.join(settings.BASE_DIR, 'static', 'media', 'product_images', 'ropa_y_bolsos', 'polos_hombre')
    print(f"📂 Scanning directory: {base_dir}")
    
    found_files = []
    prefix = product_slug + "-"
    
    if os.path.exists(base_dir):
        for f in os.listdir(base_dir):
            if f.startswith(prefix) and f.lower().endswith('.jpg'):
                found_files.append(f)
    
    print(f"📸 Found {len(found_files)} images matching product prefix.")

    # 3. IDENTIFY COLORS AND PREPARE DATA
    # Map extracted color slug to (Display Name, Hex Code)
    color_map_info = {
        'azul-marino': ('Azul Marino', '#000080'),
        'azul-real': ('Azul Real', '#4169E1'),
        'blanco': ('Blanco', '#FFFFFF'),
        'gris': ('Gris', '#9E9E9E'),
        'naranja': ('Naranja', '#FFA500'),
        'negro': ('Negro', '#000000'),
        'rojo': ('Rojo', '#FF0000'),
        'sky': ('Cielo', '#87CEEB'),
        # Fallbacks just in case
        'verde': ('Verde', '#008000'),
        'morado': ('Morado', '#800080'),
    }

    # Get Color Option
    color_option, _ = ProductOption.objects.get_or_create(
        key='color',
        defaults={'name': 'Color', 'selection_type': 'single'}
    )
    
    # Lists to hold the new objects
    new_images = []
    color_values_for_variant = []

    # Process each file
    for filename in sorted(found_files):
        # Extract color: "prefix-color.jpg" -> "color"
        color_slug = filename[len(prefix):-4] # Remove prefix and .jpg
        
        # Safety check: if filename is weird
        if not color_slug:
            continue
            
        print(f"   Processing color: {color_slug}")
        
        info = color_map_info.get(color_slug, (color_slug.title(), '#CCCCCC'))
        display_name, hex_code = info
        
        # Get or Create Option Value
        pov, created = ProductOptionValue.objects.get_or_create(
            option=color_option,
            value=color_slug,
            defaults={
                'display_name': display_name,
                'hex_code': hex_code
            }
        )
        if created:
            print(f"      Created new color value: {color_slug}")
        
        # Update hex code if it was missing or default
        if pov.hex_code == '#CCCCCC' and hex_code != '#CCCCCC':
             pov.hex_code = hex_code
             pov.display_name = display_name
             pov.save()

        if pov not in color_values_for_variant:
            color_values_for_variant.append(pov)
            
        # Create Image
        # Path logic: static/media/... -> media/... (Django stores relative to MEDIA_ROOT)
        # Assuming existing structure stores "media/..." or fully relative paths.
        # The view often prepends /static/ if not present, but let's follow existing patterns.
        # Looking at verify output: "media/product_images/..."
        
        image_url = f"media/product_images/ropa_y_bolsos/polos_hombre/{filename}"
        
        # Set primary image? Maybe the first one or 'negro'/'gris' as default
        is_primary = False
        if color_slug == 'gris': # Requested in prompt as the one being checked
            is_primary = True
            # Update base image url of product too
            product.base_image_url = image_url
            product.save()

        ProductImage.objects.create(
            product=product,
            option_value=pov,
            image_url=image_url,
            is_primary=is_primary,
            display_order=0
        )

    # 4. CREATE VARIANT LINKING COLORS
    if color_values_for_variant:
        variant = ProductVariant.objects.create(
            product=product,
            option=color_option
        )
        variant.available_values.set(color_values_for_variant)
        print(f"✅ Created 'Color' variant with {len(color_values_for_variant)} values.")
    
    
    # 5. RESTORE SIZE VARIANT (It was deleted too!)
    # We should add back standard sizes
    size_option, _ = ProductOption.objects.get_or_create(key='size', defaults={'name': 'Talla'})
    standard_sizes = ['S', 'M', 'L', 'XL']
    
    size_values = []
    for s in standard_sizes:
        val, _ = ProductOptionValue.objects.get_or_create(
            option=size_option, 
            value=s,
            defaults={'display_name': s}
        )
        size_values.append(val)
        
    size_variant = ProductVariant.objects.create(
        product=product,
        option=size_option
    )
    size_variant.available_values.set(size_values)
    print("✅ Restored 'Size' variant (S, M, L, XL).")

    print("\n🎉 Fix Complete!")

if __name__ == '__main__':
    fix_product()
