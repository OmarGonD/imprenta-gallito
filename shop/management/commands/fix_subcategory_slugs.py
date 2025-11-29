from django.core.management.base import BaseCommand
from shop.models import Subcategory
from django.db import connection


class Command(BaseCommand):
    help = 'Fix subcategory slugs for tarjetas-presentacion'

    def handle(self, *args, **options):
        self.stdout.write('Fixing subcategory slugs...')
        
        # Fix ecologicas -> premium
        try:
            # Check if ecologicas exists
            with connection.cursor() as cursor:
                cursor.execute("SELECT slug, name FROM subcategories WHERE slug = 'ecologicas'")
                row = cursor.fetchone()
                if row:
                    self.stdout.write(f'  Found subcategory: {row[0]} - {row[1]}')
                    cursor.execute("UPDATE subcategories SET slug = 'premium' WHERE slug = 'ecologicas'")
                    self.stdout.write(self.style.SUCCESS('  Updated ecologicas -> premium'))
                else:
                    self.stdout.write('  Subcategory "ecologicas" not found')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error: {e}'))
        
        # Fix estandar -> standard
        try:
            with connection.cursor() as cursor:
                # Check if standard already exists
                cursor.execute("SELECT slug FROM subcategories WHERE slug = 'standard'")
                if cursor.fetchone():
                    self.stdout.write('  Subcategory "standard" already exists')
                    # Delete estandar if standard already exists
                    cursor.execute("SELECT slug, name FROM subcategories WHERE slug = 'estandar'")
                    row = cursor.fetchone()
                    if row:
                        self.stdout.write(f'  Deleting duplicate: {row[0]} - {row[1]}')
                        cursor.execute("DELETE FROM subcategories WHERE slug = 'estandar'")
                        self.stdout.write(self.style.SUCCESS('  Deleted estandar'))
                else:
                    cursor.execute("SELECT slug, name FROM subcategories WHERE slug = 'estandar'")
                    row = cursor.fetchone()
                    if row:
                        self.stdout.write(f'  Found subcategory: {row[0]} - {row[1]}')
                        cursor.execute("UPDATE subcategories SET slug = 'standard' WHERE slug = 'estandar'")
                        self.stdout.write(self.style.SUCCESS('  Updated estandar -> standard'))
                    else:
                        self.stdout.write('  Subcategory "estandar" not found')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Done!'))
