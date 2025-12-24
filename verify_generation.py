
import pandas as pd

# Load the generated file
df = pd.read_excel(r"D:\web_proyects\imprenta_gallito\static\data\products_complete.xlsx")

# Check for specific nested products
# We expect products from packaging_alimentario/cajas_vasos_para_llevar/bolsas_para_llevar to have subcategory 'cajas-vasos-para-llevar'
# and the base_image_url should contain 'bolsas_para_llevar' if it's preserving the structure, 
# OR the product_slug should reflect the file names.

print(f"Total rows: {len(df)}")

# Filter for the subcategory
nested_sub = df[df['subcategory_slug'] == 'cajas-vasos-para-llevar']
print(f"Products in 'cajas-vasos-para-llevar': {len(nested_sub)}")

# Check for any URL containing 'bolsas_para_llevar' to confirm recursion worked
recursive_match = df[df['base_image_url'].str.contains('bolsas_para_llevar', na=False)]
print(f"Products with 'bolsas_para_llevar' in path: {len(recursive_match)}")

if not recursive_match.empty:
    print("Sample found:")
    print(recursive_match.iloc[0][['product_name', 'base_image_url', 'sku']])
else:
    print("NO nested products found!")
