import pandas as pd
import os

DATA_DIR = os.path.join('static', 'data')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products_complete.xlsx')
SUBCATS_FILE = os.path.join(DATA_DIR, 'subcategories_complete.xlsx')
CATEGORY_SLUG = 'ropa-bolsos'

def run():
    print(f"--- Resetting Data for Category: {CATEGORY_SLUG} ---")
    
    # 1. Reset Subcategories
    if os.path.exists(SUBCATS_FILE):
        df_sub = pd.read_excel(SUBCATS_FILE)
        initial_count = len(df_sub)
        
        # Remove where category_slug is 'ropa-bolsos'
        if 'category_slug' in df_sub.columns:
            df_sub = df_sub[df_sub['category_slug'] != CATEGORY_SLUG]
            
            cleaned_count = len(df_sub)
            print(f"Subcategories: Removed {initial_count - cleaned_count} rows for '{CATEGORY_SLUG}'.")
            
            df_sub.to_excel(SUBCATS_FILE, index=False)
        else:
            print("Column 'category_slug' not found in subcategories.")
            
    # 2. Reset Products
    if os.path.exists(PRODUCTS_FILE):
        df_prod = pd.read_excel(PRODUCTS_FILE)
        initial_count = len(df_prod)
        
        # Remove where category_slug is 'ropa-bolsos'
        if 'category_slug' in df_prod.columns:
            df_prod = df_prod[df_prod['category_slug'] != CATEGORY_SLUG]
            
            cleaned_count = len(df_prod)
            print(f"Products: Removed {initial_count - cleaned_count} rows for '{CATEGORY_SLUG}'.")
            
            df_prod.to_excel(PRODUCTS_FILE, index=False)
        else:
             print("Column 'category_slug' not found in products.")

if __name__ == "__main__":
    run()
