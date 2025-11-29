from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix estandar subcategory slug to standard'

    def handle(self, *args, **options):
        self.stdout.write('Fixing estandar -> standard...\n')
        
        try:
            with connection.cursor() as cursor:
                # First, update any products referencing estandar to reference standard
                cursor.execute("""
                    UPDATE products 
                    SET subcategory_slug = 'standard' 
                    WHERE subcategory_slug = 'estandar'
                """)
                products_updated = cursor.rowcount
                self.stdout.write(f'  Updated {products_updated} products to reference standard')
                
                # Now update the subcategory slug
                cursor.execute("""
                    UPDATE subcategories 
                    SET slug = 'standard' 
                    WHERE slug = 'estandar'
                """)
                self.stdout.write(self.style.SUCCESS('  Updated subcategory slug: estandar -> standard'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Done!'))
