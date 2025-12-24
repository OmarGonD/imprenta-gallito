import os
import sys
import django

# Setup Django
sys.path.append(r'D:\web_proyects\imprenta_gallito')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import DesignTemplate

print("="*80)
print("VERIFICATION: BANDERINES TEMPLATES")
print("="*80)

# Check templates for banderines
print("\n1. Checking templates with 'banderines' in path:")
banderines_templates = DesignTemplate.objects.filter(thumbnail_url__icontains='banderines')
print(f"   Found {banderines_templates.count()} templates")

if banderines_templates.count() > 0:
    print("\n   First 5 templates:")
    for t in banderines_templates[:5]:
        print(f"   - {t.slug}")
        print(f"     Name: {t.name}")
        print(f"     URL: {t.thumbnail_url}")
    
    print(f"\n   Last 3 templates:")
    for t in banderines_templates.order_by('-id')[:3]:
        print(f"   - {t.slug}")
        print(f"     URL: {t.thumbnail_url}")
else:
    print("   ❌ NO TEMPLATES FOUND!")

# Check banderas_pluma too
print("\n2. Checking templates with 'banderas_pluma' or 'banderas-pluma' in path:")
banderas_pluma = DesignTemplate.objects.filter(thumbnail_url__icontains='banderas_pluma') | \
                  DesignTemplate.objects.filter(thumbnail_url__icontains='banderas-pluma')
print(f"   Found {banderas_pluma.count()} templates")

# Check total letreros templates
print("\n3. Total letreros_banners templates:")
letreros_total = DesignTemplate.objects.filter(thumbnail_url__icontains='letreros_banners')
print(f"   Found {letreros_total.count()} templates")

print("\n" + "="*80)
