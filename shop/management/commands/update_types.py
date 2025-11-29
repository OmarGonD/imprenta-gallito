from django.core.management.base import BaseCommand
from shop.models import TarjetaPresentacion

class Command(BaseCommand):
    help = 'Update types for TarjetaPresentacion'

    def handle(self, *args, **options):
        TarjetaPresentacion.objects.filter(name__icontains='deluxe').update(type='deluxe')
        TarjetaPresentacion.objects.filter(name__icontains='premium').update(type='premium')
        TarjetaPresentacion.objects.filter(name__icontains='ecologica').update(type='premium')
        TarjetaPresentacion.objects.filter(name__icontains='standard').update(type='standard')
        self.stdout.write(self.style.SUCCESS('Successfully updated types'))
