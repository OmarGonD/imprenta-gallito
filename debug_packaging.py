
import pandas as pd

DATA_DIR = r"D:\web_proyects\imprenta_gallito\static\data"

print("--- Subcategories (Packaging Alimentario) ---")
try:
    df_subs = pd.read_excel(f"{DATA_DIR}\\subcategories_complete.xlsx")
    print("Columns:", df_subs.columns.tolist())
    # Try to find anything resembling 'cajas' or 'comida'
    print(df_subs[df_subs['category_slug'] == 'packaging-alimentario'])
except Exception as e:
    print(f"Error reading subcategories: {e}")

print("\n--- Products (Packaging Alimentario) ---")
try:
    df_prods = pd.read_excel(f"{DATA_DIR}\\products_complete.xlsx")
    prods = df_prods[df_prods['category_slug'] == 'packaging-alimentario']
    print(f"Total products: {len(prods)}")
    if not prods.empty:
        print(prods['subcategory_slug'].value_counts())
        print("\nSample URLs from 'cajas-vasos-para-llevar':")
        print(prods[prods['subcategory_slug'] == 'cajas-vasos-para-llevar']['base_image_url'].head(5))
except Exception as e:
    print(f"Error reading products: {e}")
