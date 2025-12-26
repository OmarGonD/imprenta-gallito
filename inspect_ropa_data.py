import pandas as pd
import os

DATA_DIR = os.path.join('static', 'data')
SUBCATS_FILE = os.path.join(DATA_DIR, 'subcategories_complete.xlsx')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products_complete.xlsx')

def run():
    print("--- Inspecting Subcategories ---")
    if os.path.exists(SUBCATS_FILE):
        df_sub = pd.read_excel(SUBCATS_FILE)
        print(f"Subcategory file columns: {list(df_sub.columns)}")
        
        col_slug = 'subcategory_slug' if 'subcategory_slug' in df_sub.columns else 'slug'
        if col_slug not in df_sub.columns:
             print(f"Error: Could not find slug column. Available: {df_sub.columns}")
        else:
            # Filter for our specific subcategories
            target_subs = ['polos-hombre', 'polos-mujer', 'polos_hombre', 'polos_mujer']
            found_subs = df_sub[df_sub[col_slug].isin(target_subs)]
            if not found_subs.empty:
                 cols_to_show = [c for c in [col_slug, 'subcategory_name', 'name', 'category_slug'] if c in df_sub.columns]
                 print(found_subs[cols_to_show].to_string())
            else:
                 print("No target subcategories found in Excel.")
    else:
        print("Subcategories file not found.")

    print("\n--- Inspecting Products ---")
    if os.path.exists(PRODUCTS_FILE):
        df_prod = pd.read_excel(PRODUCTS_FILE)
        # Filter for products in these subcategories
        target_subs_slugs = ['polos-hombre', 'polos-mujer', 'polos_hombre', 'polos_mujer']
        
        # Check column name for subcategory slug, usually 'subcategory_slug'
        col_name = 'subcategory_slug'
        if col_name not in df_prod.columns:
            print(f"Column '{col_name}' not found in products file.")
            print(df_prod.columns)
            return

        found_prods = df_prod[df_prod[col_name].isin(target_subs_slugs)]
        print(f"Found {len(found_prods)} products for {target_subs_slugs}")
        if not found_prods.empty:
            print(found_prods[['product_slug', 'subcategory_slug', 'product_name']].head(10).to_string())
            
        # Also check distinct subcategory slugs in 'ropa-bolsos'
        print("\nDistinct subcategory slugs in 'ropa-bolsos':")
        ropa_prods = df_prod[df_prod['category_slug'] == 'ropa-bolsos']
        print(ropa_prods['subcategory_slug'].unique())
    else:
        print("Products file not found.")

if __name__ == "__main__":
    run()
