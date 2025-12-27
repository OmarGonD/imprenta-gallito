import os
import pandas as pd
import math
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from shop.utils.smart_pricing_config import SMART_PRICING_RULES

class Command(BaseCommand):
    help = 'Generates price_tiers_complete.xlsx based on smart pricing rules.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing price tiers even if they were manually edited.'
        )

    def handle(self, *args, **options):
        self.force = options['force']
        self.data_dir = os.path.join(settings.BASE_DIR, 'static', 'data')
        
        # Files
        products_file = os.path.join(self.data_dir, 'products_complete.xlsx')
        pricing_file = os.path.join(self.data_dir, 'price_tiers_complete.xlsx')
        
        if not os.path.exists(products_file):
            self.stdout.write(self.style.ERROR(f'Products file not found: {products_file}'))
            return

        # Read Products
        self.stdout.write(f'Reading {products_file}...')
        df_products = pd.read_excel(products_file)
        
        # Read Existing Pricing (to preserve manual edits)
        existing_tiers = {} # {(product_slug, min_qty): row_data}
        if os.path.exists(pricing_file):
            self.stdout.write(f'Reading existing prices form {pricing_file}...')
            df_existing = pd.read_excel(pricing_file)
            for _, row in df_existing.iterrows():
                try:
                    slug = str(row['product_slug']).strip()
                    min_q = int(row['min_quantity'])
                    existing_tiers[(slug, min_q)] = row
                except:
                    continue
        
        new_rows = []
        
        # Iterate Products
        for _, prod_row in df_products.iterrows():
            product_slug = str(prod_row['product_slug']).strip()
            category_slug = str(prod_row['category_slug']).strip()
            
            # Check if category has smart pricing rules
            rule = SMART_PRICING_RULES.get(category_slug)
            
            if not rule:
                # If no rule, but exists in previous file, keep it
                # Logic: iterate existing_tiers matching this product
                for key, data in existing_tiers.items():
                    if key[0] == product_slug:
                         new_rows.append(data)
                continue

            self.stdout.write(f'Running Smart Pricing for: {product_slug} ({category_slug})')
            
            # --- LOGIC: ROPA-BOLSOS ---
            if rule.get('logic_type') == 'tiered_margin':
                tiers = rule['tiers']
                for tier in tiers:
                    min_q = tier['min']
                    price = tier['price']
                    
                    # Manual Override Check
                    if not self.force and (product_slug, min_q) in existing_tiers:
                        # Keep existing
                        new_rows.append(existing_tiers[(product_slug, min_q)])
                    else:
                        # New / Overwrite
                        new_rows.append({
                            'product_slug': product_slug,
                            'min_quantity': min_q,
                            'max_quantity': 999999 if min_q == 500 else (11 if min_q == 1 else (49 if min_q == 12 else (99 if min_q == 50 else (499 if min_q == 100 else 999)))), # Approximate logic from script
                            'unit_price': float(price),
                            'discount_percentage': 0 # Calculated later or left 0
                        })
                        
            # --- LOGIC: STICKERS-ETIQUETAS ---
            elif rule.get('logic_type') == 'cost_plus_fixed':
                # Determine Variant Size from Slug
                variant_data = None
                for size_key, v_data in rule['variants'].items():
                    if size_key in product_slug:
                        variant_data = v_data
                        break
                
                if not variant_data:
                    self.stdout.write(self.style.WARNING(f'   Skipping {product_slug}: No size match found in rules.'))
                    continue
                
                # Calculation Params
                full_units = variant_data['full_units']
                half_units = variant_data['half_units']
                unit_markup = float(variant_data['unit_markup'])
                
                full_cost = float(rule['params']['full_batch_cost'])
                half_cost = float(rule['params']['half_batch_cost'])
                mgmt_fee = float(rule['params']['management_fee'])
                
                for qty in rule['quantities']:
                    # 1. Calculate Real Cost
                    num_full = qty // full_units
                    rem = qty % full_units
                    
                    real_cost = num_full * full_cost
                    if rem > 0:
                        real_cost += half_cost if rem <= half_units else full_cost
                        
                    # 2. Smart Price
                    variable_profit = unit_markup * qty
                    smart_price = real_cost + mgmt_fee + variable_profit
                    
                    # Rounding
                    final_price = math.ceil(smart_price * 2) / 2
                    unit_price = final_price / qty
                    
                     # Manual Override Check
                    if not self.force and (product_slug, qty) in existing_tiers:
                        new_rows.append(existing_tiers[(product_slug, qty)])
                    else:
                         new_rows.append({
                            'product_slug': product_slug,
                            'min_quantity': qty,
                            'max_quantity': qty, # Exact quantity for stickers usually
                            'unit_price': round(unit_price, 4),
                            'discount_percentage': 0
                        })

        # Create DataFrame
        df_new = pd.DataFrame(new_rows)
        
        # Sort and Save
        if not df_new.empty:
            df_new = df_new[['product_slug', 'min_quantity', 'max_quantity', 'unit_price', 'discount_percentage']]
            df_new.sort_values(by=['product_slug', 'min_quantity'], inplace=True)
            
            # Backup
            if os.path.exists(pricing_file):
                backup_path = pricing_file.replace('.xlsx', '_backup.xlsx')
                pd.read_excel(pricing_file).to_excel(backup_path, index=False)
                self.stdout.write(f'Backup created: {backup_path}')
            
            # Save
            df_new.to_excel(pricing_file, index=False)
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {pricing_file}'))
        else:
             self.stdout.write(self.style.WARNING('No pricing rows generated.'))
