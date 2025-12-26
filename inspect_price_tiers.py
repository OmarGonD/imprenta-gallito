import pandas as pd
import os

file_path = os.path.join('static', 'data', 'price_tiers_complete.xlsx')
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    print(list(df.columns))
    print(df.head(5).to_dict('records'))
    
    # Check for any existing clothing items to copy their tiers
    clothing_tiers = df[df['product_slug'].str.contains('polo', na=False)]
    if not clothing_tiers.empty:
        print("\n--- Example Clothing Tiers ---")
        print(clothing_tiers.head(5).to_dict('records'))
else:
    print("File not found.")
