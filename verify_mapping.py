
import pandas as pd

# Load the generated file
df = pd.read_excel(r"D:\web_proyects\imprenta_gallito\static\data\products_complete.xlsx")

# Check for 'cajas-comida' subcategory
try:
    mapped_products = df[df['subcategory_slug'] == 'cajas-comida']
    print(f"Products in 'cajas-comida': {len(mapped_products)}")
    
    if not mapped_products.empty:
        print("Sample found:")
        print(mapped_products.iloc[0][['product_name', 'base_image_url', 'sku']])
    else:
        print("NO 'cajas-comida' products found!")
        
    # Double check no old slug exists
    old_slug = df[df['subcategory_slug'] == 'cajas-vasos-para-llevar']
    print(f"Products with old slug 'cajas-vasos-para-llevar': {len(old_slug)}")
    
except KeyError:
    print("Column 'subcategory_slug' not found")
