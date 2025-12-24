import pandas as pd

excel_path = r'D:\web_proyects\imprenta_gallito\static\data\products_complete.xlsx'

try:
    df = pd.read_excel(excel_path)
    
    # Check all vasos products
    vasos = df[df['subcategory_slug'] == 'vasos'].copy()
    
    if not vasos.empty:
        print(f"✅ Total vasos products: {len(vasos)}\n")
        print("=" * 80)
        print("UPDATED PRODUCTS:")
        print("=" * 80)
        
        for idx, row in vasos.head(10).iterrows():
            print(f"\n{row['product_name']}")
            print(f"  Description: {row['description'][:100]}...")
            print(f"  SKU: {row['sku']}")
    else:
        print("❌ No vasos found")
        
except Exception as e:
    print(f"Error: {e}")
