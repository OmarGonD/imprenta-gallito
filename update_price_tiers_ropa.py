import pandas as pd
import os

# Files
DATA_DIR = os.path.join('static', 'data')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products_complete.xlsx')
TIERS_FILE = os.path.join(DATA_DIR, 'price_tiers_complete.xlsx')

def run():
    if not os.path.exists(PRODUCTS_FILE) or not os.path.exists(TIERS_FILE):
        print("Error: Files not found.")
        return

    try:
        products_df = pd.read_excel(PRODUCTS_FILE)
        tiers_df = pd.read_excel(TIERS_FILE)
    except Exception as e:
        print(f"Error reading Excel files: {e}")
        return
        
    # Get all products that are 'ropa-bolsos'
    ropa_products = products_df[products_df['category_slug'] == 'ropa-bolsos']
    
    if ropa_products.empty:
        print("No ropa products found.")
        return
        
    print(f"Found {len(ropa_products)} ropa products.")
    
    # Get headers of tiers file
    headers = list(tiers_df.columns)
    
    new_tiers = []
    
    # Existing products with pricing
    existing_priced_products = set(tiers_df['product_slug'].astype(str))
    
    count_added = 0
    
    for _, product in ropa_products.iterrows():
        p_slug = str(product['product_slug']).strip()
        
        if p_slug in existing_priced_products:
            continue
            
        # Define standard tiers (Sample pricing)
        # 1-11: Base Price (25.00)
        # 12-49: 23.00 (8% off)
        # 50+: 20.00 (20% off)
        
        base_price = 25.00 # Placeholder base price
        
        # Tier 1: 1 - 11
        t1 = {
            'category_slug': product['category_slug'],
            'subcategory_slug': product['subcategory_slug'],
            'product_slug': p_slug,
            'min_quan': 1,
            'max_quan': 11,
            'unit_price': base_price,
            'discount_percent': 0
        }
        
        # Tier 2: 12 - 49
        t2 = {
            'category_slug': product['category_slug'],
            'subcategory_slug': product['subcategory_slug'],
            'product_slug': p_slug,
            'min_quan': 12,
            'max_quan': 49,
            'unit_price': 23.00,
            'discount_percent': 8
        }
        
        # Tier 3: 50+
        t3 = {
            'category_slug': product['category_slug'],
            'subcategory_slug': product['subcategory_slug'],
            'product_slug': p_slug,
            'min_quan': 50,
            'max_quan': 99999, # Representation of infinity or empty
            'unit_price': 20.00,
            'discount_percent': 20
        }
        
        # Add columns ensuring order matches headers if possible, or just dict
        new_tiers.append(t1)
        new_tiers.append(t2)
        new_tiers.append(t3)
        
        count_added += 1
        
    if new_tiers:
        new_tiers_df = pd.DataFrame(new_tiers)
        # Ensure columns align
        tiers_df = pd.concat([tiers_df, new_tiers_df], ignore_index=True)
        tiers_df.to_excel(TIERS_FILE, index=False)
        print(f"Added pricing for {count_added} products ({len(new_tiers)} rows).")
    else:
        print("No new products to add pricing for.")

if __name__ == "__main__":
    run()
