import pandas as pd
import csv
from shop.models import Product, Category
from django.core.management.base import BaseCommand



tmp_data_categories=pd.read_csv('static/data/categories.csv',sep=',', encoding='iso-8859-1').fillna(" ")




class Command(BaseCommand):
    def handle(self, **options):
        categories = [
            Category(
                name=row['category'],
                slug=row['slug'],
                description=row['description'],
                image=row['image']
        )
            for _, row in tmp_data_categories.iterrows()
        ]

        Category.objects.bulk_create(categories)
