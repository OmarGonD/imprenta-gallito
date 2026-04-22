import pandas as pd
import os

FILE_PATH = 'static/data/products_complete.xlsx'

def update_images():
    try:
        df = pd.read_excel(FILE_PATH)
        print(f"Loaded {len(df)} products.")
        
        updates = {
            'polo-fin-domingo': 'media/products/predesigned/polo_fin_domingo.png',
            'polo-no-seas-presa': 'media/products/predesigned/polo_no_seas_presa.png'
        }
        
        count = 0
        for slug, image_path in updates.items():
            mask = df['product_slug'] == slug
            if mask.any():
                df.loc[mask, 'design_image'] = image_path
                print(f"Updated {slug} -> {image_path}")
                count += 1
            else:
                print(f"Slug not found: {slug}")
        
        if count > 0:
            df.to_excel(FILE_PATH, index=False)
            print("Successfully saved excel.")
        else:
            print("No updates made.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_images()
