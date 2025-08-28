import pandas as pd
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

tmp_data_groups = pd.read_csv('static/data/groups.csv', sep=',', encoding='iso-8859-1').fillna(" ")


class Command(BaseCommand):
    def handle(self, **options):
        groups = [
            Group(
                name=row['group']
            )
        for _, row in tmp_data_groups.iterrows()
        ]

        Group.objects.bulk_create(groups)
