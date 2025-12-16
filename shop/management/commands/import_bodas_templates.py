"""
Management command to import bodas templates from static files into DesignTemplate model.
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from shop.models import DesignTemplate, Category, Subcategory


class Command(BaseCommand):
    help = 'Import bodas templates from static folder into DesignTemplate model'

    def handle(self, *args, **options):
        self.stdout.write('Importing bodas templates...\n')
        
        # Base path for templates
        base_path = os.path.join(settings.BASE_DIR, 'static', 'media', 'template_images', 'invitaciones_papeleria', 'bodas')
        
        if not os.path.exists(base_path):
            self.stdout.write(self.style.ERROR(f'Path not found: {base_path}'))
            return
        
        # Get category and subcategory
        try:
            category = Category.objects.get(slug='invitaciones-papeleria')
            subcategory = Subcategory.objects.get(slug='bodas', category=category)
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR('Category invitaciones-papeleria not found'))
            return
        except Subcategory.DoesNotExist:
            self.stdout.write(self.style.ERROR('Subcategory bodas not found'))
            return
        
        self.stdout.write(f'Category: {category.name}')
        self.stdout.write(f'Subcategory: {subcategory.name}\n')
        
        # Mapping folder names to product slugs
        folder_to_product = {
            'guarda_la_fecha': 'guarda-la-fecha',
            'servilletas': 'servilletas',
            'carteles_carton_espuma': 'carteles-carton-espuma',
            'invitaciones_despedida_soltera': 'invitaciones-despedida-soltera',
            'libro_firmas_invitados': 'libro-firmas-invitados',
            'programas_boda': 'programas-boda',
            'tarjetas_de_gracias': 'tarjetas-de-gracias',
            'tarjetas_informativas': 'tarjetas-informativas',
            'tarjetas_itinerario': 'tarjetas-itinerario',
            'tarjetas_itineario': 'tarjetas-itinerario',  # typo variant
            'tarjetas_menu': 'tarjetas-menu',
            'tarjetas_rsvp': 'tarjetas-rsvp',
        }
        
        total_created = 0
        total_updated = 0
        
        # Iterate through each product folder
        for folder_name in os.listdir(base_path):
            folder_path = os.path.join(base_path, folder_name)
            
            if not os.path.isdir(folder_path):
                continue
            
            product_slug = folder_to_product.get(folder_name, folder_name.replace('_', '-'))
            self.stdout.write(f'\nProcessing: {folder_name} -> product: {product_slug}')
            
            # Get all image files
            image_extensions = ('.jpg', '.jpeg', '.png', '.webp')
            images = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
            
            self.stdout.write(f'  Found {len(images)} template images')
            
            for i, image_file in enumerate(images):
                # Create slug from filename (without extension)
                file_slug = os.path.splitext(image_file)[0].lower()
                template_slug = f'bodas-{product_slug}-{file_slug}'[:100]  # Max 100 chars
                
                # Image URL (relative to static)
                image_url = f'/static/media/template_images/invitaciones_papeleria/bodas/{folder_name}/{image_file}'
                
                # Create template name from filename
                template_name = file_slug.replace('-', ' ').replace('_', ' ').title()[:200]
                
                # Create or update template
                template, created = DesignTemplate.objects.update_or_create(
                    slug=template_slug,
                    defaults={
                        'name': template_name,
                        'category': category,
                        'subcategory': subcategory,
                        'thumbnail_url': image_url,
                        'preview_url': image_url,
                        'is_popular': i < 10,  # First 10 are popular
                        'is_new': i < 5,  # First 5 are new
                        'display_order': i,
                    }
                )
                
                if created:
                    total_created += 1
                else:
                    total_updated += 1
            
            self.stdout.write(f'  Imported {len(images)} templates for {product_slug}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Done! Created: {total_created}, Updated: {total_updated}'))
