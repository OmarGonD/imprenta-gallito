
import os
import pandas as pd
from pathlib import Path

# Configuration
BASE_DIR = Path(r"D:\web_proyects\imprenta_gallito\static\media\product_images")
OUTPUT_DIR = Path(r"D:\web_proyects\imprenta_gallito\static\data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# User defined category mapping (Folder Name -> Category Slug)
CATEGORY_MAPPING = {
    'ropa_y_bolsos': 'ropa-bolsos',
}

# Subcategory Mapping (Folder Name -> Subcategory Slug)
# Mappings inferred from previous debugging to match existing shop structure
SUBCATEGORY_MAPPING = {
    'invitaciones_y_anuncios': 'invitaciones-personalizadas',
}

# Pricing Logic
PRICING_TIERS = [
    {'min_quan': 1, 'max_quan': 49, 'unit_price': 1.2, 'discount_percent': 0},
    {'min_quan': 50, 'max_quan': 99, 'unit_price': 1.02, 'discount_percent': 15},
    {'min_quan': 100, 'max_quan': 249, 'unit_price': 1.00, 'discount_percent': 30},
    {'min_quan': 250, 'max_quan': 499, 'unit_price': 0.90, 'discount_percent': 40},
    {'min_quan': 500, 'max_quan': 9999, 'unit_price': 0.60, 'discount_percent': 50},
]

def get_slug(name):
    return name.replace('_', '-').lower()

def clean_name(slug):
    return slug.replace('-', ' ').title()

def generate_files():
    products_data = []
    prices_data = []
    generated_skus = set()

    # Iterate Categories
    for category_dir in BASE_DIR.iterdir():
        if not category_dir.is_dir():
            continue
        
        # Determine Category Slug
        cat_folder = category_dir.name
        cat_slug = CATEGORY_MAPPING.get(cat_folder, cat_folder.replace('_', '-'))

        # Iterate Subcategories
        for subcategory_dir in category_dir.iterdir():
            if not subcategory_dir.is_dir():
                continue
            
            sub_folder = subcategory_dir.name
            sub_slug = SUBCATEGORY_MAPPING.get(sub_folder, sub_folder.replace('_', '-'))
            
            # Iterate Products (Images) recursively
            for image_file in subcategory_dir.rglob('*'):
                if image_file.is_dir():
                    continue
                if image_file.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.webp']:
                    continue
                
                # Product Data
                prod_slug = image_file.stem.replace('_', '-')
                prod_name = clean_name(prod_slug)
                
                # SKU Generation with Uniqueness Check
                # Use first 8 chars of slug to keep it reasonably short but recognizable
                base_sku = f"{cat_slug[:3].upper()}-{sub_slug[:3].upper()}-{prod_slug[:8].upper()}"
                sku = base_sku
                counter = 1
                while sku in generated_skus:
                    sku = f"{base_sku}-{counter}"
                    counter += 1
                generated_skus.add(sku)
                
                # Base Image URL - ensure it's relative to MEDIA
                # D:\web_proyects\imprenta_gallito\static\media\product_images\...
                # We need /media/product_images/...
                try:
                    rel_path = image_file.relative_to(r"D:\web_proyects\imprenta_gallito\static")
                    base_image_url = "/" + str(rel_path).replace("\\", "/")
                except ValueError:
                    # Fallback if path manipulation fails
                    base_image_url = ""

                products_data.append({
                    'product_slug': prod_slug,
                    'product_name': prod_name,
                    'category_slug': cat_slug,
                    'subcategory_slug': sub_slug,
                    'sku': sku,
                    'description': f"Descripción para {prod_name}",
                    'base_image_url': base_image_url
                })

                # Price Tiers Data
                for tier in PRICING_TIERS:
                    prices_data.append({
                        'category_slug': cat_slug,
                        'subcategory_slug': sub_slug,
                        'product_slug': prod_slug,
                        'min_quan': tier['min_quan'],
                        'max_quan': tier['max_quan'],
                        'unit_price': tier['unit_price'],
                        'discount_percent': tier['discount_percent']
                    })

    # Create DataFrames
    df_products = pd.DataFrame(products_data)
    df_prices = pd.DataFrame(prices_data)

    # Save to Excel
    products_path = OUTPUT_DIR / "products_complete.xlsx"
    prices_path = OUTPUT_DIR / "price_tiers_complete.xlsx"

    print(f"Saving products to {products_path}")
    df_products.to_excel(products_path, index=False)
    
    print(f"Saving prices to {prices_path}")
    df_prices.to_excel(prices_path, index=False)
    
    print(f"Done! Generated {len(df_products)} products.")

if __name__ == "__main__":
    generate_files()
