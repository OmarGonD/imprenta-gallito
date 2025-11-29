from django.core.management.base import BaseCommand
from shop.models import Product, Subcategory


class Command(BaseCommand):
    help = 'Fix products with null subcategory to use correct deluxe subcategory'

    def handle(self, *args, **options):
        self.stdout.write('Fixing products with missing deluxe subcategory...\n')
        
        try:
            # Get the deluxe subcategory
            try:
                deluxe_subcat = Subcategory.objects.get(slug='deluxe', category__slug='tarjetas-presentacion')
                self.stdout.write(f'  Found deluxe subcategory: {deluxe_subcat.name}')
            except Subcategory.DoesNotExist:
                self.stdout.write(self.style.ERROR('  Deluxe subcategory not found!'))
                return
            
            # Get all tarjetas-presentacion products without subcategory that should be deluxe
            deluxe_products_skus = [
                'TP-BAMBOO', 'TP-CLEARPLASTIC', 'TP-PEARL', 'TP-ULTRATHICK',
                'TP-FROSTEDPLASTIC', 'TP-EMBOSSEDGLOSS', 'TP-PAINTEDEDGE',
                'TP-RAISEDFOIL', 'TP-FOILACCENT'
            ]
            
            products = Product.objects.filter(
                category__slug='tarjetas-presentacion',
                sku__in=deluxe_products_skus,
                subcategory__isnull=True
            )
            
            count = products.count()
            self.stdout.write(f'  Found {count} products without subcategory')
            
            # Update each product
            for product in products:
                product.subcategory = deluxe_subcat
                product.save()
                self.stdout.write(f'    Updated {product.sku} - {product.name}')
            
            self.stdout.write(self.style.SUCCESS(f'\n  Total: Updated {count} products to deluxe subcategory'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Done!'))
