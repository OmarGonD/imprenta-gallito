import pandas as pd
import os

FILE_PATH = 'static/data/products_complete.xlsx'
try:
    df = pd.read_excel(FILE_PATH)
    print(f"Rows: {len(df)}")
    print("Columns:", df.columns.tolist())
    # Check for our slug
    found = df[df['product_slug'].astype(str).str.contains('polo-tumba')]
    if not found.empty:
        print("FOUND polo-tumba!")
        print(found[['product_slug', 'is_pre_designed']])
    else:
        print("NOT FOUND polo-tumba")
except Exception as e:
    print(f"Error: {e}")
