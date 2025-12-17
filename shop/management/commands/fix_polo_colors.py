import os
import pandas as pd
import django
from django.conf import settings
from decimal import Decimal

# Helper to run in django context if needed, or assume manage.py shell context
# We will run it with "python manage.py shell < fix_polo_colors.py" or similar?
# Better to make it a management command or a standalone script that does setup.
# But since I can use "run_command" with python, I'll make it a management command for simplicity of context.

from django.core.management.base import BaseCommand
from shop.models import Product, ProductOption, ProductOptionValue, ProductVariant

class Command(BaseCommand):
    help = 'Fixes polo colors from Excel'

    def handle(self, *args, **options):
        self.stdout.write("STARTING FIX POLO COLORS")
        
        filepath = os.path.join(settings.BASE_DIR, 'static', 'data', 'products_complete.xlsx')
        if not os.path.exists(filepath):
            self.stdout.write(f"Error: {filepath} not found")
            return

        df = pd.read_excel(filepath)
        
        try:
            color_opt = ProductOption.objects.get(key='color')
        except ProductOption.DoesNotExist:
            self.stdout.write("Error: Color option not found")
            return

        polos_fixed = 0
        
        # Normalize column names just in case
        df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
        
        target_col = 'colores_hex'
        if 'colores_hex' not in df.columns:
            if 'available_colors' in df.columns:
                target_col = 'available_colors'
            else:
                 self.stdout.write("Error: 'colores_hex' or 'available_colors' column not found")
                 self.stdout.write(f"Columns: {df.columns.tolist()}")
                 return

        processed_count = 0
        for _, row in df.iterrows():
            processed_count += 1
            slug = str(row.get('product_slug', '')).strip()
            name = str(row.get('product_name', '')).strip()
            
            if 'polo' in slug.lower() or 'polo' in name.lower():
                self.stdout.write(f"DEBUG MATCH: Slug='{slug}', Name='{name}'")
                colors_str = row.get(target_col)
                
                if pd.isna(colors_str) or not colors_str:
                    self.stdout.write(f"Skipping {slug}: No colors")
                    continue
                
                self.stdout.write(f"Processing {slug} with colors: {colors_str}")
                
                # Parse colors
                # Format: slug:hex|slug:hex
                active_values = []
                
                parts_list = str(colors_str).split('|')
                self.stdout.write(f"  Split into {len(parts_list)} items: {parts_list}")
                
                for item in parts_list:
                    if ':' in item:
                        parts = item.split(':', 1)
                        if len(parts) == 2:
                            c_slug = parts[0].strip()
                            c_hex = parts[1].strip()
                            self.stdout.write(f"    Found: {c_slug} -> {c_hex}")
                            
                            if not c_hex.startswith('#'):
                                c_hex = f'#{c_hex}'
                                
                            # Get or create value
                            val, created = ProductOptionValue.objects.get_or_create(
                                option=color_opt,
                                value=c_slug,
                                defaults={
                                    'display_name': c_slug.replace('-', ' ').title(),
                                    'hex_code': c_hex,
                                    'is_active': True,
                                    'display_order': 0
                                }
                            )
                            active_values.append(val)
                
                if matched_count > 0: # Stop after 1 match for debug
                     raise Exception("DEBUG HALT")
                
                if active_values:
                    # Update variant
                    variant, _ = ProductVariant.objects.get_or_create(
                        product=Product.objects.get(slug=slug),
                        option=color_opt,
                        defaults={'display_order': 1}
                    )
                    variant.available_values.set(active_values)
                    self.stdout.write(f"  Updated variant with {len(active_values)} colors")
                    polos_fixed += 1
        
        self.stdout.write(f"DONE. Fixed {polos_fixed} polos.")
