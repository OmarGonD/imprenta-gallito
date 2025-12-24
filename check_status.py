
import pandas as pd

file_path = r'D:\web_proyects\imprenta_gallito\static\data\products_complete.xlsx'
try:
    df = pd.read_excel(file_path)
    print("Unique Statuses:", df['status'].unique())
    print("Sample SKUs:", df['sku'].head().tolist())
except Exception as e:
    print(e)
