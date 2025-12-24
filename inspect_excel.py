
import pandas as pd
import os

file_path = r'D:\web_proyects\imprenta_gallito\static\data\products_complete.xlsx'

try:
    df = pd.read_excel(file_path)
    print("Columns:", df.columns.tolist())
    print("\nFirst 5 rows:")
    print(df.head().to_string())
    
    # Check for similar category if exists
    print("\nChecking for existing 'vasos' in 'productos_promocionales':")
    existing = df[(df['category_slug'] == 'productos_promocionales') & (df['subcategory_slug'] == 'vasos')]
    if not existing.empty:
        print(existing.head().to_string())
    else:
        print("No existing entries found.")
        
except Exception as e:
    print(f"Error reading excel: {e}")
