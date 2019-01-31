import pandas as pd
import csv
from shop.models import Peru
from django.core.management.base import BaseCommand



tmp_data=pd.read_csv('static/data/ubigeo-peru-2018-12-25.csv',sep=',', encoding="utf-8")


class Command(BaseCommand):
    def handle(self, **options):
        products = [
            Peru(
                departamento=row['departamento'],
                provincia=row['provincia'],
                distrito=row['distrito'],
            )
            for idx, row in tmp_data.iterrows()
        ]

        Peru.objects.bulk_create(products)








