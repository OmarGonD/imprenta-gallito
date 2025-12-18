import pandas as pd
import os

BASE_DIR = r"D:\web_proyects\imprenta_gallito"
DATA_DIR = os.path.join(BASE_DIR, "static", "data")
products_path = os.path.join(DATA_DIR, "products_complete.xlsx")
prices_path = os.path.join(DATA_DIR, "price_tiers_complete.xlsx")

def inspect():
    print("--- PRODUCTS ---")
    df_prod = pd.read_excel(products_path)
    print(df_prod.columns)
    # Check for stickers products
    stickers_prod = df_prod[df_prod['category_slug'] == 'stickers-etiquetas']
    if not stickers_prod.empty:
        print(stickers_prod[['product_name', 'product_slug', 'subcategory_slug', 'base_image_url']].head(10))
    else:
        print("No stickers-etiquetas products found.")
        # Print unique categories to verify slug
        print("Categories found:", df_prod['category_slug'].unique())

    print("\n--- PRICES ---")
    df_prices = pd.read_excel(prices_path)
    print(df_prices.columns)
    print(df_prices.head())

if __name__ == "__main__":
    inspect()
