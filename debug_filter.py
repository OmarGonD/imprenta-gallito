
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Product, DesignTemplate, Subcategory

# Check product slug
try:
    p = Product.objects.get(slug='calendario-marcapaginas')
    print(f"Product: {p.name}")
    print(f"Product Slug: '{p.slug}'")
    print(f"Subcategory: {p.subcategory.name} (slug: '{p.subcategory.slug}')")
except Product.DoesNotExist:
    print("Product 'calendario-marcapaginas' NOT FOUND")

# Check templates
print("\nTemplates with 'marcapaginas' in slug:")
templates = DesignTemplate.objects.filter(slug__contains='marcapaginas')
print(f"Found: {templates.count()}")
for t in templates[:5]:
    print(f" - {t.slug}")

print("\nChecking what view would return:")
try:
    p = Product.objects.get(slug='calendario-marcapaginas')
    templates = DesignTemplate.objects.filter(category=p.category)
    if p.subcategory:
        from django.db.models import Q
        templates = templates.filter(
            Q(subcategory=p.subcategory) | Q(subcategory__isnull=True)
        )
        print(f"After subcategory filter: {templates.count()}")
        
        if p.subcategory.slug == 'calendarios-familiares':
            print(f"Applying product slug filter: slug__contains='{p.slug}'")
            templates = templates.filter(slug__contains=p.slug)
            print(f"After product slug filter: {templates.count()}")
            for t in templates[:5]:
                print(f" - {t.slug}")
        else:
            print(f"Subcategory slug is NOT calendarios-familiares: '{p.subcategory.slug}'")
except Exception as e:
    print(f"Error: {e}")
