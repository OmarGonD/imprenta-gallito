import pandas as pd
import csv
from shop.models import UnitaryProduct, Category
from django.core.management.base import BaseCommand



tmp_data_unitaryproducts=pd.read_csv('static/data/unitary_products.csv',sep=',', encoding='iso-8859-1').fillna(" ")


class Command(BaseCommand):
    def handle(self, **options):
        unitary_products = [
            UnitaryProduct(
                category=Category.objects.get(name=row['category']),
                subcategory1=row['subcategory1'],
                subcategory2=row['subcategory2'],
                name=row['name'],
                slug=row['slug'],
                sku=row['sku'],
                size=row['size'],
                quantity=row['quantity'],
                price=row['price'],
                image=row['image'],
                description=row['description'],
                available=row['available']
        )
            for _, row in tmp_data_unitaryproducts.iterrows()
        ]

        UnitaryProduct.objects.bulk_create(unitary_products)