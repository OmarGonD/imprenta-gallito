import pandas as pd
import csv
from shop.models import Peru
from django.core.management.base import BaseCommand



tmp_data=pd.read_csv('static/data/ubigeo-peru.csv',sep=',', encoding="utf-8")


class Command(BaseCommand):
    def handle(self, **options):
        products = [
            Peru(
                departamento=row['departamento'],
                provincia=row['provincia'],
                distrito=row['distrito'],
                costo_despacho_con_recojo=row['costo_despacho_con_recojo'],
                costo_despacho_sin_recojo=row['costo_despacho_sin_recojo'],
                dias_despacho = row['dias_despacho']

        )
            for idx, row in tmp_data.iterrows()
        ]

        Peru.objects.bulk_create(products)








