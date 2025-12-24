
import pandas as pd
import os
import random

def get_subcategory(filename):
    name = filename.lower()
    if any(x in name for x in ['estandar', 'matte', 'glossy', 'uncoated', 'recycled']):
        return 'estandar'
    elif any(x in name for x in ['bamboo', 'plastic', 'foil', 'raised', 'painted', 'thick', 'hemp']):
        return 'deluxe'
    else:
        return 'premium'

def run():
    base_dir = r"d:\web_proyects\imprenta_gallito"
    products_path = os.path.join(base_dir, 'static', 'data', 'products_complete.xlsx')
    images_dir = os.path.join(base_dir, 'static', 'media', 'product_images', 'tarjetas_presentacion')
    
    # Load existing
    df = pd.read_excel(products_path)
    print(f"Loaded {len(df)} existing products")
    
    # Remove existing tarjetas if any (just into case)
    df = df[df['category_slug'] != 'tarjetas-presentacion']
    print(f"After cleaning old tarjetas: {len(df)}")
    
    new_rows = []
    
    if not os.path.exists(images_dir):
        print("Images dir not found")
        return

    for filename in os.listdir(images_dir):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
            
        slug_base = os.path.splitext(filename)[0].replace('_', '-')
        product_slug = f"tarjetas-{slug_base}"
        subcategory_slug = get_subcategory(filename)
        
        name = slug_base.replace('-', ' ').title()
        
        row = {
            'product_slug': product_slug,
            'product_name': f"Tarjetas {name}",
            'category_slug': 'tarjetas-presentacion',
            'subcategory_slug': subcategory_slug,
            'sku': f"TP-{slug_base.upper()}-{random.randint(100,999)}",
            'description': f"Tarjetas de presentación con acabado {name}. Alta calidad y durabilidad.",
            'base_image_url': f"media/product_images/tarjetas_presentacion/{filename}",
            'status': 'active',
            'min_quantity': 100,
            'base_price': 50.00
        }
        new_rows.append(row)

    if new_rows:
        new_df = pd.DataFrame(new_rows)
        # Ensure columns match
        for col in df.columns:
            if col not in new_df.columns:
                new_df[col] = None
                
        df = pd.concat([df, new_df], ignore_index=True)
        print(f"Added {len(new_rows)} new products")
        
        # Save
        df.to_excel(products_path, index=False)
        print("Saved products_complete.xlsx")
    else:
        print("No images found to add")

if __name__ == "__main__":
    run()
