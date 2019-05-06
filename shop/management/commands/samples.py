import pandas as pd
import csv
from shop.models import Product, Category, Sample
from django.core.management.base import BaseCommand



tmp_data_samples=pd.read_csv('static/data/samples.csv',sep=',', encoding='iso-8859-1').fillna(" ")




class Command(BaseCommand):
    def handle(self, **options):
        samples = [
            Sample(
                category=Category.objects.get(name=row['category']),
                name=row['sample'],
                slug=row['slug'],
                description=row['description'],
                available=row['available']
        )
            for _, row in tmp_data_samples.iterrows()
        ]

        Sample.objects.bulk_create(samples)