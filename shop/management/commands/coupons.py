import pandas as pd
import csv
from marketing.models import Cupons
from django.core.management.base import BaseCommand

# Read CSV, keep empty strings for manual handling
tmp_data_coupons = pd.read_csv(
    'static/data/coupons.csv',
    sep=',',
    encoding='iso-8859-1',
    keep_default_na=False
).fillna("")

class Command(BaseCommand):
    def handle(self, **options):
        def parse_number(val):
            val = str(val).strip()
            if val == "" or val == " ":
                return None
            try:
                # Try integer first, fallback to float
                if '.' in val:
                    return float(val)
                return int(val)
            except Exception:
                return None

        cupones = [
            Cupons(
                cupon=row['cupon'],
                percentage=parse_number(row['percentage']),
                hard_discount=parse_number(row['hard_discount']),
                quantity=parse_number(row['quantity']),
                start_date=row['start_date'],
                end_date=row['end_date'],
                active=row['active']
            )
            for _, row in tmp_data_coupons.iterrows()
        ]

        Cupons.objects.bulk_create(cupones)