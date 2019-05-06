import pandas as pd
import csv
from shop.models import Sample, Category, SamplesPricing
from django.core.management.base import BaseCommand



tmp_data_samples_pricing=pd.read_csv('static/data/samples_pricing.csv',sep=',', encoding='iso-8859-1').fillna(" ")



class Command(BaseCommand):
    def handle(self, **options):
        samples_pricing = [
            SamplesPricing(
                category=Category.objects.get(name=row['category']),
                sample=Sample.objects.get(name=row['sample']),
                size=row['size'],
                quantity=row['quantity'],
                price=row['price']
        )
            for _, row in tmp_data_samples_pricing.iterrows()
        ]

        SamplesPricing.objects.bulk_create(samples_pricing)