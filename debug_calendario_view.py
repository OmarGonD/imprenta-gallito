
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Product, DesignTemplate, Subcategory

slug = 'calendario-escritorio'
try:
    product = Product.objects.get(slug=slug)
    print(f"Product: {product.name}")
    print(f"Product Slug: {product.slug}")
    print(f"Subcategory: {product.subcategory.name} (slug: {product.subcategory.slug})")
    
    # Simulate View Logic
    templates = DesignTemplate.objects.filter(category=product.category)
    
    if product.subcategory:
        from django.db.models import Q
        templates = templates.filter(
            Q(subcategory=product.subcategory) | Q(subcategory__isnull=True)
        )
        print(f"Templates after subcategory filter: {templates.count()}")
        
        if product.subcategory.slug == 'calendarios':
            print("Applying slug filter for 'calendarios'...")
            templates = templates.filter(slug__contains=product.slug)
            print(f"Templates after slug filter: {templates.count()}")
            
            # Print first 5 slugs
            print("Sample slugs:")
            for t in templates[:5]:
                print(f" - {t.slug}")
                
            # Check for incorrect ones
            invalid = templates.exclude(slug__contains=product.slug)
            if invalid.exists():
                print(f"WARNING: Found {invalid.count()} templates that DO NOT match slug (logic error?)")
            else:
                 print("All filtered templates match the slug check.")

            # Check if we have templates that SHOULD be there but aren't?
            # Or if we have templates that shouldn't be there?
            # Check if any 'calendario-magnetico' is in the list
            magnetico = templates.filter(slug__contains='magnetico')
            if magnetico.exists():
                print(f"ERROR: Found {magnetico.count()} magnetico templates!")
            else:
                print("No magnetico templates found (Good).")

except Product.DoesNotExist:
    print(f"Product {slug} not found")
