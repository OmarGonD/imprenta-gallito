import pandas as pd
import csv
from shop.models import Product, Category
from django.core.management.base import BaseCommand



tmp_data_products=pd.read_csv('static/data/products.csv',sep=',', encoding='iso-8859-1').fillna(" ")




class Command(BaseCommand):
    def handle(self, **options):
        products = [
            Product(
                category=Category.objects.get(name=row['category']),
                name=row['product'],
                slug=row['slug'],
                description=row['description'],
                available=row['available']
        )
            for _, row in tmp_data_products.iterrows()
        ]

        Product.objects.bulk_create(products)