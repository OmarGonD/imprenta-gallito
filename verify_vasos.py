import pandas as pd

excel_path = r'D:\web_proyects\imprenta_gallito\static\data\products_complete.xlsx'

try:
    df = pd.read_excel(excel_path)
    
    # Check vasos products
    vasos = df[df['subcategory_slug'] == 'vasos']
    
    if not vasos.empty:
        print(f"Total vasos products: {len(vasos)}")
        print("\nFirst 5 updated products:")
        print(vasos[['product_name', 'description']].head().to_string())
    else:
        print("No vasos found")
        
except Exception as e:
    print(f"Error: {e}")
