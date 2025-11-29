from django.core.management.base import BaseCommand
from shop.models import Subcategory


class Command(BaseCommand):
    help = 'Check subcategories for tarjetas-presentacion'

    def handle(self, *args, **options):
        self.stdout.write('Checking subcategories for tarjetas-presentacion...\n')
        
        subs = Subcategory.objects.filter(category__slug='tarjetas-presentacion')
        
        for sub in subs:
            self.stdout.write(f'  {sub.slug} - {sub.name}')
        
        self.stdout.write(f'\nTotal: {subs.count()} subcategories')
