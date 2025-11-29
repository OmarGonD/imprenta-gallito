from django.core.management.base import BaseCommand
from shop.models import Product, PriceTier


class Command(BaseCommand):
    help = 'Check price tiers for tarjetas-presentacion products'

    def handle(self, *args, **options):
        self.stdout.write('Checking price tiers...\n')
        
        # Get all tarjetas products
        products = Product.objects.filter(category__slug='tarjetas-presentacion')
        
        self.stdout.write(f'Found {products.count()} tarjetas products\n')
        
        for product in products:
            tiers = PriceTier.objects.filter(product=product).count()
            self.stdout.write(f'  {product.slug}: {tiers} price tiers')
        
        self.stdout.write('\n\nTotal price tiers in database: ' + str(PriceTier.objects.count()))
