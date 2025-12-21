
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import DesignTemplate

# 1. Delete mistakenly imported 'calendario-de-escritorio' templates
bad_templates = DesignTemplate.objects.filter(slug__contains='calendario-de-escritorio')
count = bad_templates.count()
print(f"Found {count} bad templates (calendario-de-escritorio). Deleting...")
bad_templates.delete()
print("Deleted.")

# 2. Check for generic 'calendarios' imported without product slug?
# If their slug is just 'calendarios-filename' or similar.
# Let's count total templates in 'calendarios' subcategory again.
from shop.models import Subcategory
try:
    sub = Subcategory.objects.get(slug='calendarios')
    total = DesignTemplate.objects.filter(subcategory=sub).count()
    print(f"Total remaining templates in 'calendarios' subcategory: {total}")
    
    # Check specifically for calendario-escritorio
    escritorio = DesignTemplate.objects.filter(subcategory=sub, slug__contains='calendario-escritorio')
    print(f"Templates matching 'calendario-escritorio': {escritorio.count()}")

except Subcategory.DoesNotExist:
    print("Subcategory not found")
