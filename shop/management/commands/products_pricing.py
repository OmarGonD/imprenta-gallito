import pandas as pd
import csv
from shop.models import Product, Category, ProductsPricing
from django.core.management.base import BaseCommand



tmp_data_products_pricing=pd.read_csv('static/data/products_pricing.csv',sep=',', encoding='iso-8859-1').fillna(" ")



class Command(BaseCommand):
    def handle(self, **options):
        products_pricing = [
            ProductsPricing(
                category=Category.objects.get(name=row['category']),
                product=Product.objects.get(name=row['product']),
                size=row['size'],
                quantity=row['quantity'],
                price=row['price']
        )
            for _, row in tmp_data_products_pricing.iterrows()
        ]

        ProductsPricing.objects.bulk_create(products_pricing)
