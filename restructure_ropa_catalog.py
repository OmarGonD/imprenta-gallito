import pandas as pd
import os
import re

# Config
BASE_IMAGES_DIR = os.path.join('static', 'media', 'product_images', 'ropa_y_bolsos')
DATA_DIR = os.path.join('static', 'data')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products_complete.xlsx')
IMAGES_FILE = os.path.join(DATA_DIR, 'ropa_product_images.xlsx')

CATEGORY_SLUG = 'ropa-bolsos'

def get_subcategory_info(folder_name):
    slug = folder_name.replace('_', '-').lower()
    return slug

def common_prefix(s1, s2):
    min_len = min(len(s1), len(s2))
    for i in range(min_len):
        if s1[i] != s2[i]:
            return s1[:i]
    return s1[:min_len]

def restructure():
    print("--- Restructuring Ropa Catalog ---")
    
    new_products = []
    product_images = [] # ID: product_slug, image_url, color_slug
    
    # 1. Load Existing (to append/update if needed, but we essentially want to replace ropa entries)
    # Actually, we should CLEAN ropa entries first (which we did previously, but let's be safe).
    # For this script, we will just BUILD the lists, then merge/write.
    
    if not os.path.exists(BASE_IMAGES_DIR):
        print(f"Error: {BASE_IMAGES_DIR} not found.")
        return

    # Iterate Subcategories
    for folder_name in os.listdir(BASE_IMAGES_DIR):
        folder_path = os.path.join(BASE_IMAGES_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue
            
        sub_slug = get_subcategory_info(folder_name)
        print(f"Processing Subcategory: {sub_slug}")
        
        # Get all images
        images = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        
        if not images:
            continue
            
        # Grouping Logic
        groups = []
        if images:
            current_group = [images[0]]
            
            for i in range(1, len(images)):
                prev_img = current_group[0] # Compare with LEAD of group to keep checking compatibility
                curr_img = images[i]
                
                # Simple prefix check
                # Remove extension for checking
                p1 = os.path.splitext(prev_img)[0]
                p2 = os.path.splitext(curr_img)[0]
                
                prefix = common_prefix(p1, p2)
                
                # Heuristic: Valid prefix must be at least 10 chars and end with '-' or be substantial?
                # Ideally, trim prefix to last '-' to avoid cutting in middle of word
                if '-' in prefix:
                    clean_prefix = prefix[:prefix.rfind('-') + 1]
                else:
                    clean_prefix = prefix

                # If the clean prefix is long enough (e.g., >5 chars) AND covers significant part
                # Actually, let's just check if p2 starts with clean_prefix
                if len(clean_prefix) > 5 and p2.startswith(clean_prefix):
                    current_group.append(curr_img)
                else:
                    groups.append(current_group)
                    current_group = [curr_img]
            
            if current_group:
                groups.append(current_group)
        
        # Process Groups -> Products
        for group in groups:
            first_img = group[0]
            
            # Determine Base Name from Group
            if len(group) > 1:
                # Find common prefix of whole group
                p1 = os.path.splitext(group[0])[0]
                p2 = os.path.splitext(group[-1])[0] # Compare first and last for range
                raw_prefix = common_prefix(p1, p2)
                if '-' in raw_prefix:
                    base_name_slug = raw_prefix[:raw_prefix.rfind('-')]
                else:
                    base_name_slug = raw_prefix
            else:
                # Single file
                base_name_slug = os.path.splitext(first_img)[0]
                # If there are dashes, maybe distinct color? e.g. "poll-rojo"
                # But without variants, it's ambiguous. Let's assume filename IS product name.
            
            # Clean slug
            base_name_slug = base_name_slug.strip('-').lower()
            if not base_name_slug:
                # Fallback if prefix logic failed (e.g. completely diff names?)
                base_name_slug = os.path.splitext(first_img)[0]

            # Construct Product Data
            product_slug = base_name_slug
            
            # Uniqueness check: prepend subcategory if needed?
            # Ideally "soft-touch-tee" is unique enough. 
            # But let's verify if we need subcategory prefix.
            # User wants: http://.../subcategory/product-slug/
            # Let's keep it simple for now. 
            # Collision check happens at global DB level.
            # Let's prepend subcategory ONLY if we detect collision later? 
            # Or just always prepend to be safe? "polos-hombre-soft-touch-tee".
            # User example: "bella-canvas-r-ultra-soft-jersey-unisex-t-shirt" (no subcat prefix shown in url, but slug might have it)
            # URL: /ropa-bolsos/polos-hombre/bella-canvas.../
            # So slug can be just 'bella-canvas...' if unique.
            
            # Let's clean the slug from common boilerplate if desired? 
            # "district-r-...", "gildan-r-..."
            
            product_name = base_name_slug.replace('-', ' ').title()
            
            # Base Image (Use first)
            # Path: media/product_images/ropa_y_bolsos/{folder_name}/{first_img}
            base_image_url = f"media/product_images/ropa_y_bolsos/{folder_name}/{first_img}".replace('\\', '/')
            
            p_data = {
                'product_slug': product_slug,
                'product_name': product_name,
                'category_slug': CATEGORY_SLUG,
                'subcategory_slug': sub_slug,
                'sku': f"ROPA-{sub_slug[:3].upper()}-{len(new_products):04d}",
                'description': f"{product_name} - Disponible en varios colores.",
                'base_image_url': base_image_url,
                'status': 'active',
                'min_quantity': 1,
                'base_price': 25.00
            }
            new_products.append(p_data)
            
            # Process Images (Variants)
            for idx, img_file in enumerate(group):
                # Extract Color
                # Color is suffix: filename - base_name_slug
                fname = os.path.splitext(img_file)[0]
                
                # Remove base_name_slug from fname
                # Be careful of partial matches
                # If fname starts with base_name_slug, remove it.
                
                color_slug = None
                if fname.startswith(base_name_slug):
                    suffix = fname[len(base_name_slug):].strip('-')
                    if suffix:
                        color_slug = suffix
                    else:
                        color_slug = "default" # or 'unico'
                else:
                    # If base name inference was imperfect
                    color_slug = fname
                
                img_entry = {
                    'product_slug': product_slug,
                    'image_url': f"media/product_images/ropa_y_bolsos/{folder_name}/{img_file}".replace('\\', '/'),
                    'color_slug': color_slug,
                    'display_order': idx,
                    'is_primary': (idx == 0)
                }
                product_images.append(img_entry)

    # OUTPUT
    print(f"Generated {len(new_products)} unique products and {len(product_images)} images/variants.")
    
    # 1. Update Products File
    # We load standard file, REMOVE existing ropa items, APPEND new ones.
    if os.path.exists(PRODUCTS_FILE):
        df_all = pd.read_excel(PRODUCTS_FILE)
        # Remove old ropa
        df_clean = df_all[df_all['category_slug'] != CATEGORY_SLUG]
        
        # Create new DF
        df_new = pd.DataFrame(new_products)
        # Ensure cols match
        combined = pd.concat([df_clean, df_new], ignore_index=True)
        combined.to_excel(PRODUCTS_FILE, index=False)
        print(f"Updated {PRODUCTS_FILE}")
    
    # 2. Write Images File
    # Create new Excel for image import
    if product_images:
        df_imgs = pd.DataFrame(product_images)
        df_imgs.to_excel(IMAGES_FILE, index=False)
        print(f"Created {IMAGES_FILE}")

if __name__ == "__main__":
    restructure()
