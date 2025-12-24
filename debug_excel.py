
import pandas as pd

excel_path = r'D:\web_proyects\imprenta_gallito\static\data\products_complete.xlsx'

try:
    df = pd.read_excel(excel_path)
    
    # Filter just by subcategory
    vasos = df[df['subcategory_slug'] == 'vasos']
    
    print(f"Rows with subcategory_slug='vasos': {len(vasos)}")
    if not vasos.empty:
        print("Sample Category Slugs:")
        print(vasos['category_slug'].unique())
        print("First row category slug repr:", repr(vasos.iloc[0]['category_slug']))

except Exception as e:
    print(e)
