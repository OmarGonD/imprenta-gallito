import pandas as pd
import os

data_dir = os.path.join('static', 'data')
files = ['subcategories_complete.xlsx', 'products_complete.xlsx']

for f in files:
    path = os.path.join(data_dir, f)
    if os.path.exists(path):
        print(f"--- {f} ---")
        try:
            df = pd.read_excel(path)
            print(list(df.columns))
            print(df.head(1).to_dict('records'))
        except Exception as e:
            print(f"Error reading {f}: {e}")
    else:
        print(f"{f} not found.")
