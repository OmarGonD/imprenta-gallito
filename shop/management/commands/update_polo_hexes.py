from django.core.management.base import BaseCommand
from shop.models import ProductOptionValue

class Command(BaseCommand):
    help = 'Update hex codes for existing color options'

    def handle(self, *args, **kwargs):
        # Color mapping (Spanish slug -> Hex)
        COLOR_MAP = {
            'amarillo': '#FFEB3B',
            'arena': '#F4D03F',
            'asfalto': '#4D5656',
            'azalea': '#F48FB1',
            'azul': '#2196F3',
            'azul-carolina': '#90CAF9',
            'azul-cielo-nocturno': '#1A237E',
            'azul-claro': '#BBDEFB',
            'azul-marino': '#0D47A1',
            'azul-marino-jaspeado': '#546E7A',
            'azul-medianoche': '#1A237E',
            'azul-metro': '#3F51B5',
            'azul-real': '#2962FF',
            'blanco': '#FFFFFF',
            'borgo-a': '#880E4F', # borgoña bug?
            'borgona': '#880E4F', 
            'cafe': '#6D4C41',
            'carb-n': '#424242', # carbon bug?
            'carbon': '#424242',
            'cardinal-red': '#C62828',
            'celed-n': '#81C784',
            'celeste': '#81D4FA',
            'cereza-roja': '#D32F2F',
            'chocolate': '#5D4037',
            'coral': '#FF8A65',
            'coral-seda': '#FFAB91',
            'crema': '#FFF9C4',
            'fucsia': '#E91E63',
            'grafito': '#616161',
            'grafito-jaspeado': '#757575',
            'gris': '#9E9E9E',
            'gris-ceniza': '#BDBDBD',
            'gris-deportivo': '#9E9E9E', # heather grey
            'gris-jaspeado': '#B0BEC5',
            'heliconia': '#EC407A',
            'indigo': '#3949AB',
            'jade-dome': '#00897B',
            'kiwi': '#AED581',
            'lavanda': '#CE93D8',
            'lima': '#CDDC39',
            'lima-electrico': '#C6FF00',
            'maiz-seda': '#FFF176',
            'mandarina': '#FF9800',
            'margarita': '#FDD835',
            'marron': '#795548',
            'menta': '#A5D6A7',
            'mora': '#7B1FA2',
            'morado': '#9C27B0',
            'naranja': '#FF5722',
            'naranja-atardecer': '#FF7043',
            'naranja-seguridad': '#FF6E40',
            'natural': '#F5F5DC',
            'negro': '#000000',
            'negro-jaspeado': '#424242',
            'oro-viejo': '#BCAAA4',
            'pistacho': '#C5E1A5',
            'platino': '#E0E0E0',
            'purpura': '#8E24AA',
            'rojo': '#F44336',
            'rojo-cereza': '#D32F2F',
            'rojo-granate': '#B71C1C',
            'rojo-ladrillo': '#A1887F',
            'rosa': '#F48FB1',
            'rosa-claro': '#F8BBD0',
            'rosa-n-n': '#F06292', # rosa neon?
            'rosa-neon': '#FF4081',
            'rosa-seguridad': '#FF80AB',
            'russet': '#795548',
            'safari': '#A1887F',
            'salmon': '#FF8A65',
            'sapphire': '#1E88E5',
            'texas-orange': '#FFCC80',
            'tweed': '#424242',
            'verde': '#4CAF50',
            'verde-bosque': '#2E7D32',
            'verde-botella': '#2E7D32',
            'verde-cali': '#66BB6A',
            'verde-cesped': '#66BB6A',
            'verde-irlandes': '#43A047',
            'verde-lima': '#CDDC39',
            'verde-militar': '#558B2F',
            'verde-oscuro': '#1B5E20',
            'verde-seguridad': '#CCFF90',
            'vintage-turquoise': '#80DEEA',
            'cardenal': '#C62828',
            'ceniza': '#E0E0E0',
            'deep-forest': '#1B5E20',
            'dorado': '#FFD700',
            'fuchsia-frost': '#E91E63',
            'granate': '#880E4F',
            'graphite': '#616161',
            'heather-peach': '#FFCC80',
            'heather-sangria': '#880E4F',
            'kelly': '#4CAF50',
            'light-steel': '#B0BEC5',
            'lila': '#CE93D8',
            'sangria': '#880E4F',
            'shiraz': '#4A148C',
            'sky': '#81D4FA',
            'smoked-paprika': '#FF5722',
            'turquoise': '#00BCD4',
            'turquoise-frost': '#00BCD4',
            'violeta': '#9C27B0',
            'zafiro': '#01579B'
        }
        
        updated = 0
        qs = ProductOptionValue.objects.filter(option__key='color')
        
        for val in qs:
            slug = val.value.lower().strip()
            
            # Direct match
            new_hex = COLOR_MAP.get(slug)
            
            # Fuzzy match attempt if not found
            if not new_hex:
                for k, v in COLOR_MAP.items():
                    if k in slug:
                        new_hex = v
                        break
            
            if new_hex:
                val.hex_code = new_hex
                val.save()
                updated += 1
                self.stdout.write(f"Updated {slug} -> {new_hex}")
            else:
                self.stdout.write(self.style.WARNING(f"No match for {slug}"))

        self.stdout.write(self.style.SUCCESS(f"Finished. Updated {updated}/{qs.count()} colors."))
