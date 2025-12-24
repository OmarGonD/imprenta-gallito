import pandas as pd

excel_path = r'D:\web_proyects\imprenta_gallito\static\data\products_complete.xlsx'

try:
    df = pd.read_excel(excel_path)
    
    # Check snacks products
    snacks = df[df['subcategory_slug'] == 'snacks-caramelos']
    
    if not snacks.empty:
        print(f"✅ Total snacks products: {len(snacks)}\n")
        print("=" * 80)
        print("SAMPLE UPDATED PRODUCTS (First 10):")
        print("=" * 80)
        
        for idx, row in snacks.head(10).iterrows():
            print(f"\n{row['product_name']}")
            print(f"  SKU: {row['sku']}")
            print(f"  Desc: {row['description'][:80]}...")
    else:
        print("❌ No snacks products found")
        
except Exception as e:
    print(f"Error: {e}")
