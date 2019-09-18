import pandas as pd
import csv
from shop.models import Pack, Category, PacksPricing
from django.core.management.base import BaseCommand



tmp_data_packs_pricing=pd.read_csv('static/data/packs_pricing.csv',sep=',', encoding='iso-8859-1').fillna(" ")



class Command(BaseCommand):
    def handle(self, **options):
        packs_pricing = [
            PacksPricing(
                category=Category.objects.get(name=row['category']),
                pack=Pack.objects.get(name=row['pack']),
                size=row['size'],
                quantity=row['quantity'],
                price=row['price']
        )
            for _, row in tmp_data_packs_pricing.iterrows()
        ]

        PacksPricing.objects.bulk_create(packs_pricing)