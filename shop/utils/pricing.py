import csv
from decimal import Decimal
from django.conf import settings
import os


class PricingService:
    def __init__(self):
        self.price_tiers = self.load_price_tiers()

    def fix_mojibake(self, text):
        """Corrige caracteres mojibake (UTF-8 leído como Latin-1)."""
        if not isinstance(text, str):
            return text
        
        result = text
        for _ in range(3):
            try:
                fixed = result.encode('latin-1').decode('utf-8')
                if fixed == result:
                    break
                result = fixed
            except (UnicodeDecodeError, UnicodeEncodeError):
                break
        return result

    def detect_delimiter(self, filepath):
        """Detecta el delimitador del CSV (coma o punto y coma)."""
        with open(filepath, 'r', encoding='latin-1') as f:
            sample = f.read(2048)
            # Si hay más ; que , probablemente sea ;
            if sample.count(';') > sample.count(','):
                return ';'
            return ','

    def clean_key(self, key):
        """Limpia una clave de diccionario de caracteres invisibles y BOM."""
        if not key:
            return key
        # Eliminar BOM, espacios, y caracteres de control
        return key.strip().lstrip('\ufeff').strip()

    def load_price_tiers(self):
        filepath = os.path.join(settings.BASE_DIR, 'static', 'data', 'price_tiers_complete.csv')
        tiers = {}
        
        # Detectar delimitador
        delimiter = self.detect_delimiter(filepath)
        
        # Leer como Latin-1 (acepta cualquier byte, nunca falla)
        with open(filepath, 'r', encoding='latin-1') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            
            for row in reader:
                # Limpiar las claves del diccionario (por si tienen BOM o espacios)
                cleaned_row = {self.clean_key(k): v for k, v in row.items()}
                
                # Debug: si no encuentra la columna, mostrar qué columnas hay
                if 'product_slug' not in cleaned_row:
                    raise KeyError(
                        f"Columna 'product_slug' no encontrada. "
                        f"Columnas disponibles: {list(cleaned_row.keys())}. "
                        f"Delimitador detectado: '{delimiter}'"
                    )
                
                # Corregir encoding del slug si tiene caracteres especiales
                slug = self.fix_mojibake(cleaned_row['product_slug'].strip())
                
                if slug not in tiers:
                    tiers[slug] = []
                
                # Limpiar valores de espacios y \r
                min_q = cleaned_row['min_quan'].strip()
                max_q = cleaned_row['max_quan'].strip()
                price = cleaned_row['unit_price'].strip()
                discount = cleaned_row['discount_percent'].strip()
                    
                tiers[slug].append({
                    'min_quan': int(min_q),
                    'max_quan': int(max_q) if max_q != '999999' else 999999,
                    'unit_price': Decimal(price),
                    'discount_percent': int(discount)
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
