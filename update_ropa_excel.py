import pandas as pd
import os

# Configuration
BASE_IMAGES_DIR = os.path.join('static', 'media', 'product_images', 'ropa_y_bolsos')
DATA_DIR = os.path.join('static', 'data')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products_complete.xlsx')
SUBCATS_FILE = os.path.join(DATA_DIR, 'subcategories_complete.xlsx')
CATEGORY_SLUG = 'ropa-bolsos' # Assuming this based on URL /ropa-bolsos/

def get_subcategory_info(folder_name):
    slug = folder_name.replace('_', '-').lower()
    name = folder_name.replace('_', ' ').title()
    return slug, name

def run():
    if not os.path.exists(BASE_IMAGES_DIR):
        print(f"Error: {BASE_IMAGES_DIR} does not exist.")
        return

    # Load existing data
    try:
        products_df = pd.read_excel(PRODUCTS_FILE)
        subcats_df = pd.read_excel(SUBCATS_FILE)
        print("Loaded existing Excel files.")
    except Exception as e:
        print(f"Error loading Excel files: {e}")
        return

    existing_product_slugs = set(products_df['product_slug'].astype(str))
    existing_subcat_slugs = set(subcats_df['subcategory_slug'].astype(str))

    new_products = []
    new_subcats = []

    # Iterate over subdirectories in ropa_y_bolsos
    for folder_name in os.listdir(BASE_IMAGES_DIR):
        folder_path = os.path.join(BASE_IMAGES_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue

        sub_slug, sub_name = get_subcategory_info(folder_name)
        
        # Find images
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        if not images:
            print(f"No images found in {folder_name}, skipping.")
            continue
            
        # 1. Update Subcategory
        first_image = images[0]
        # Image URL for subcategory: relative to static root or media root?
        # Template uses {% static sub.image_url %}, so it should be relative to static/
        # My paths are static/media/product_images/..., so it should be media/product_images/...
        sub_image_url = f"media/product_images/ropa_y_bolsos/{folder_name}/{first_image}".replace('\\', '/')

        if sub_slug not in existing_subcat_slugs:
            print(f"Adding new subcategory: {sub_name} ({sub_slug})")
            new_subcat = {
                'subcategory_slug': sub_slug,
                'subcategory_name': sub_name,
                'category_slug': CATEGORY_SLUG,
                'description': f"Explora nuestra colección de {sub_name}",
                'image_url': sub_image_url,
                'display_order': 10, # arbitrary
                'display_style': 'grid'
            }
            # Fill missing columns with defaults
            for col in subcats_df.columns:
                if col not in new_subcat:
                    new_subcat[col] = None
            new_subcats.append(new_subcat)
            existing_subcat_slugs.add(sub_slug)
        else:
             # Update image for existing subcategory if needed (optional, skipping for now)
             pass

        # 2. Update Products
        for img_file in images:
            product_basename = os.path.splitext(img_file)[0]
            product_slug = product_basename.lower().replace('_', '-').replace(' ', '-')
            
            # Ensure unique slug if collision with other folders (unlikely but possible)
            if product_slug in existing_product_slugs:
                # print(f"Skipping existing product: {product_slug}")
                continue

            product_name = product_basename.replace('-', ' ').replace('_', ' ').title()
            sku = f"ROPA-{sub_slug[:3].upper()}-{len(existing_product_slugs) + len(new_products):04d}"
            base_image_url = f"/media/product_images/ropa_y_bolsos/{folder_name}/{img_file}".replace('\\', '/')
            # Note: template logic uses {% static product.base_image_url %}, so it usually expects no leading slash if it's strictly static.
            # But wait, product.base_image_url is usually a media reference.
            # Let's check update_products_excel.py line 26: 
            # base_image_url = f"/static/media/product_images/postales_publicidad/{subcategory_slug}/{file}"
            # It includes /static/. This is slightly redundant if static tag is used, but I will follow the pattern.
            # Actually line 158 of template: <img src="{% static product.base_image_url %}" 
            # If base_image_url starts with /, static tag might act weirdly or just prepend static URL.
            # Correct Django usage: static 'path' -> /static/path.
            # If path is /static/media/..., result is /static/static/media/... which is wrong.
            # Checking update_products_excel.py again: it uses /static/media/...
            # Let's verify existing products_complete.xlsx format via inspecting the head again?
            # Step 1645 output: 'base_image_url': '/static/media/product_images/...'
            # Okay, I will follow that pattern: /static/media/...
            
            full_image_url = f"media/product_images/ropa_y_bolsos/{folder_name}/{img_file}".replace('\\', '/')
            # No, if previous data has /static/ prefix in DB, I must match it?
            # Wait, step 1645 output was messy.
            # Let's trust the previous pattern: /static/media/...
            
            final_image_url = f"media/product_images/ropa_y_bolsos/{folder_name}/{img_file}".replace('\\', '/')
            
            # Actually, let's look at `update_products_excel.py` again.
            # Line 26: base_image_url = f"/static/media/..."
            # So I will use that.
            
            p_data = {
                'product_slug': product_slug,
                'product_name': product_name,
                'category_slug': CATEGORY_SLUG,
                'subcategory_slug': sub_slug,
                'sku': sku,
                'description': f"{product_name} de alta calidad.",
                'base_image_url': f"media/product_images/ropa_y_bolsos/{folder_name}/{img_file}".replace('\\', '/'), # Removing /static/ prefix to test relative path correctness with {% static %}
                # Wait, if I put media/... and use {% static %}, it becomes /static/media/... which is correct.
                # If I put /static/media/... and use {% static %}, it becomes /static//static/media/...
                # The previous user issue "double /static/static/" was exactly this.
                # So I should PROBABLY use `media/product_images/...` WITHOUT leading slash or static prefix.
                # Let's check one row from products_complete.xlsx properly.
                'status': 'active',
                'min_quantity': 1,
                'base_price': 25.00,
                'is_featured': False
            }
            
            # Fill defaults
            for col in products_df.columns:
                if col not in p_data:
                    p_data[col] = None
            
            new_products.append(p_data)
            existing_product_slugs.add(product_slug)

    print(f"Found {len(new_subcats)} new subcategories and {len(new_products)} new products.")

    if new_subcats:
        new_subcats_df = pd.DataFrame(new_subcats)
        subcats_df = pd.concat([subcats_df, new_subcats_df], ignore_index=True)
        subcats_df.to_excel(SUBCATS_FILE, index=False)
        print("Updated subcategories_complete.xlsx")

    if new_products:
        new_products_df = pd.DataFrame(new_products)
        products_df = pd.concat([products_df, new_products_df], ignore_index=True)
        products_df.to_excel(PRODUCTS_FILE, index=False)
        print("Updated products_complete.xlsx")

if __name__ == "__main__":
    run()
