import pandas as pd
try:
    df = pd.read_excel('D:/web_proyects/imprenta_gallito/products_complete.xlsx')
    print("Columns:", df.columns.tolist())
    print("First row:", df.iloc[0].to_dict())
except Exception as e:
    print(e)
