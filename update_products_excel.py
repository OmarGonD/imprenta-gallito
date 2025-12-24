import pandas as pd
import os

products_data = []

# Dynamically generate product entries from postales_publicidad images
base_dir = os.path.join('static', 'media', 'product_images', 'postales_publicidad')
image_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
subcategory_counters = {}

for root, dirs, files in os.walk(base_dir):
    rel_path = os.path.relpath(root, base_dir)
    if rel_path == '.' or rel_path == '..':
        continue  # Skip base directory itself
    subcategory_slug = rel_path.replace('_', '-').replace('\\', '/').strip('/')
    if subcategory_slug not in subcategory_counters:
        subcategory_counters[subcategory_slug] = 1
    for file in files:
        if not file.lower().endswith(image_extensions):
            continue
        filename_no_ext = os.path.splitext(file)[0]
        product_name = filename_no_ext.replace('_', ' ').replace('-', ' ').title()
        product_slug = filename_no_ext.lower().replace(' ', '-').replace('_', '-')
        sku = f"POSTALES-{subcategory_slug.upper().replace('-', '_')}-{subcategory_counters[subcategory_slug]:03d}"
        description = f"¡Descubre nuestra postal {product_name} que captura la esencia de tu mensaje!"
        base_image_url = f"/static/media/product_images/postales_publicidad/{subcategory_slug}/{file}".replace('\\', '/')
        products_data.append({
            'category_slug': 'postales-publicidad',
            'subcategory_slug': subcategory_slug,
            'product_name': product_name,
            'product_slug': product_slug,
            'sku': sku,
            'description': description,
            'base_image_url': base_image_url,
        })
        subcategory_counters[subcategory_slug] += 1

file_path = os.path.join('static', 'data', 'products_complete.xlsx')

print(f"Checking for file at: {file_path}")

if not os.path.exists(file_path):
    print(f"Error: {file_path} does not exist.")
    # Debug listing of static/data
    static_data = os.path.join('static', 'data')
    if os.path.exists(static_data):
        print(f"Files in {static_data}:")
        for f in os.listdir(static_data):
            print(f" - {f}")
    else:
        print(f"Directory {static_data} does not exist!")
    exit(1)

print(f"Loading {file_path}...")
df = pd.read_excel(file_path)

# Create a set of existing slugs for faster lookup
existing_slugs = set(df['product_slug'].astype(str).values)

new_rows = []
for p in products_data:
    if p['product_slug'] in existing_slugs:
        print(f"Product {p['product_slug']} already exists. Skipping.")
    else:
        print(f"Adding product: {p['product_name']}")
        # Create a new row matching formatting of existing DF
        new_row = {
            'product_id': None, # Let DB handle ID or leave empty
            'category_slug': p['category_slug'],
            'subcategory_slug': p['subcategory_slug'],
            'product_name': p['product_name'],
            'product_slug': p['product_slug'],
            'sku': p['sku'],
            'description': p['description'],
            'base_image_url': p['base_image_url'],
            'status': 'active',
            'is_featured': False,
            'is_new': True,
            'stock': 100,
            'display_order': 0
        }
        # Add any other columns present in df with default values
        for col in df.columns:
            if col not in new_row:
                new_row[col] = None 
        
        new_rows.append(new_row)

if new_rows:
    new_df = pd.DataFrame(new_rows)
    df = pd.concat([df, new_df], ignore_index=True)
    
    try:
        df.to_excel(file_path, index=False)
        print("Successfully saved updated products_complete.xlsx")
    except Exception as e:
        print(f"Error saving file: {e}")
        # Try saving to a temporary file if locked
        try:
           temp_file = 'products_complete_updated.xlsx'
           df.to_excel(temp_file, index=False)
           print(f"Saved to {temp_file} instead due to lock error.")
        except Exception as e2:
           print(f"Critical error: {e2}")
else:
    print("No new products to add.")
