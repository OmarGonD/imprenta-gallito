import csv
from decimal import Decimal
from django.conf import settings
import os

class PricingService:
    def __init__(self):
        self.price_tiers = self.load_price_tiers()

    def load_price_tiers(self):
        filepath = os.path.join(settings.BASE_DIR, 'static', 'data', 'price_tiers_complete.csv')
        tiers = {}
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                slug = row['product_slug']
                if slug not in tiers:
                    tiers[slug] = []
                tiers[slug].append({
                    'min_quan': int(row['min_quan']),
                    'max_quan': int(row['max_quan']) if row['max_quan'] != '999999' else 999999,
                    'unit_price': Decimal(row['unit_price']),
                    'discount_percent': int(row['discount_percent'])
                })
        return tiers

    def get_pricing(self, product_slug, quantity):
        if product_slug not in self.price_tiers:
            return None  # or raise error

        all_tiers = sorted(self.price_tiers[product_slug], key=lambda t: t['min_quan'])
        
        current_tier = None
        for tier in all_tiers:
            if tier['min_quan'] <= quantity <= tier['max_quan']:
                current_tier = tier
                break
        
        if not current_tier:
            # If quantity exceeds all tiers, use the last one
            current_tier = all_tiers[-1]

        total_price = current_tier['unit_price'] * quantity

        next_tier = None
        next_index = all_tiers.index(current_tier) + 1
        if next_index < len(all_tiers):
            next_tier_data = all_tiers[next_index]
            units_needed = next_tier_data['min_quan'] - quantity
            if units_needed > 0:
                savings = (current_tier['unit_price'] - next_tier_data['unit_price']) * quantity
                next_tier = {
                    'min_quan': next_tier_data['min_quan'],
                    'max_quan': next_tier_data['max_quan'],
                    'unit_price': next_tier_data['unit_price'],
                    'discount_percent': next_tier_data['discount_percent'],
                    'units_needed': units_needed,
                    'savings': float(savings)
                }

        return {
            'quantity': quantity,
            'unit_price': float(current_tier['unit_price']),
            'discount_percent': current_tier['discount_percent'],
            'total_price': float(total_price),
            'current_tier': current_tier,
            'next_tier': next_tier,
            'all_tiers': all_tiers
        }
