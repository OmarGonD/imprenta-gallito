"""
Management command to import calendarios templates from static files into DesignTemplate model.
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from shop.models import DesignTemplate, Category, Subcategory


class Command(BaseCommand):
    help = 'Import calendarios templates from static folder into DesignTemplate model'

    def handle(self, *args, **options):
        self.stdout.write('Importing calendarios templates...\n')
        
        # Base path for templates
        # D:\web_proyects\imprenta_gallito\static\media\template_images\calendarios_regalos
        base_path = os.path.join(settings.BASE_DIR, 'static', 'media', 'template_images', 'calendarios_regalos')
        
        if not os.path.exists(base_path):
            self.stdout.write(self.style.ERROR(f'Path not found: {base_path}'))
            return
        
        # Get category and subcategory
        # URL: /calendarios-regalos/calendarios/calendario-magnetico/
        try:
            category = Category.objects.get(slug='calendarios-regalos')
            subcategory = Subcategory.objects.get(slug='calendarios', category=category)
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR('Category calendarios-regalos not found'))
            return
        except Subcategory.DoesNotExist:
            self.stdout.write(self.style.ERROR('Subcategory calendarios not found'))
            return
        
        self.stdout.write(f'Category: {category.name}')
        self.stdout.write(f'Subcategory: {subcategory.name}\n')
        
        # Mapping folder names to product slugs
        folder_to_product = {
            'calendarios_magneticos': 'calendario-magnetico',
            'calendarios_escritorio': 'calendario-escritorio', 
            'calendarios_marcapaginas': 'calendario-marcapaginas',
            'calendarios_mousepad': 'calendario-mousepad',
            'calendarios_poster': 'tipos-calendario-poster',
        }
        
        total_created = 0
        total_updated = 0
        
        # Iterate through each folder in base_path
        for folder_name in os.listdir(base_path):
            folder_path = os.path.join(base_path, folder_name)
            
            if not os.path.isdir(folder_path):
                continue
            
            # Skip if not in our mapping (unless we want to try auto-mapping)
            if folder_name not in folder_to_product and folder_name != 'calendarios':
                 self.stdout.write(f'Skipping folder (no mapping): {folder_name}')
                 continue

            if folder_name == 'calendarios':
                # Special handling for generic calendars if needed?
                # For now let's focus on the specific products as requested.
                # If these are generic, maybe they shouldn't trigger "product specific" logic.
                # But they are huge in number (598 files).
                # Maybe they belong to "calendarios-de-pared" or just "calendarios"?
                # I'll skip loading the generic 'calendarios' folder for now unless I find a product slug for it.
                # The user specifically asked about 'calendarios_magneticos'.
                 self.stdout.write(f'Skipping generic folder for now: {folder_name}')
                 continue
            
            product_slug = folder_to_product[folder_name]
            self.stdout.write(f'\nProcessing: {folder_name} -> product: {product_slug}')
            
            # Get all image files
            image_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.svg')
            images = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
            
            self.stdout.write(f'  Found {len(images)} template images')
            
            for i, image_file in enumerate(images):
                # Create slug from filename (without extension)
                file_slug = os.path.splitext(image_file)[0].lower()
                
                # Slug format: calendarios-{product_slug}-{file_slug}
                # Similar to bodas-{product_slug}-{file_slug}
                template_slug = f'calendarios-{product_slug}-{file_slug}'[:100]
                
                # Image URL (relative to static)
                image_url = f'/static/media/template_images/calendarios_regalos/{folder_name}/{image_file}'
                
                # Create template name from filename
                template_name = file_slug.replace('-', ' ').replace('_', ' ').replace('calendario magneticos', 'Diseño').title()[:200]
                
                # Create or update template
                template, created = DesignTemplate.objects.update_or_create(
                    slug=template_slug,
                    defaults={
                        'name': template_name,
                        'category': category,
                        'subcategory': subcategory,
                        'thumbnail_url': image_url,
                        'preview_url': image_url,
                        'is_popular': i < 10,
                        'is_new': i < 5,
                        'display_order': i,
                    }
                )
                
                if created:
                    total_created += 1
                else:
                    total_updated += 1
            
            self.stdout.write(f'  Imported {len(images)} templates for {product_slug}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Done! Created: {total_created}, Updated: {total_updated}'))
