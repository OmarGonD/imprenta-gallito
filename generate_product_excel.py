import os
import pandas as pd

def generate_product_excel():
    # Define path
    BASE_DIR = r"D:\web_proyects\imprenta_gallito"
    IMAGES_REL_PATH = r"static\media\product_images\letreros_banners"
    ROOT_PATH = os.path.join(BASE_DIR, IMAGES_REL_PATH)
    
    # Check if path exists
    if not os.path.exists(ROOT_PATH):
        print(f"Error: Path {ROOT_PATH} does not exist.")
        return

    data = []

    # Walk through the directory
    for root, dirs, files in os.walk(ROOT_PATH):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                # Calculate paths
                full_path = os.path.join(root, file)
                rel_path_from_images = os.path.relpath(full_path, ROOT_PATH)
                
                # Extract metadata
                subcategory_slug = os.path.dirname(rel_path_from_images)
                
                # Skip files in the root folder if any (or assign a default subcat)
                if subcategory_slug == '.':
                    continue # Skipping root files as per "subdirectorio + nombre de archivo" implication
                
                category_slug = "letreros-banners"
                
                filename_no_ext = os.path.splitext(file)[0]
                product_slug = filename_no_ext.lower().replace(' ', '-')
                
                # Product Name: Title case, replace hyphens/underscores with spaces
                product_name = filename_no_ext.replace('-', ' ').replace('_', ' ').title()
                
                sku = "" # Empty as requested/default
                description = "" # Empty as requested/default
                
                # Base Image URL
                # Path relative to static/media/..., ensuring forward slashes
                # Construct path: /media/product_images/letreros_banners/<subdir>/<file>
                
                # Note: os.path.join with 'media' might use backslashes on Windows.
                # We need forced forward slashes.
                
                # Get path relative to the media root conceptually
                # "letreros_banners" is inside "product_images", which is inside "media" (in "static/media"?)
                # Wait, user path: ...\static\media\product_images\letreros_banners
                # Request: "base_image_url que sea solo a partir de /media/..."
                
                # So we want /media/product_images/letreros_banners/subdir/file.ext
                
                # Let's construct it manually to be safe
                web_path = f"/media/product_images/letreros_banners/{subcategory_slug}/{file}"
                web_path = web_path.replace("\\", "/") # Ensure forward slashes
                
                data.append({
                    "product_slug": product_slug,
                    "product_name": product_name,
                    "category_slug": category_slug,
                    "subcategory_slug": subcategory_slug,
                    "sku": sku,
                    "description": description,
                    "base_image_url": web_path
                })

    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to Excel
    output_file = "products_letreros_banners.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Excel file created: {os.path.abspath(output_file)}")
    print(f"Total records: {len(df)}")

if __name__ == "__main__":
    generate_product_excel()
