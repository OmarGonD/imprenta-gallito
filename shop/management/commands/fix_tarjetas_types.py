from django.core.management.base import BaseCommand
from shop.models import TarjetaPresentacion


class Command(BaseCommand):
    help = 'Fix TarjetaPresentacion type values'

    def handle(self, *args, **options):
        self.stdout.write('Fixing TarjetaPresentacion types...')
        
        # Get all tarjetas
        tarjetas = TarjetaPresentacion.objects.all()
        
        self.stdout.write(f'Found {tarjetas.count()} tarjetas')
        
        for tarjeta in tarjetas:
            old_type = tarjeta.type
            # Map old type values to new ones
            if old_type == 'ecologicas':
                tarjeta.type = 'premium'
                tarjeta.save()
                self.stdout.write(f'  Updated {tarjeta.name}: ecologicas -> premium')
            elif old_type == 'estandar':
                tarjeta.type = 'standard'
                tarjeta.save()
                self.stdout.write(f'  Updated {tarjeta.name}: estandar -> standard')
            else:
                self.stdout.write(f'  {tarjeta.name}: {old_type} (no change)')
        
        self.stdout.write(self.style.SUCCESS('Done!'))
