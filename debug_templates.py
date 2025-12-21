
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Product, DesignTemplate, Subcategory

def check_stuff():
    product_slug = 'libro-de-firmas'
    print(f"Checking product: {product_slug}")
    
    try:
        product = Product.objects.get(slug=product_slug)
        print(f"Product found: {product.name}")
        print(f"Category: {product.category.slug}")
        if product.subcategory:
            print(f"Subcategory: {product.subcategory.slug}")
        else:
            print("Subcategory: None")
            
        print("-" * 30)
        
        # Check templates using the view logic
        templates = DesignTemplate.objects.all()
        print(f"Total templates in DB: {templates.count()}")
        
        # Filter by category
        templates = templates.filter(category=product.category)
        print(f"Templates in category '{product.category.slug}': {templates.count()}")
        
        if product.subcategory:
             # Logic from view:
             # templates = templates.filter(Q(subcategory=product.subcategory) | Q(subcategory__isnull=True))
             templates_sub = templates.filter(subcategory=product.subcategory)
             print(f"Templates strictly in subcategory '{product.subcategory.slug}': {templates_sub.count()}")
             
             if product.subcategory.slug == 'bodas':
                 
                 print(f"Checking for correct slug 'bodas-{product.slug}'...")
                 correct = templates.filter(slug__contains=f"bodas-{product.slug}")
                 print(f"Templates correctly named: {correct.count()}")
                 for t in correct[:5]:
                     print(f" - {t.slug}")

                 # Check for old/incorrect slug 
                 old_slug = "libro-firmas-invitados"
                 print(f"Checking for old/incorrect slug '{old_slug}'...")
                 incorrect = templates.filter(slug__contains=old_slug)
                 print(f"Templates with old slug: {incorrect.count()}")
                 for t in incorrect[:5]:
                     print(f" - {t.slug}")
                     
                 # Check for any other variant?
                 # print("Sample of other templates in subcategory:")
                 # for t in templates_sub[:5]:
                 #     print(f" - {t.slug}")

    except Product.DoesNotExist:
        print("Product not found!")

if __name__ == '__main__':
    check_stuff()
