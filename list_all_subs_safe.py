
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Category, Subcategory

with open('all_subs_utf8.txt', 'w', encoding='utf-8') as f:
    cats = Category.objects.all()
    for c in cats:
        f.write(f"Category: {c.name} ({c.slug})\n")
        subs = Subcategory.objects.filter(category=c)
        if subs.exists():
            for s in subs:
                f.write(f"  - Sub: {s.name} ({s.slug})\n")
        else:
            f.write("  (No subcategories)\n")
