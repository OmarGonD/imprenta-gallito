import pandas as pd
import csv
from django.contrib.auth.models import Group
from shop.models import Product, Category, ProductsPricing, Pack
from django.core.management.base import BaseCommand

tmp_data_groups = pd.read_csv('static/data/groups.csv', sep=',', encoding='iso-8859-1').fillna(" ")

tmp_data_categories=pd.read_csv('static/data/categories.csv',sep=',', encoding='iso-8859-1').fillna(" ")

tmp_data_products = pd.read_csv('static/data/products.csv', sep=';', encoding='iso-8859-1').fillna(" ")

tmp_data_products_pricing=pd.read_csv('static/data/products_pricing.csv',sep=',', encoding='iso-8859-1').fillna(" ")

tmp_data_packs=pd.read_csv('static/data/packs.csv',sep=',', encoding='iso-8859-1').fillna(" ")


class Command(BaseCommand):
    def handle(self, **options):
        groups = [
            Group(
                name=row['group']
            )
            for _, row in tmp_data_groups.iterrows()
        ]

        Group.objects.bulk_create(groups)

        categories = [
            Category(
                name=row['category'],
                slug=row['slug'],
                description=row['description']
            )
            for _, row in tmp_data_categories.iterrows()
        ]

        Category.objects.bulk_create(categories)

        products = [
            Product(
                category=Category.objects.get(name=row['category']),
                name=row['product'],
                slug=row['slug'],
                sku=row['sku'],
                description=row['description'],
                available=row['available'],
                image=row['image']
        )
            for _, row in tmp_data_products.iterrows()
        ]

        Product.objects.bulk_create(products)

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

