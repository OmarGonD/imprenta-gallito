import pandas as pd
import os

BASE_DIR = r"D:\web_proyects\imprenta_gallito"
DATA_DIR = os.path.join(BASE_DIR, "static", "data")
IMAGES_DIR = os.path.join(BASE_DIR, "static", "media", "product_images", "stickers_etiquetas")

CATEGORIES = ['stickers', 'embalaje', 'etiquetas']

def get_all_images():
    # Returns list of dicts: {'filename': '...', 'subcat': '...', 'path': '...'}
    images = []
    for subcat in CATEGORIES:
        path = os.path.join(IMAGES_DIR, subcat)
        if os.path.exists(path):
            for fname in os.listdir(path):
                if fname.lower().endswith(('.jpg', '.png', '.jpeg')):
                    # Path relative to Site Root, must start with /media/
                    # FS Path: static/media/product_images/stickers_etiquetas/...
                    # URL Path: /media/product_images/stickers_etiquetas/...
                    rel_path = f"/media/product_images/stickers_etiquetas/{subcat}/{fname}"
                    images.append({
                        'filename': fname,
                        'subcat': subcat, # This matches subcategory_slug
                        'path': rel_path,
                        'slug_candidate': os.path.splitext(fname)[0].replace(' ', '-').lower()
                    })
    return images

def update_products():
    products_path = os.path.join(DATA_DIR, "products_complete.xlsx")
    df = pd.read_excel(products_path)
    
    # Existing slugs
    existing_slugs = set(df['product_slug'].astype(str).str.lower().str.strip())
    
    all_images = get_all_images()
    
    new_rows = []
    
    for img in all_images:
        slug = img['slug_candidate']
        path = img['path']
        subcat = img['subcat']
        
        # We need to find if this slug (or fuzzy match) exists
        # Actually, let's look for exact match first
        
        if slug in existing_slugs:
            # Update existing
            mask = df['product_slug'] == slug
            df.loc[mask, 'base_image_url'] = path
            df.loc[mask, 'subcategory_slug'] = subcat
            print(f"Updated {slug} -> {path}")
        else:
             # Check if there is a 'stickers-personalizados' vs 'stickers-troquelados' mismatch?
             # User mentioned "not all products are there". So adding them is correct.
             print(f"Adding new product: {slug} -> {path}")
             new_rows.append({
                'product_slug': slug,
                'product_name': slug.replace('-', ' ').title(),
                'category_slug': 'stickers-etiquetas',
                'subcategory_slug': subcat,
                'base_image_url': path,
                'sku': f"SKU-{slug[:4].upper()}-{len(slug)}",
                'description': f"Impresión de {slug.replace('-', ' ')}",
                'status': 'active',
                'min_quantity': 100
             })

    if new_rows:
        df_new = pd.DataFrame(new_rows)
        # Concatenate
        df_final = pd.concat([df, df_new], ignore_index=True)
        print(f"Added {len(new_rows)} new products.")
    else:
        df_final = df
        print("No new products added.")
        
    df_final.to_excel(products_path, index=False)
    return df_final

def update_prices(products_df):
    prices_path = os.path.join(DATA_DIR, "price_tiers_complete.xlsx")
    if os.path.exists(prices_path):
        df_prices = pd.read_excel(prices_path)
    else:
        df_prices = pd.DataFrame(columns=['product_slug', 'min_quantity', 'unit_price', 'discount_percent'])
    
    sticker_slugs = products_df[products_df['category_slug'] == 'stickers-etiquetas']['product_slug'].unique()
    
    new_rows = []
    
    for slug in sticker_slugs:
        # Check if tiers exist
        if not df_prices[df_prices['product_slug'] == slug].empty:
            continue
            
        # Add dummy tiers
        # Dummy prices: 0.50 per unit for 100, 0.40 for 500
        new_rows.append({'product_slug': slug, 'min_quantity': 100, 'unit_price': 0.50, 'discount_percent': 0})
        new_rows.append({'product_slug': slug, 'min_quantity': 500, 'unit_price': 0.40, 'discount_percent': 20})
        new_rows.append({'product_slug': slug, 'min_quantity': 1000, 'unit_price': 0.30, 'discount_percent': 30})

    if new_rows:
        df_new = pd.DataFrame(new_rows)
        df_final = pd.concat([df_prices, df_new], ignore_index=True)
        df_final.to_excel(prices_path, index=False)
        print(f"Added price tiers for {len(new_rows)//3} products.")
    else:
        print("No new price tiers needed.")

if __name__ == "__main__":
    df_final = update_products()
    update_prices(df_final)
