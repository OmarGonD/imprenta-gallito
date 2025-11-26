"""
Django management command to import categories data from CSV files

MIGRATION NOTE (2024):
- This command now uses Category and Subcategory from shop.models
- Previously used CatalogCategory and CatalogSubcategory from catalog_models.py
- Those old models are deprecated and will be removed in a future migration
"""
import os
import pandas as pd
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

# Import from the main models.py (migrated from catalog_models.py)
from shop.models import (
    Category,
    Subcategory,
    Product,
    VariantType,
    VariantOption,
    ProductVariantType,
    PriceTier
)


class Command(BaseCommand):
    help = 'Importa el sistema de categorías de productos desde archivos CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar reimportación (elimina datos existentes de categorías)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular importación sin escribir en base de datos'
        )

    def handle(self, *args, **options):
        self.force = options['force']
        self.dry_run = options['dry_run']
        self.data_dir = os.path.join(settings.BASE_DIR, 'static', 'data')
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('IMPORTACIÓN DE CATEGORÍAS DE PRODUCTOS'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  MODO DRY-RUN: No se escribirá en la base de datos\n'))
        
        if self.force and not self.dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  Modo FORCE activado: Se eliminarán datos existentes\n'))
            if not self.confirm_action('¿Está seguro de que desea continuar?'):
                self.stdout.write(self.style.ERROR('Operación cancelada'))
                return
        
        try:
            with transaction.atomic():
                # Verificar que existan los archivos CSV
                self.verify_csv_files()
                
                # Limpiar datos existentes si force=True
                if self.force and not self.dry_run:
                    self.clear_existing_data()
                
                # Importar en orden correcto
                self.stdout.write('\n📦 Iniciando importación...\n')
                
                categories_count = self.import_categories()
                subcategories_count = self.import_subcategories()
                variant_types_count = self.import_variant_types()
                variant_options_count = self.import_variant_options()
                products_count = self.import_products()
                product_variants_count = self.import_product_variant_types()
                price_tiers_count = self.import_price_tiers()
                
                # Resumen
                self.stdout.write('\n' + '=' * 70)
                self.stdout.write(self.style.SUCCESS('✅ IMPORTACIÓN COMPLETADA CON ÉXITO'))
                self.stdout.write('=' * 70)
                self.stdout.write(f'\n📊 Registros importados:')
                self.stdout.write(f'   • Categorías: {categories_count}')
                self.stdout.write(f'   • Subcategorías: {subcategories_count}')
                self.stdout.write(f'   • Productos: {products_count}')
                self.stdout.write(f'   • Tipos de variantes: {variant_types_count}')
                self.stdout.write(f'   • Opciones de variantes: {variant_options_count}')
                self.stdout.write(f'   • Variantes de productos: {product_variants_count}')
                self.stdout.write(f'   • Niveles de precios: {price_tiers_count}')
                self.stdout.write(f'\n📈 Total: {categories_count + subcategories_count + products_count + variant_types_count + variant_options_count + product_variants_count + price_tiers_count} registros')
                
                if self.dry_run:
                    self.stdout.write(self.style.WARNING('\n⚠️  DRY-RUN: Revertiendo transacción...'))
                    raise Exception('Dry run - rolling back')
                    
        except Exception as e:
            if not self.dry_run:
                self.stdout.write(self.style.ERROR(f'\n❌ Error durante la importación: {str(e)}'))
                raise
            else:
                self.stdout.write(self.style.SUCCESS('\n✅ Dry-run completado exitosamente'))

    def confirm_action(self, message):
        """Solicita confirmación del usuario"""
        response = input(f'{message} (si/no): ').lower()
        return response in ['si', 'yes', 'y', 's']

    def verify_csv_files(self):
        """Verifica que existan todos los archivos CSV necesarios"""
        required_files = [
            'categories_complete.csv',
            'subcategories_complete.csv',
            'products_complete.csv',
            'price_tiers_complete.csv',
            'variant_types_complete.csv',
            'variant_options_complete.csv',
            'product_variant_types_complete.csv'
        ]
        
        self.stdout.write('🔍 Verificando archivos CSV...')
        missing_files = []
        
        for filename in required_files:
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                missing_files.append(filename)
            else:
                self.stdout.write(f'   ✓ {filename}')
        
        if missing_files:
            raise FileNotFoundError(
                f'Archivos CSV faltantes: {", ".join(missing_files)}'
            )
        
        self.stdout.write(self.style.SUCCESS('   ✅ Todos los archivos encontrados\n'))

    def clear_existing_data(self):
        """Elimina datos existentes de categorías"""
        self.stdout.write('🗑️  Eliminando datos existentes...')
        
        # Updated to use the new model names
        counts = {
            'PriceTier': PriceTier.objects.all().delete()[0],
            'ProductVariantType': ProductVariantType.objects.all().delete()[0],
            'Product': Product.objects.all().delete()[0],
            'VariantOption': VariantOption.objects.all().delete()[0],
            'VariantType': VariantType.objects.all().delete()[0],
            'Subcategory': Subcategory.objects.all().delete()[0],
            'Category': Category.objects.all().delete()[0],
        }
        
        total = sum(counts.values())
        self.stdout.write(f'   ✓ {total} registros eliminados')
        for model, count in counts.items():
            if count > 0:
                self.stdout.write(f'     - {model}: {count}')
        self.stdout.write('')

    def import_categories(self):
        """Importa categorías desde CSV"""
        self.stdout.write('📁 Importando categorías...')
        filepath = os.path.join(self.data_dir, 'categories_complete.csv')
        df = pd.read_csv(filepath)
        
        created = 0
        updated = 0
        
        for _, row in df.iterrows():
            defaults = {
                'name': row['category_name'],
                'description': row['description'] if pd.notna(row['description']) else '',
                'image_url': row['image_url'] if pd.notna(row['image_url']) else '',
                'display_order': int(row['display_order']),
                'status': row['status']
            }
            
            if not self.dry_run:
                # Using Category instead of CatalogCategory
                _, was_created = Category.objects.update_or_create(
                    slug=row['category_slug'],
                    defaults=defaults
                )
                if was_created:
                    created += 1
                else:
                    updated += 1
            else:
                created += 1
        
        self.stdout.write(f'   ✓ {created} creadas, {updated} actualizadas\n')
        return created + updated

    def import_subcategories(self):
        """Importa subcategorías desde CSV"""
        self.stdout.write('📂 Importando subcategorías...')
        filepath = os.path.join(self.data_dir, 'subcategories_complete.csv')
        df = pd.read_csv(filepath)
        
        created = 0
        updated = 0
        errors = 0
        
        for _, row in df.iterrows():
            try:
                if not self.dry_run:
                    # Using Category instead of CatalogCategory
                    category = Category.objects.get(slug=row['category_slug'])
                    defaults = {
                        'name': row['subcategory_name'],
                        'category': category,
                        'description': row['description'] if pd.notna(row['description']) else '',
                        'image_url': row['image_url'] if pd.notna(row['image_url']) else '',
                        'display_order': int(row['display_order'])
                    }
                    # Using Subcategory instead of CatalogSubcategory
                    _, was_created = Subcategory.objects.update_or_create(
                        slug=row['subcategory_slug'],
                        defaults=defaults
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                else:
                    created += 1
            except Category.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'   ⚠️  Categoría no encontrada: {row["category_slug"]}'
                ))
                errors += 1
        
        self.stdout.write(f'   ✓ {created} creadas, {updated} actualizadas')
        if errors > 0:
            self.stdout.write(self.style.WARNING(f'   ⚠️  {errors} errores\n'))
        else:
            self.stdout.write('')
        return created + updated

    def import_variant_types(self):
        """Importa tipos de variantes desde CSV"""
        self.stdout.write('🎨 Importando tipos de variantes...')
        filepath = os.path.join(self.data_dir, 'variant_types_complete.csv')
        df = pd.read_csv(filepath)
        
        created = 0
        updated = 0
        
        for _, row in df.iterrows():
            defaults = {
                'name': row['variant_type_name'],
                'description': row['description'] if pd.notna(row['description']) else '',
                'is_required': str(row['is_required']).lower() == 'true',
                'allows_multiple': str(row['allows_multiple']).lower() == 'true',
                'display_order': int(row['display_order']),
                'applies_to': row['applies_to'] if pd.notna(row['applies_to']) else None
            }
            
            if not self.dry_run:
                _, was_created = VariantType.objects.update_or_create(
                    slug=row['variant_type_slug'],
                    defaults=defaults
                )
                if was_created:
                    created += 1
                else:
                    updated += 1
            else:
                created += 1
        
        self.stdout.write(f'   ✓ {created} creados, {updated} actualizados\n')
        return created + updated

    def import_variant_options(self):
        """Importa opciones de variantes desde CSV"""
        self.stdout.write('🎯 Importando opciones de variantes...')
        filepath = os.path.join(self.data_dir, 'variant_options_complete.csv')
        df = pd.read_csv(filepath)
        
        created = 0
        updated = 0
        errors = 0
        
        for _, row in df.iterrows():
            try:
                if not self.dry_run:
                    variant_type = VariantType.objects.get(slug=row['variant_type_slug'])
                    defaults = {
                        'name': row['option_name'],
                        'variant_type': variant_type,
                        'description': row['description'] if pd.notna(row['description']) else '',
                        'additional_price': Decimal(str(row['additional_price'])),
                        'image_url': row['image_url'] if pd.notna(row['image_url']) else None,
                        'display_order': int(row['display_order'])
                    }
                    _, was_created = VariantOption.objects.update_or_create(
                        slug=row['option_slug'],
                        defaults=defaults
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                else:
                    created += 1
            except VariantType.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'   ⚠️  Tipo de variante no encontrado: {row["variant_type_slug"]}'
                ))
                errors += 1
        
        self.stdout.write(f'   ✓ {created} creadas, {updated} actualizadas')
        if errors > 0:
            self.stdout.write(self.style.WARNING(f'   ⚠️  {errors} errores\n'))
        else:
            self.stdout.write('')
        return created + updated

    def import_products(self):
        """Importa productos desde CSV"""
        self.stdout.write('🛍️  Importando productos...')
        filepath = os.path.join(self.data_dir, 'products_complete.csv')
        df = pd.read_csv(filepath)
        
        created = 0
        updated = 0
        errors = 0
        
        for _, row in df.iterrows():
            try:
                if not self.dry_run:
                    # Using Category instead of CatalogCategory
                    category = Category.objects.get(slug=row['category_slug'])
                    subcategory = None
                    if pd.notna(row['subcategory_slug']):
                        try:
                            # Using Subcategory instead of CatalogSubcategory
                            subcategory = Subcategory.objects.get(slug=row['subcategory_slug'])
                        except Subcategory.DoesNotExist:
                            pass
                    
                    defaults = {
                        'name': row['product_name'],
                        'category': category,
                        'subcategory': subcategory,
                        'sku': row['sku'],
                        'description': row['description'] if pd.notna(row['description']) else '',
                        'base_image_url': row['base_image_url'] if pd.notna(row['base_image_url']) else '',
                        'status': row['status']
                    }
                    _, was_created = Product.objects.update_or_create(
                        slug=row['product_slug'],
                        defaults=defaults
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                else:
                    created += 1
            except Category.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'   ⚠️  Categoría no encontrada para producto: {row["product_slug"]}'
                ))
                errors += 1
        
        self.stdout.write(f'   ✓ {created} creados, {updated} actualizados')
        if errors > 0:
            self.stdout.write(self.style.WARNING(f'   ⚠️  {errors} errores\n'))
        else:
            self.stdout.write('')
        return created + updated

    def import_product_variant_types(self):
        """Importa relaciones producto-variantes desde CSV"""
        self.stdout.write('🔗 Importando variantes de productos...')
        filepath = os.path.join(self.data_dir, 'product_variant_types_complete.csv')
        df = pd.read_csv(filepath)
        
        created = 0
        skipped = 0
        errors = 0
        
        for _, row in df.iterrows():
            try:
                if not self.dry_run:
                    product = Product.objects.get(slug=row['product_slug'])
                    variant_type = VariantType.objects.get(slug=row['variant_type_slug'])
                    
                    _, was_created = ProductVariantType.objects.get_or_create(
                        product=product,
                        variant_type=variant_type
                    )
                    if was_created:
                        created += 1
                    else:
                        skipped += 1
                else:
                    created += 1
            except (Product.DoesNotExist, VariantType.DoesNotExist) as e:
                errors += 1
        
        self.stdout.write(f'   ✓ {created} creadas, {skipped} ya existían')
        if errors > 0:
            self.stdout.write(self.style.WARNING(f'   ⚠️  {errors} errores\n'))
        else:
            self.stdout.write('')
        return created

    def import_price_tiers(self):
        """Importa niveles de precio desde CSV"""
        self.stdout.write('💰 Importando niveles de precios...')
        filepath = os.path.join(self.data_dir, 'price_tiers_complete.csv')
        df = pd.read_csv(filepath)
        
        created = 0
        updated = 0
        errors = 0
        
        for _, row in df.iterrows():
            try:
                if not self.dry_run:
                    product = Product.objects.get(slug=row['product_slug'])
                    defaults = {
                        'max_quantity': int(row['max_quantity']),
                        'unit_price': Decimal(str(row['unit_price'])),
                        'discount_percentage': int(row['discount_percentage'])
                    }
                    _, was_created = PriceTier.objects.update_or_create(
                        product=product,
                        min_quantity=int(row['min_quantity']),
                        defaults=defaults
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                else:
                    created += 1
            except Product.DoesNotExist:
                errors += 1
        
        self.stdout.write(f'   ✓ {created} creados, {updated} actualizados')
        if errors > 0:
            self.stdout.write(self.style.WARNING(f'   ⚠️  {errors} errores\n'))
        else:
            self.stdout.write('')
        return created + updated
