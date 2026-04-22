import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'static', 'data')
FILE_PATH = os.path.join(DATA_DIR, 'products_complete.xlsx')

print(f"Reading from: {FILE_PATH}")

# Read existing Excel
try:
    df = pd.read_excel(FILE_PATH)
    print(f"Loaded {len(df)} existing products.")
except FileNotFoundError:
    print("Error: products_complete.xlsx not found.")
    exit(1)

# Definition of Pre-designed Products
new_products = [
    {
        'product_slug': 'polo-tumba-vacia',
        'product_name': 'Polo Tumba Vacía',
        'category_slug': 'ropa-bolsos',
        'subcategory_slug': 'polos-hombre', # Assuming generic unisesx or mapping to hombre
        'sku': 'PRE-TUMBA',
        'description': 'Polo de algodón con diseño cristiano moderno.',
        'base_image_url': '',
        'status': 'active',
        'is_pre_designed': True,
        'skip_customization': True,
        'design_text': 'No le temo a la muerte. Mi tumba ya está vacía.',
        'design_reference': 'Mateo 28:6',
        'design_image': 'media/products/predesigned/polo_tumba_vacia.png',
        'available_colors': 'negro:#000000'
    },
    {
        'product_slug': 'polo-noe-conspiranoico',
        'product_name': 'Polo Noé Conspiranoico',
        'category_slug': 'ropa-bolsos',
        'subcategory_slug': 'polos-hombre',
        'sku': 'PRE-NOE',
        'description': 'Polo divertido sobre Noé y el diluvio.',
        'base_image_url': '',
        'status': 'active',
        'is_pre_designed': True,
        'skip_customization': True,
        'design_text': 'Noé era conspiranoico... hasta que empezó a llover.',
        'design_reference': 'Génesis 7',
        'design_image': 'media/products/predesigned/polo_noe_conspiranoico.png',
        'available_colors': 'blanco:#ffffff'
    },
     {
        'product_slug': 'polo-referentes-carcel',
        'product_name': 'Polo Referentes Cárcel',
        'category_slug': 'ropa-bolsos',
        'subcategory_slug': 'polos-hombre',
        'sku': 'PRE-REFERENTES',
        'description': 'Diseño inspirado en personajes bíblicos.',
        'base_image_url': '',
        'status': 'active',
        'is_pre_designed': True,
        'design_text': 'Mis referentes pasaron por la cárcel. Jesús. Pedro. Daniel. Juan.',
        'design_reference': '',
        'design_image': 'media/products/predesigned/placeholder.png', # Placeholder
        'available_colors': 'negro:#000000'
    },
    {
        'product_slug': 'polo-body-piercing',
        'product_name': 'Polo Body Piercing',
        'category_slug': 'ropa-bolsos',
        'subcategory_slug': 'polos-hombre',
        'sku': 'PRE-PIERCING',
        'description': 'Diseño juvenil estilo grunge.',
        'base_image_url': '',
        'status': 'active',
        'is_pre_designed': True,
        'design_text': 'Body piercing saved my life.',
        'design_reference': '',
        'design_image': 'media/products/predesigned/placeholder.png',
        'available_colors': 'negro:#000000'
    },
    {
        'product_slug': 'polo-stalkear-jesus',
        'product_name': 'Polo Stalkear Jesús',
        'category_slug': 'ropa-bolsos',
        'subcategory_slug': 'polos-hombre',
        'sku': 'PRE-STALK',
        'description': 'Pregunta provocadora sobre el seguimiento a Jesús.',
        'base_image_url': '',
        'status': 'active',
        'is_pre_designed': True,
        'design_text': '¿Sigues a Jesús… o solo lo stalkeas?',
        'design_reference': '',
        'design_image': 'media/products/predesigned/placeholder.png',
        'available_colors': 'blanco:#ffffff'
    },
     {
        'product_slug': 'polo-no-seas-presa',
        'product_name': 'Polo No Seas Presa',
        'category_slug': 'ropa-bolsos',
        'subcategory_slug': 'polos-hombre',
        'sku': 'PRE-PRESA',
        'description': 'Alerta sobre los peligros espirituales.',
        'base_image_url': '',
        'status': 'active',
        'is_pre_designed': True,
        'design_text': 'No seas presa. Hay leones sueltos.',
        'design_reference': '1 Pedro 5:8',
        'design_image': 'media/products/predesigned/placeholder.png',
        'available_colors': 'negro:#000000'
    },
    {
        'product_slug': 'polo-cancelado',
        'product_name': 'Polo Cancelado',
        'category_slug': 'ropa-bolsos',
        'subcategory_slug': 'polos-hombre',
        'sku': 'PRE-CANCEL',
        'description': 'Sobre la cultura de la cancelación.',
        'base_image_url': '',
        'status': 'active',
        'is_pre_designed': True,
        'design_text': 'Me cancelaron antes de que “cancelar” existiera.',
        'design_reference': '',
        'design_image': 'media/products/predesigned/placeholder.png',
        'available_colors': 'negro:#000000'
    },
    {
        'product_slug': 'polo-terapeuta',
        'product_name': 'Polo Terapeuta',
        'category_slug': 'ropa-bolsos',
        'subcategory_slug': 'polos-hombre',
        'sku': 'PRE-TERAPEUTA',
        'description': 'Comparación entre terapeutas humanos y divino.',
        'base_image_url': '',
        'status': 'active',
        'is_pre_designed': True,
        'design_text': 'Mi terapeuta venció a la muerte. ¿El tuyo qué certificaciones tiene?',
        'design_reference': '',
        'design_image': 'media/products/predesigned/placeholder.png',
        'available_colors': 'blanco:#ffffff'
    },
    {
        'product_slug': 'polo-suerte-cruz',
        'product_name': 'Polo Suerte Cruz',
        'category_slug': 'ropa-bolsos',
        'subcategory_slug': 'polos-hombre',
        'sku': 'PRE-SUERTE',
        'description': 'Fe sobre suerte.',
        'base_image_url': '',
        'status': 'active',
        'is_pre_designed': True,
        'design_text': 'No creo en la suerte. Creo en una cruz y una promesa.',
        'design_reference': '',
        'design_image': 'media/products/predesigned/placeholder.png',
        'available_colors': 'negro:#000000'
    },
    {
        'product_slug': 'polo-fin-domingo',
        'product_name': 'Polo Fin Domingo',
        'category_slug': 'ropa-bolsos',
        'subcategory_slug': 'polos-hombre',
        'sku': 'PRE-DOMINGO',
        'description': 'Esperanza en la resurrección.',
        'base_image_url': '',
        'status': 'active',
        'is_pre_designed': True,
        'design_text': 'El mundo dijo “fin”. Dios dijo “domingo”.',
        'design_reference': '',
        'design_image': 'media/products/predesigned/placeholder.png',
        'available_colors': 'blanco:#ffffff'
    }
]

# Convert to DataFrame
new_df = pd.DataFrame(new_products)

# Ensure columns exist in target df
for col in new_df.columns:
    if col not in df.columns:
        print(f"Adding new column: {col}")
        df[col] = None

# Filter out existing pre-designed products to avoid duplicates if re-run
existing_slugs = df['product_slug'].astype(str).tolist()
new_df = new_df[~new_df['product_slug'].isin(existing_slugs)]

if new_df.empty:
    print("No new products to add (all slugs already exist).")
else:
    # Append
    print(f"Appending {len(new_df)} new products...")
    df = pd.concat([df, new_df], ignore_index=True)
    
    # Save back
    try:
        df.to_excel(FILE_PATH, index=False)
        print("Successfully updated products_complete.xlsx")
    except Exception as e:
        print(f"Error saving Excel: {e}")
