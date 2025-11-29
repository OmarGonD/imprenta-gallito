from django.core.management.base import BaseCommand
from shop.models import Product, PriceTier
from decimal import Decimal


class Command(BaseCommand):
    help = 'Import price tiers for tarjetas-presentacion products'

    def handle(self, *args, **options):
        self.stdout.write('Importing price tiers for tarjetas products...\n')
        
        # Get all tarjetas products
        products = Product.objects.filter(category__slug='tarjetas-presentacion', status='active')
        
        # Standard price tiers for business cards
        price_tiers_data = [
            {'min': 50, 'max': 99, 'price': '51.00', 'discount': 0},
            {'min': 100, 'max': 199, 'price': '56.00', 'discount': 45},
            {'min': 200, 'max': 299, 'price': '65.00', 'discount': 68},
            {'min': 300, 'max': 499, 'price': '73.00', 'discount': 76},
            {'min': 500, 'max': 999, 'price': '87.00', 'discount': 83},
            {'min': 1000, 'max': 1999, 'price': '117.00', 'discount': 89},
            {'min': 2000, 'max': 2999, 'price': '168.00', 'discount': 92},
            {'min': 3000, 'max': 4999, 'price': '213.00', 'discount': 93},
            {'min': 5000, 'max': 9999, 'price': '293.00', 'discount': 94},
            {'min': 10000, 'max': 999999, 'price': '464.00', 'discount': 95},
        ]
        
        total_created = 0
        
        for product in products:
            # Check if product already has price tiers
            existing = PriceTier.objects.filter(product=product).count()
            if existing > 0:
                self.stdout.write(f'  {product.slug}: Already has {existing} tiers, skipping')
                continue
            
            # Create price tiers for this product
            for tier_data in price_tiers_data:
                PriceTier.objects.create(
                    product=product,
                    min_quantity=tier_data['min'],
                    max_quantity=tier_data['max'],
                    unit_price=Decimal(tier_data['price']),
                    discount_percentage=tier_data['discount']
                )
                total_created += 1
            
            self.stdout.write(f'  {product.slug}: Created {len(price_tiers_data)} price tiers')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Total price tiers created: {total_created}'))
