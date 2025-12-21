
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Category, Subcategory

cats = Category.objects.all()
for c in cats:
    print(f"Category: {c.name} ({c.slug})")
    subs = Subcategory.objects.filter(category=c)
    for s in subs:
        print(f"  - Sub: {s.name} ({s.slug})")
