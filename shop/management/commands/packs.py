import pandas as pd
import csv
from shop.models import Pack, Category
from django.core.management.base import BaseCommand



tmp_data_packs=pd.read_csv('static/data/packs.csv',sep=',', encoding='iso-8859-1').fillna(" ")




class Command(BaseCommand):
    def handle(self, **options):
        packs = [
            Pack(
                category=Category.objects.get(name=row['category']),
                subcategory=row['subcategory'],
                name=row['pack'],
                slug=row['slug'],
                sku=row['sku'],
                size=row['size'],
                quantity=row['quantity'],
                price=row['price'],
                description=row['description'],
                available=row['available']
        )
            for _, row in tmp_data_packs.iterrows()
        ]

        Pack.objects.bulk_create(packs)
