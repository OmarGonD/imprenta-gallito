import os
import pandas as pd
from pathlib import Path

# Mapping of directory names to subcategory slugs
DIRECTORY_TO_SUBCATEGORY = {
    'lapiceros': 'lapiceros',
    'llaveros': 'llaveros',
    'usb': 'usb',
    'termos': 'termos-botellas',
    'snacks_caramelos': 'snacks-caramelos',
    'tazas_vasos': 'tazas',  # Will handle both tazas and vasos
}

def get_subcategory_from_filename(directory, filename):
    """Determine subcategory from directory and filename."""
    base_subcategory = DIRECTORY_TO_SUBCATEGORY.get(directory, directory)
    
    # Special handling for tazas_vasos directory
    if directory == 'tazas_vasos':
        if 'vaso' in filename.lower():
            return 'vasos'
        else:
            return 'tazas'
    
    return base_subcategory

def create_product_name(subcategory_slug, filename):
    """Create a human-readable product name."""
    # Remove file extension and replace hyphens/underscores with spaces
    name = Path(filename).stem.replace('-', ' ').replace('_', ' ')
    # Capitalize each word
    name = ' '.join(word.capitalize() for word in name.split())
    return name

def create_product_slug(subcategory_slug, filename):
    """Create a product slug."""
    # Remove file extension
    slug = Path(filename).stem.lower()
    # Ensure it's URL-friendly
    slug = slug.replace('_', '-').replace(' ', '-')
    return slug

def main():
    # Paths
    images_base_path = r'D:\web_proyects\imprenta_gallito\static\media\product_images\productos_promocionales'
    excel_path = r'D:\web_proyects\imprenta_gallito\static\data\products_complete.xlsx'
    
    # Read existing Excel
    print(f"Reading Excel file: {excel_path}")
    df = pd.read_excel(excel_path)
    print(f"Current products in Excel: {len(df)}")
    print(f"Columns: {df.columns.tolist()}\n")
    
    # List to store new products
    new_products = []
    
    # Category slug for all promotional products
    category_slug = 'productos-promocionales'
    
    # Explore each subdirectory
    for subdir in os.listdir(images_base_path):
        subdir_path = os.path.join(images_base_path, subdir)
        
        if not os.path.isdir(subdir_path):
            continue
        
        print(f"Processing directory: {subdir}")
        
        # Get all image files in the subdirectory
        image_files = [f for f in os.listdir(subdir_path) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        
        print(f"  Found {len(image_files)} images")
        
        for image_file in image_files:
            # Determine subcategory
            subcategory_slug = get_subcategory_from_filename(subdir, image_file)
            
            # Create product details
            product_slug = create_product_slug(subcategory_slug, image_file)
            product_name = create_product_name(subcategory_slug, image_file)
            
            # Create base image URL (relative path from /media/)
            base_image_url = f"/media/product_images/productos_promocionales/{subdir}/{image_file}"
            
            # Create SKU
            sku = f"PROMO-{subcategory_slug.upper()}-{product_slug.upper()}"[:50]
            
            # Create description
            description = f"{product_name} - Producto promocional personalizable"
            
            # Create new product entry
            new_product = {
                'product_slug': product_slug,
                'product_name': product_name,
                'category_slug': category_slug,
                'subcategory_slug': subcategory_slug,
                'sku': sku,
                'description': description,
                'base_image_url': base_image_url
            }
            
            new_products.append(new_product)
            print(f"    + {product_name} ({subcategory_slug})")
    
    print(f"\nTotal new products to add: {len(new_products)}")
    
    # Create DataFrame from new products
    new_df = pd.DataFrame(new_products)
    
    # Combine with existing DataFrame
    # Only add columns that exist in the original DataFrame
    for col in df.columns:
        if col not in new_df.columns:
            new_df[col] = None
    
    # Reorder columns to match original DataFrame
    new_df = new_df[df.columns]
    
    # Append new products
    combined_df = pd.concat([df, new_df], ignore_index=True)
    
    print(f"\nTotal products after addition: {len(combined_df)}")
    
    # Save to Excel
    print(f"\nSaving to: {excel_path}")
    combined_df.to_excel(excel_path, index=False)
    print("✓ Excel file updated successfully!")
    
    # Display summary by subcategory
    print("\n=== Summary by Subcategory ===")
    new_summary = new_df['subcategory_slug'].value_counts()
    for subcategory, count in new_summary.items():
        print(f"  {subcategory}: {count} products")

if __name__ == "__main__":
    main()
