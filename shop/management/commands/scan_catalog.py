import os
import re
import glob
import pandas as pd
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify
import math

class Command(BaseCommand):
    help = 'Scans static/media/product_images and generates catalog Excel files (Fresh Start with Backups).'

    def handle(self, *args, **options):
        self.stdout.write("Scaning catalog from filesystem (FRESH START)...")
        
        # Paths
        base_img_dir = os.path.join(settings.BASE_DIR, 'static', 'media', 'product_images')
        subcat_img_dir = os.path.join(settings.BASE_DIR, 'static', 'media', 'subcategory_images')
        data_dir = os.path.join(settings.BASE_DIR, 'static', 'data')
        
        files = {
            'cats': os.path.join(data_dir, 'categories_complete.xlsx'),
            'subcats': os.path.join(data_dir, 'subcategories_complete.xlsx'),
            'products': os.path.join(data_dir, 'products_complete.xlsx'),
            'images': os.path.join(data_dir, 'ropa_product_images.xlsx'), 
            'prices': os.path.join(data_dir, 'price_tiers_complete.xlsx')
        }
        
        # 0. BACKUP LOGIC
        self.create_backups(files)
        
        scanned_cats = []
        scanned_subcats = []
        scanned_products = []
        scanned_images = [] # For variants
        
        # =====================================================================
        # PHASE 1: SCAN subcategory_images/ FOR CATEGORIES AND SUBCATEGORIES
        # =====================================================================
        if not os.path.exists(subcat_img_dir):
            self.stdout.write(self.style.WARNING(f"subcategory_images not found: {subcat_img_dir}"))
        else:
            for cat_folder in sorted(os.listdir(subcat_img_dir)):
                cat_path = os.path.join(subcat_img_dir, cat_folder)
                if not os.path.isdir(cat_path):
                    continue
                
                # Map folder to slug
                cat_slug = cat_folder.replace('_', '-').lower()
                
                # SLUG OVERRIDES
                if cat_slug == 'ropa-y-bolsos': 
                    cat_slug = 'ropa-bolsos'
                if cat_slug == 'stickers':
                    cat_slug = 'stickers-etiquetas'
                if cat_slug == 'calendarios-regalos-otros':
                    continue  # Skip this auxiliary folder
                
                cat_name = cat_folder.replace('_', ' ').title()
                
                self.stdout.write(f"Processing Category (from subcategory_images): {cat_slug}")
                
                # Add Category
                if not any(c['category_slug'] == cat_slug for c in scanned_cats):
                    scanned_cats.append({
                        'category_slug': cat_slug,
                        'category_name': cat_name,
                        'status': 'active',
                        'display_order': 0,
                        'description': '', 
                        'image_url': '' 
                    })
                
                # Scan images in this folder → Each image = 1 Subcategory
                for img_file in sorted(os.listdir(cat_path)):
                    img_path = os.path.join(cat_path, img_file)
                    if os.path.isdir(img_path):
                        continue
                    if not img_file.lower().endswith(('.jpg', '.png', '.jpeg', '.webp')):
                        continue
                    
                    # Subcategory slug = filename without extension
                    base_name = os.path.splitext(img_file)[0]
                    base_sub_slug = base_name.replace('_', '-').lower()
                    
                    # Sanitize slug
                    base_sub_slug = base_sub_slug.replace(' ', '-')
                    base_sub_slug = re.sub(r'[^a-z0-9_-]', '', base_sub_slug)
                    base_sub_slug = re.sub(r'-+', '-', base_sub_slug).strip('-')
                    
                    sub_name = base_name.replace('-', ' ').replace('_', ' ').title()
                    
                    # Logic to avoid duplicates and handle collisions across categories
                    existing_in_cat = any(s['subcategory_slug'] == base_sub_slug and s['category_slug'] == cat_slug for s in scanned_subcats)
                    if existing_in_cat:
                        continue
                        
                    sub_slug = base_sub_slug
                    # If this slug is already used by ANOTHER category, use prefixed version
                    if any(s['subcategory_slug'] == sub_slug for s in scanned_subcats):
                        sub_slug = f"{cat_slug}-{base_sub_slug}"
                    
                    # Check if product folder exists
                    # product_images/{cat_folder_original}/{base_name}/
                    product_folder_name = base_name.replace('-', '_')
                    cat_folder_in_products = cat_folder
                    # Handle naming mismatches
                    if cat_slug == 'stickers-etiquetas':
                        cat_folder_in_products = 'stickers_etiquetas'
                    if cat_slug == 'ropa-bolsos':
                        cat_folder_in_products = 'ropa_y_bolsos'
                    
                    product_folder_path = os.path.join(base_img_dir, cat_folder_in_products, product_folder_name)
                    has_products = os.path.isdir(product_folder_path)
                    
                    scanned_subcats.append({
                        'subcategory_slug': sub_slug,
                        'subcategory_name': sub_name,
                        'category_slug': cat_slug,
                        'description': f"Colección {sub_name}",
                        'image_url': f"media/subcategory_images/{cat_folder}/{img_file}".replace('\\', '/'),
                        'display_order': 0,
                        'status': 'active' if has_products else 'inactive',  # Mark empty subcats as inactive
                        'has_products': has_products
                    })
                    
                    self.stdout.write(f"  + Subcategory: {sub_slug} (products: {has_products})")
        
        # =====================================================================
        # PHASE 2: SCAN product_images/ FOR PRODUCTS
        # =====================================================================
        if not os.path.exists(base_img_dir):
            self.stdout.write(self.style.ERROR(f"Directory not found: {base_img_dir}"))
            return
        
        for cat_folder in sorted(os.listdir(base_img_dir)):
            cat_path = os.path.join(base_img_dir, cat_folder)
            if not os.path.isdir(cat_path):
                continue
            
            cat_slug = cat_folder.replace('_', '-').lower()
            if cat_slug == 'ropa-y-bolsos': 
                cat_slug = 'ropa-bolsos'
            
            # Ensure category exists (might not if subcategory_images didn't have it)
            if not any(c['category_slug'] == cat_slug for c in scanned_cats):
                cat_name = cat_folder.replace('_', ' ').title()
                scanned_cats.append({
                    'category_slug': cat_slug,
                    'category_name': cat_name,
                    'status': 'active',
                    'display_order': 0,
                    'description': '', 
                    'image_url': '' 
                })
            
            # Get subdirectories (subcategories with products)
            subdirs = [d for d in os.listdir(cat_path) if os.path.isdir(os.path.join(cat_path, d))]
            
            if subdirs:
                for sub_folder in subdirs:
                    sub_path = os.path.join(cat_path, sub_folder)
                    base_sub_slug = sub_folder.replace('_', '-').lower()
                    
                    # 1. Determine sub_slug
                    existing = next((s for s in scanned_subcats if s['category_slug'] == cat_slug and (s['subcategory_slug'] == base_sub_slug or s['subcategory_slug'] == f"{cat_slug}-{base_sub_slug}")), None)
                    
                    if existing:
                        sub_slug = existing['subcategory_slug']
                    else:
                        sub_slug = base_sub_slug
                        # Handle global collisions
                        if any(s['subcategory_slug'] == sub_slug for s in scanned_subcats):
                            sub_slug = f"{cat_slug}-{base_sub_slug}"
                            
                        sub_name = sub_folder.replace('_', ' ').title()
                        # Find first image for thumbnail
                        first_image = ''
                        for item in os.listdir(sub_path):
                            item_path = os.path.join(sub_path, item)
                            if not os.path.isdir(item_path) and item.lower().endswith(('.jpg', '.png', '.jpeg', '.webp')):
                                first_image = item
                                break
                                
                        scanned_subcats.append({
                            'subcategory_slug': sub_slug,
                            'subcategory_name': sub_name,
                            'category_slug': cat_slug,
                            'description': f"Colección {sub_name}",
                            'image_url': f"media/product_images/{cat_folder}/{sub_folder}/{first_image}".replace('\\', '/') if first_image else '',
                            'display_order': 0,
                            'status': 'active',
                            'has_products': True
                        })
                    
                    # Process products in this subcategory
                    self.process_folder_products(cat_slug, sub_slug, sub_path, scanned_products, scanned_images, f"{cat_folder}/{sub_folder}")
            else:
                # FLAT STRUCTURE (e.g. Tarjetas - images directly in category folder)
                sub_slug = "standard"
                if cat_slug == 'tarjetas-presentacion': 
                    sub_slug = 'tarjetas-standard'
                
                if any(s['subcategory_slug'] == sub_slug for s in scanned_subcats):
                    sub_slug = f"{cat_slug}-standard"
                
                if not any(s['subcategory_slug'] == sub_slug for s in scanned_subcats):
                    scanned_subcats.append({
                        'subcategory_slug': sub_slug,
                        'subcategory_name': 'Estándar',
                        'category_slug': cat_slug,
                        'description': 'Productos Estándar',
                        'image_url': '',
                        'display_order': 0,
                        'status': 'active',
                        'has_products': True
                    })
                
                self.process_folder_products(cat_slug, sub_slug, cat_path, scanned_products, scanned_images, cat_folder)


        # SAVE (No Merge, just Overwrite)
        
        # Categories
        self.save_df(scanned_cats, files['cats'])
        
        # Subcategories
        self.save_df(scanned_subcats, files['subcats'])
        
        # Products
        self.save_df_products(scanned_products, files['products'])
        
        # Images (Variants)
        pd.DataFrame(scanned_images).to_excel(files['images'], index=False)
        self.stdout.write(f"Saved {files['images']}")
        
        # Prices
        self.generate_prices_fresh(scanned_products, files['prices'])

    def create_backups(self, files_dict):
        self.stdout.write("Creating backups...")
        today_str = datetime.now().strftime('%d%m%Y')
        
        for name, filepath in files_dict.items():
            if os.path.exists(filepath):
                base, ext = os.path.splitext(filepath)
                # Format: filename-old-ddmmyyy.xlsx
                backup_name = f"{base}-old-{today_str}{ext}"
                
                # Copy/Rename logic
                # User said: "backup". Renaming is safer to ensure we don't process old file if code failed?
                # But we just overwrite later. Copy is better.
                import shutil
                shutil.copy2(filepath, backup_name)
                self.stdout.write(f"   Backup created: {os.path.basename(backup_name)}")
                
                # Cleanup Old Backups (Max 3)
                # Pattern: base-old-*.xlsx
                pattern = f"{base}-old-*{ext}"
                backups = sorted(glob.glob(pattern), key=os.path.getmtime)
                
                if len(backups) > 3:
                    to_delete = backups[:-3] # Keep last 3
                    for f in to_delete:
                        try:
                            os.remove(f)
                            self.stdout.write(f"   Deleted old backup: {os.path.basename(f)}")
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f"   Failed to delete {f}: {e}"))

    def process_folder_products(self, cat_slug, sub_slug, folder_path, products_list, images_list, rel_path):
        # Exclude -detalle.jpg images (detail shots, not main products)
        files = sorted([
            f for f in os.listdir(folder_path) 
            if f.lower().endswith(('.jpg', '.png', '.jpeg', '.webp'))
            and not f.lower().endswith('-detalle.jpg')
            and '-detalle.' not in f.lower()
        ])
        if not files: return
        
        # GROUPING LOGIC
        groups = []
        if files:
            current_group = [files[0]]
            for i in range(1, len(files)):
                prev = current_group[0]
                curr = files[i]
                
                p1 = os.path.splitext(prev)[0]
                p2 = os.path.splitext(curr)[0]
                
                def common(s1, s2):
                    return os.path.commonprefix([s1, s2])
                
                prefix = common(p1, p2)
                
                should_group = False
                if len(prefix) > 4:
                     if '-' in prefix:
                         should_group = True
                     elif p2.startswith(p1): 
                         should_group = True
                
                if cat_slug == 'ropa-bolsos':
                     if len(prefix) > 5 and p2.startswith(prefix[:prefix.rfind('-')+1] if '-' in prefix else prefix):
                         should_group = True
                     else:
                         should_group = False
                else:
                    should_group = False

                if should_group:
                    current_group.append(curr)
                else:
                    groups.append(current_group)
                    current_group = [curr]
            if current_group:
                groups.append(current_group)

        # Create Products from Groups
        for group in groups:
            first_img = group[0]
            base_sq = os.path.splitext(first_img)[0]
            
            # Slug Logic
            if len(group) > 1:
                common = os.path.commonprefix([os.path.splitext(f)[0] for f in group])
                slug = common.strip('-').lower()
                if not slug: slug = base_sq.lower()
            else:
                slug = base_sq.lower()
            
            # SANITIZE SLUG: Remove spaces, replace with hyphens, remove invalid chars
            import re
            slug = slug.replace(' ', '-')  # Replace spaces with hyphens
            slug = re.sub(r'[^a-z0-9_-]', '', slug)  # Keep only valid slug chars
            slug = re.sub(r'-+', '-', slug)  # Collapse multiple hyphens
            slug = slug.strip('-')  # Remove leading/trailing hyphens
            
            # UNIQUENESS CHECK
            existing_slugs = {p['product_slug'] for p in products_list}
            
            if slug in existing_slugs:
                slug = f"{sub_slug}-{slug}"
                
            if slug in existing_slugs:
                 import uuid
                 slug = f"{slug}-{uuid.uuid4().hex[:4]}"
            
            name = slug.replace('-', ' ').title()
            base_image_url = f"media/product_images/{rel_path}/{first_img}".replace('\\', '/')
            
            # --- CUSTOM LOGIC FOR STICKERS: EXPLODE SIZES ---
            is_generic_sticker = False
            if cat_slug == 'stickers-etiquetas':
                # Exclude specific non-sticker items from expansion
                exclusions = ['cinta', 'sobres', 'letras', 'plancha']
                if not any(exc in slug for exc in exclusions):
                    is_generic_sticker = True
            
            if is_generic_sticker:
                sizes = ["4x4", "5x5", "6x6", "7x7", "8x8", "9x9", "10x10"]
                for size in sizes:
                    variant_slug = f"{slug}-{size}"
                    variant_name = f"{name} {size}cm"
                    
                    products_list.append({
                        'product_slug': variant_slug,
                        'product_name': variant_name,
                        'category_slug': cat_slug,
                        'subcategory_slug': sub_slug,
                        'sku': f"{cat_slug[:3].upper()}-{sub_slug[:3].upper()}-{len(products_list):04d}",
                        'base_image_url': base_image_url,
                        'min_quantity': 100, # Stickers default min
                        'status': 'active',
                        'description': f"{variant_name} - Colección {cat_slug}"
                    })
            else:
                # STANDARD PRODUCT creation
                products_list.append({
                    'product_slug': slug,
                    'product_name': name,
                    'category_slug': cat_slug,
                    'subcategory_slug': sub_slug,
                    'sku': f"{cat_slug[:3].upper()}-{sub_slug[:3].upper()}-{len(products_list):04d}",
                    'base_image_url': base_image_url,
                    'min_quantity': 100 if cat_slug != 'ropa-bolsos' else 1, 
                    'status': 'active',
                    'description': f"{name} - Colección {cat_slug}"
                })
            
            # Images/Variants
            for idx, img in enumerate(group):
                img_name = os.path.splitext(img)[0]
                color = "default"
                if len(group) > 1 and img_name.startswith(slug):
                    color = img_name[len(slug):].strip('-')
                    if not color: color = "default"
                elif len(group) == 1:
                    color = "unique"
                
                images_list.append({
                    'product_slug': slug,
                    'image_url': f"media/product_images/{rel_path}/{img}".replace('\\', '/'),
                    'color_slug': color,
                    'display_order': idx,
                    'is_primary': idx==0
                })

    def save_df(self, data, filepath):
        if not data: 
            # Save empty?
            pd.DataFrame().to_excel(filepath, index=False)
            return
            
        df = pd.DataFrame(data)
        
        # Ensure display_order
        if 'display_order' in df.columns:
            df['display_order'] = df['display_order'].fillna(0).astype(int)

        df.to_excel(filepath, index=False)
        self.stdout.write(f"Saved {filepath}")

    def save_df_products(self, data, filepath):
        if not data: 
            pd.DataFrame().to_excel(filepath, index=False)
            return
        
        df = pd.DataFrame(data)
        
        # Deduplicate just in case
        if 'product_slug' in df.columns:
            df = df.drop_duplicates(subset=['product_slug'], keep='last')

        df.to_excel(filepath, index=False)
        self.stdout.write(f"Saved {filepath} (Products)")

    def generate_prices_fresh(self, products_list, filepath):
        self.stdout.write("Generating price tiers (FRESH)...")
        
        # Override any existing file logic, create from scratch
        new_tiers = []
        
        for p in products_list:
            slug = p['product_slug']
            
            # Default Tiers
            if p['category_slug'] == 'ropa-bolsos':
                tiers = [
                    (1, 11, 67.00),
                    (12, 49, 62.00),
                    (50, 99, 56.00),
                    (100, 499, 50.00),
                    (500, 999999, 48.00)
                ]
            else:
                # CHECK FOR STICKER SIZES
                # Using the config: (Full cost, Half cost, Markup)
                # FULL_BATCH_COST = 45.0
                # HALF_BATCH_COST = 25.0
                # MANAGEMENT_FEE = 12.00
                
                sticker_config = {
                    "-4x4":   (500, 250, 0.15), 
                    "-5x5":   (360, 180, 0.20),
                    "-6x6":   (280, 140, 0.30),
                    "-7x7":   (200, 100, 0.40),
                    "-8x8":   (150, 75,  0.50),
                    "-9x9":   (130, 65,  0.60),
                    "-10x10": (100, 50,  0.80),
                }
                
                matched_config = None
                for suffix, config in sticker_config.items():
                    if slug.endswith(suffix):
                        matched_config = config
                        break
                
                if matched_config:
                    # SMART PRICING LOGIC
                    full_units, half_units, unit_markup = matched_config
                    quantities = [10, 20, 50, 100, 500, 1000]
                    mgmt_fee = 12.00
                    
                    tiers = []
                    for qty in quantities:
                        # 1. Costo Real
                        num_full = qty // full_units
                        rem = qty % full_units
                        
                        cost = num_full * 45.0
                        if rem > 0:
                            cost += 25.0 if rem <= half_units else 45.0
                            
                        # 2. Precio Venta
                        var_profit = unit_markup * qty
                        smart = cost + mgmt_fee + var_profit
                        
                        total = math.ceil(smart * 2) / 2
                        unit = round(total / qty, 3)
                        
                        # Max Qty logic
                        max_q = 999999
                        if qty == 10: max_q = 19
                        elif qty == 20: max_q = 49
                        elif qty == 50: max_q = 99
                        elif qty == 100: max_q = 499
                        elif qty == 500: max_q = 999
                        
                        tiers.append((qty, max_q, unit))
                else:
                    # GENERIC FALLBACK
                    tiers = [
                        (100, 499, 0.50),
                        (500, 999, 0.40),
                        (1000, 999999, 0.30)
                    ]
                
            base_price = tiers[0][2] if tiers else 0
            for min_q, max_q, price in tiers:
                discount = 0
                if base_price > 0:
                    discount = round((1 - (price / base_price)) * 100)
                
                new_tiers.append({
                    'product': slug,
                    'min_quantity': min_q,
                    'max_quantity': max_q,
                    'unit_price': price,
                    'discount_percentage': discount
                })
                    
        df = pd.DataFrame(new_tiers)
        df.to_excel(filepath, index=False)
        self.stdout.write(f"Saved {filepath} with {len(new_tiers)} price tiers.")
