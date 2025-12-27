import os
import django
import sys
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Product, Category, ProductOption, ProductOptionValue, ProductVariant, PriceTier

def apply_smart_pricing():
    print("🚀 Starting Smart Pricing for Ropa y Bolsos...")
    
    try:
        category = Category.objects.get(slug='ropa-bolsos')
    except Category.DoesNotExist:
        print("❌ Category 'ropa-bolsos' not found.")
        return

    products = Product.objects.filter(category=category)
    print(f"📦 Found {products.count()} products.")

    # 1. SETUP OPTIONS
    # Print Size
    size_print_opt, _ = ProductOption.objects.get_or_create(
        key='print_size',
        defaults={'name': 'Tamaño de Impresión', 'selection_type': 'single', 'display_order': 2}
    )
    
    # Values for Print Size
    ps_small, _ = ProductOptionValue.objects.get_or_create(
        option=size_print_opt, value='14x21', defaults={'display_name': '14cm x 21cm'}
    )
    ps_small.additional_price = Decimal('0.00')
    ps_small.save()
    
    ps_medium, _ = ProductOptionValue.objects.get_or_create(
        option=size_print_opt, value='21x30', defaults={'display_name': '21cm x 30cm'}
    )
    ps_medium.additional_price = Decimal('9.00') # Rounded
    ps_medium.save()
    
    ps_large, _ = ProductOptionValue.objects.get_or_create(
        option=size_print_opt, value='32x38', defaults={'display_name': '32cm x 38cm'}
    )
    ps_large.additional_price = Decimal('17.00') # Rounded
    ps_large.save()
    
    print("✅ 'Print Size' option configured.")

    # 2. ITERATE PRODUCTS
    for product in products:
        print(f"\nProcessing: {product.name}")
        
        # A. UPDATE COLOR OPTION SURCHARGES
        try:
            color_variant = product.variant_options.get(option__key='color')
            colors = color_variant.get_available_values()
            
            for color in colors:
                val_lower = color.value.lower()
                if 'blanco' in val_lower or 'white' in val_lower:
                    color.additional_price = Decimal('0.00')
                else:
                    color.additional_price = Decimal('9.00') # Rounded
                color.save()
            print("   Updated color surcharges.")
            
        except ProductVariant.DoesNotExist:
            print("   ⚠️ No color variant found (skipping color update).")

        # B. ADD PRINT SIZE VARIANT
        if not product.variant_options.filter(option=size_print_opt).exists():
            ps_variant = ProductVariant.objects.create(
                product=product,
                option=size_print_opt,
                display_order=2
            )
            ps_variant.available_values.set([ps_small, ps_medium, ps_large])
            print("   Added 'Print Size' variant.")
        else:
            print("   'Print Size' variant already exists.")

        # C. UPDATE PRICE TIERS (Base Cost = 40.00)
        # Rounded Up Ceiling Prices
        # 1+: 67.00
        # 12+: 62.00
        # 50+: 56.00
        # 100+: 50.00
        # 500+: 48.00
        
        product.price_tiers.all().delete()
        
        # Calculate discount percentages relative to base (67.00)
        base = 67.00
        d12 = int((1 - 62.00/base) * 100)
        d50 = int((1 - 56.00/base) * 100)
        d100 = int((1 - 50.00/base) * 100)
        d500 = int((1 - 48.00/base) * 100)
        
        PriceTier.objects.create(product=product, min_quantity=1, max_quantity=11, unit_price=Decimal('67.00'), discount_percentage=0)
        PriceTier.objects.create(product=product, min_quantity=12, max_quantity=49, unit_price=Decimal('62.00'), discount_percentage=d12)
        PriceTier.objects.create(product=product, min_quantity=50, max_quantity=99, unit_price=Decimal('56.00'), discount_percentage=d50)
        PriceTier.objects.create(product=product, min_quantity=100, max_quantity=499, unit_price=Decimal('50.00'), discount_percentage=d100)
        PriceTier.objects.create(product=product, min_quantity=500, max_quantity=999999, unit_price=Decimal('48.00'), discount_percentage=d500)
        
        # Update Product Base Price
        product.base_price = Decimal('67.00')
        product.min_quantity = 1
        product.save()
        
        print("   Updated Pricing Tiers.")

    print("\n🏁 Apply Completed.")

if __name__ == '__main__':
    apply_smart_pricing()
