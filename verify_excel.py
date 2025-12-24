
import pandas as pd

excel_path = r'D:\web_proyects\imprenta_gallito\static\data\products_complete.xlsx'
try:
    df = pd.read_excel(excel_path)
    print("Total rows:", len(df))
    print("Last 5 rows:")
    print(df.tail().to_string())
except Exception as e:
    print(e)
