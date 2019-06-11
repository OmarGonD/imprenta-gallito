import pandas as pd
import csv
from marketing.models import Cupons
from django.core.management.base import BaseCommand



tmp_data_coupons=pd.read_csv('static/data/coupons.csv',sep=',', encoding='iso-8859-1').fillna(" ")




class Command(BaseCommand):
    def handle(self, **options):
        cupones = [
            Cupons(
                cupon=row['cupon'],
                percentage=row['percentage'],
                hard_discount=row['hard_discount'],
                quantity=row['quantity'],
                start_date=row['start_date'],
                end_date=row['end_date'],
                active=row['active']
        )
            for _, row in tmp_data_coupons.iterrows()
        ]

        Cupons.objects.bulk_create(cupones)