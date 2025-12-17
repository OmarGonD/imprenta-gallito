import os
import pandas as pd
import django
from django.conf import settings

# Setup Django environment manually if run directly, though we'll use 'python manage.py shell < script' style or custom command
# Just implementing as a command is easier
from django.core.management.base import BaseCommand
from shop.models import Product

class Command(BaseCommand):
    help = 'Generates polo_imagenes_colores.xlsx from file system'

    def handle(self, *args, **options):
        self.stdout.write("Generating Excel...")
        
        # 1. Directory Config
        # Based on user info: D:\web_proyects\imprenta_gallito\static\media\product_images\ropa_y_bolsos\polos
        img_dir = os.path.join(settings.BASE_DIR, 'static', 'media', 'product_images', 'ropa_y_bolsos', 'polos')
        
        if not os.path.exists(img_dir):
            self.stdout.write(f"Error: Directory not found: {img_dir}")
            return

        # 2. Get Product Slugs
        # Filter for products that are likely in this directory (ropa-bolsos)
        products = Product.objects.filter(category__slug='ropa-bolsos')
        product_slugs = [p.slug for p in products]
        
        # Sort by length desc to match longest slug first (greedy matching)
        product_slugs.sort(key=len, reverse=True)
        
        self.stdout.write(f"Found {len(product_slugs)} products to match against.")

        data = []
        files = sorted([f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        
        matched_count = 0
        unmatched_count = 0

        for filename in files:
            # Remove extension
            name_no_ext = os.path.splitext(filename)[0]
            
            matched_slug = None
            color_slug = None
            
            # Find matching product slug
            for slug in product_slugs:
                # Expect slug + '-' + color
                prefix = slug + '-'
                if name_no_ext.startswith(prefix):
                    matched_slug = slug
                    # Extract remainder as color
                    color_part = name_no_ext[len(prefix):]
                    color_slug = color_part
                    break
            
            if matched_slug:
                # Construct URL
                # Assuming /media/product_images/ropa_y_bolsos/polos/filename
                # Adjust if your MEDIA_URL setup is different
                image_url = f"/media/product_images/ropa_y_bolsos/polos/{filename}"
                
                data.append({
                    'product_slug': matched_slug,
                    'image_url': image_url,
                    'color_slug': color_slug,
                    'is_primary': False, # Update logic later if needed
                    'display_order': 0
                })
                matched_count += 1
            else:
                unmatched_count += 1
                # self.stdout.write(f"Unmatched: {filename}")

        self.stdout.write(f"Matched: {matched_count}, Unmatched: {unmatched_count}")
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Output path
        output_file = os.path.join(settings.BASE_DIR, 'static', 'data', 'polo_imagenes_colores.xlsx')
        df.to_excel(output_file, index=False)
        self.stdout.write(f"Saved to {output_file}")
