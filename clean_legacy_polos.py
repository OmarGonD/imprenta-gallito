import pandas as pd
import os

DATA_DIR = os.path.join('static', 'data')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products_complete.xlsx')
SUBCATS_FILE = os.path.join(DATA_DIR, 'subcategories_complete.xlsx')

def clean():
    print("--- Cleaning Legacy 'polos' Data ---")
    
    # 1. Clean Products
    if os.path.exists(PRODUCTS_FILE):
        df_prod = pd.read_excel(PRODUCTS_FILE)
        initial_count = len(df_prod)
        
        # Remove products where subcategory_slug is 'polos'
        # Check column name
        col_sub = 'subcategory_slug'
        if col_sub in df_prod.columns:
            df_prod = df_prod[df_prod[col_sub] != 'polos']
            # Also remove products defined as 'polos' in category 'ropa-bolsos' if subcategory is missing/different but logically it was that
            # But relying on subcategory_slug='polos' is safest.
            
            cleaned_count = len(df_prod)
            print(f"Products: Removed {initial_count - cleaned_count} rows with subcategory_slug='polos'.")
            
            df_prod.to_excel(PRODUCTS_FILE, index=False)
            print(f"Updated {PRODUCTS_FILE}")
        else:
            print(f"Column '{col_sub}' not found in products file.")

    # 2. Clean Subcategories
    if os.path.exists(SUBCATS_FILE):
        df_sub = pd.read_excel(SUBCATS_FILE)
        initial_count = len(df_sub)
        
        col_slug = 'subcategory_slug' if 'subcategory_slug' in df_sub.columns else 'slug'
        
        # Remove subcategory "polos"
        if col_slug in df_sub.columns:
            df_sub = df_sub[df_sub[col_slug] != 'polos']
            
            cleaned_count = len(df_sub)
            print(f"Subcategories: Removed {initial_count - cleaned_count} rows with slug='polos'.")
            
            df_sub.to_excel(SUBCATS_FILE, index=False)
            print(f"Updated {SUBCATS_FILE}")
        else:
            print("Could not find slug column in subcategories.")

if __name__ == "__main__":
    clean()
