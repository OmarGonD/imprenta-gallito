
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from shop.models import DesignTemplate

def fix_slugs():
    # 1. Fix invitaciones-despedida-de-soltera
    # Mismatch: 'invitaciones-despedida-soltera' -> 'invitaciones-despedida-de-soltera'
    print("Fixing 'invitaciones-despedida-de-soltera'...")
    wrong_slug_part = 'invitaciones-despedida-soltera'
    correct_slug_part = 'invitaciones-despedida-de-soltera'
    
    templates = DesignTemplate.objects.filter(slug__contains=wrong_slug_part).exclude(slug__contains=correct_slug_part)
    print(f"Found {templates.count()} templates with wrong slug '{wrong_slug_part}'")
    
    for t in templates:
        new_slug = t.slug.replace(wrong_slug_part, correct_slug_part)
        print(f"Renaming: {t.slug} -> {new_slug}")
        t.slug = new_slug
        try:
            t.save()
        except Exception as e:
            print(f"Error saving {t.slug}: {e}")

    print("-" * 30)

    # 2. Fix libro-de-firmas
    # Mismatch: 'libro-firmas-invitados' -> 'libro-de-firmas'
    print("Fixing 'libro-de-firmas'...")
    wrong_slug_part_2 = 'libro-firmas-invitados'
    correct_slug_part_2 = 'libro-de-firmas'
    
    templates_2 = DesignTemplate.objects.filter(slug__contains=wrong_slug_part_2).exclude(slug__contains=correct_slug_part_2)
    print(f"Found {templates_2.count()} templates with wrong slug '{wrong_slug_part_2}'")
    
    for t in templates_2:
        # Note: 'libro-firmas-invitados' is completely different from 'libro-de-firmas', 
        # so replace the whole part.
        new_slug = t.slug.replace(wrong_slug_part_2, correct_slug_part_2)
        print(f"Renaming: {t.slug} -> {new_slug}")
        t.slug = new_slug
        try:
            t.save()
        except Exception as e:
            print(f"Error saving {t.slug}: {e}")

if __name__ == '__main__':
    fix_slugs()
