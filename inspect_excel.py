import pandas as pd
import os
from django.conf import settings

# Setup Django (although purely for path access, not needed if we use absolute path)
# But let's just use the absolute path directly for simplicity in this script run
base_path = r'd:\web_proyects\imprenta_gallito\static\data'
filename = 'products_complete.xlsx'
filepath = os.path.join(base_path, filename)

print(f"Reading {filepath}...")
try:
    df = pd.read_excel(filepath)
    print("\nALL COLUMNS:")
    print(df.columns.tolist())
    
    # Filter for specific product
    polos = df[df['product_slug'].astype(str).str.contains('gildan-r-softstyle-r-unisex-t-shirt', case=False, na=False)]
    
    if not polos.empty:
        print(f"\nFOUND {len(polos)} POLOS.")
        row = polos.iloc[0]
        print(f"available_colors: {row.get('available_colors')}")
        print(f"colores_hex: {row.get('colores_hex')}")
    else:
        print("\nNO POLOS FOUND IN THIS FILE.")
except Exception as e:
    print(f"Error: {e}")
