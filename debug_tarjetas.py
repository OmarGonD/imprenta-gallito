import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import Category, Product

cat = Category.objects.get(slug='tarjetas-presentacion')
print(f"Cat: {cat.name} Status: {cat.status}")
subs = cat.subcategories.all()
print(f"Total subs: {subs.count()}")
print(f"Active subs: {subs.filter(status='active').count()}")
for s in subs:
    print(f" - Subcat: {s.name}: {s.status} ({s.products.filter(status='active').count()} prods)")
orphan_prods = Product.objects.filter(category=cat, subcategory__isnull=True, status='active')
print(f"Total Orphan Products (no subcategory): {orphan_prods.count()}")
for p in orphan_prods:
    print(f"  - {p.name}")
