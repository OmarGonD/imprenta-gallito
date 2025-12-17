from django.core.management.base import BaseCommand
from shop.models import ProductOption, ProductOptionValue

class Command(BaseCommand):
    help = 'Populates standard clothing colors'

    def handle(self, *args, **options):
        self.stdout.write('Populating colors...')
        
        color_opt, created = ProductOption.objects.get_or_create(
            key='color',
            defaults={
                'name': 'Color',
                'is_required': True,
                'selection_type': 'single'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Color option'))

        colors = [
            # ID, Name, Hex
            ('negro', 'Negro', '#000000'),
            ('blanco', 'Blanco', '#FFFFFF'),
            ('azul-marino', 'Azul Marino', '#1e3a8a'), # Navy 800
            ('gris-jaspe', 'Gris Jaspe', '#9ca3af'), # Gray 400
            ('rojo', 'Rojo', '#dc2626'), # Red 600
            ('azul-royal', 'Azul Royal', '#2563eb'), # Blue 600
            ('verde-militar', 'Verde Militar', '#4d7c0f'), # Green
        ]
        
        count = 0
        for value, name, hex_code in colors:
            obj, created = ProductOptionValue.objects.get_or_create(
                option=color_opt,
                value=value,
                defaults={
                    'display_name': name,
                    'hex_code': hex_code,
                    'is_active': True,
                    'display_order': count
                }
            )
            if created:
                count += 1
                self.stdout.write(f'  Created {name}')
            else:
                # Update hex if missing
                if not obj.hex_code:
                    obj.hex_code = hex_code
                    obj.save()
                    self.stdout.write(f'  Updated hex for {name}')

        self.stdout.write(self.style.SUCCESS(f'Done! Added {count} new colors.'))
