import os
import django
import pandas as pd
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Product, ProductOption, ProductOptionValue, ProductVariant, ProductImage

def fix_swatches():
    print("Starting swatch data fix...")
    
    # 1. Ensure 'color' option exists
    color_option, _ = ProductOption.objects.get_or_create(
        key='color',
        defaults={'name': 'Color', 'display_order': 1}
    )
    
    # 2. Read the mapping file
    filepath = 'static/data/polo_imagenes_colores.xlsx'
    if not os.path.exists(filepath):
        print(f"File {filepath} not found!")
        return
    
    df = pd.read_excel(filepath)
    print(f"Processing {len(df)} mapping rows...")
    
    updated_products = set()
    created_images = 0
    
    for _, row in df.iterrows():
        base_slug = str(row.get('product_slug', '')).strip()
        color_slug = str(row.get('color_slug', '')).strip()
        image_url = str(row.get('image_url', '')).strip()
        is_primary = str(row.get('is_primary', 'False')).lower() == 'true'
        display_order = int(row.get('display_order', 0))
        
        if not base_slug or not color_slug:
            continue
            
        # Find all products that match this base slug (exact or as prefix)
        from django.db.models import Q
        products = Product.objects.filter(Q(slug=base_slug) | Q(slug__startswith=base_slug + "-"))
        
        if not products.exists():
            continue
            
        # Ensure the color value exists
        color_val, _ = ProductOptionValue.objects.get_or_create(
            option=color_option,
            value=color_slug,
            defaults={
                'display_name': color_slug.replace('-', ' ').title(),
                'hex_code': '#CCCCCC',
                'is_active': True
            }
        )
        
        for product in products:
            # Associate color with product variant
            variant, _ = ProductVariant.objects.get_or_create(
                product=product,
                option=color_option,
                defaults={'display_order': 1}
            )
            variant.available_values.add(color_val)
            updated_products.add(product.slug)
            
            # Add images for this color to this product
            if image_url:
                _, created = ProductImage.objects.update_or_create(
                    product=product,
                    image_url=image_url,
                    defaults={
                        'option_value': color_val,
                        'is_primary': is_primary,
                        'display_order': display_order
                    }
                )
                if created:
                    created_images += 1

    print(f"Successfully processed {len(updated_products)} products.")
    print(f"Created {created_images} new product images.")
    
    # 3. Update HEX codes (optional but good for UX)
    print("Updating HEX codes...")
    COLOR_MAP = {
        'amarillo': '#FFEE58', 'azul': '#1E88E5', 'blanco': '#FFFFFF', 'negro': '#212121',
        'rojo': '#E53935', 'gris': '#9E9E9E', 'gris-terreno': '#616161', 'azul-marino': '#1A237E',
        'azul-cielo-nocturno': '#283593', 'blanco-brillante': '#F5F5F5', 'negro-profundo': '#000000',
        'rosa': '#F06292', 'verde': '#4CAF50', 'naranja': '#FB8C00'
    }
    
    hex_updated = 0
    for val in ProductOptionValue.objects.filter(option=color_option):
        slug = val.value.lower()
        new_hex = COLOR_MAP.get(slug)
        if not new_hex:
            for k, v in COLOR_MAP.items():
                if k in slug:
                    new_hex = v
                    break
        if new_hex and val.hex_code != new_hex:
            val.hex_code = new_hex
            val.save()
            hex_updated += 1
    
    print(f"Updated {hex_updated} HEX codes.")

if __name__ == "__main__":
    fix_swatches()
