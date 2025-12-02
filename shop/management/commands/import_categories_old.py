"""
Django management command to import categories data from CSV files

MIGRATION NOTE (2024):
- This command now uses Category and Subcategory from shop.models
- Previously used CatalogCategory and CatalogSubcategory from catalog_models.py
- Those old models are deprecated and will be removed in a future migration
"""
import os
import pandas as pd
import csv
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

# Import from the main models.py (migrated from catalog_models.py)
from shop.models import (
    Category,
    Subcategory,
    Product,
    DesignTemplate,
    VariantType,
    VariantOption,
    ProductVariantType,
    PriceTier
)



class Command(BaseCommand):
    help = 'Importa el sistema de categorías de productos desde archivos CSV'

    # Mapeo de caracteres cirílicos a latinos acentuados
    # Estos caracteres aparecen por corrupción de datos en los CSVs
    CYRILLIC_TO_LATIN = {
        '\u0443': 'ó',  # у -> ó (Algodуn -> Algodón)
        '\u0423': 'Ó',  # У -> Ó
        '\u0431': 'á',  # б -> á (Estбndar -> Estándar)
        '\u0411': 'Á',  # Б -> Á
        '\u0441': 'ñ',  # с -> ñ (Cбсamo -> Cáñamo)
        '\u0421': 'Ñ',  # С -> Ñ
        '\u043d': 'í',  # н -> í (Bolнgrafo -> Bolígrafo)
        '\u041d': 'Í',  # Н -> Í
        '\u0456': 'i',  # і -> i
        '\u0406': 'I',  # І -> I
        '\u0435': 'e',  # е -> e
        '\u0415': 'E',  # Е -> E
        '\u043e': 'o',  # о -> o
        '\u041e': 'O',  # О -> O
        '\u0430': 'a',  # а -> a
        '\u0410': 'A',  # А -> A
        '\u0440': 'p',  # р -> p
        '\u0420': 'P',  # Р -> P
        '\u0445': 'x',  # х -> x
        '\u0425': 'X',  # Х -> X
        '\u0451': 'ё',  # ё -> ё
    }

    def fix_cyrillic_homoglyphs(self, text):
        """
        Reemplaza caracteres cirílicos que parecen latinos.
        Ejemplo: "Algodуn" (con у cirílico) -> "Algodón"
        """
        if not isinstance(text, str):
            return text
        
        result = text
        for cyrillic, latin in self.CYRILLIC_TO_LATIN.items():
            result = result.replace(cyrillic, latin)
        return result

    def fix_mojibake(self, text):
        """
        Corrige caracteres mojibake en un texto.
        Mojibake ocurre cuando texto UTF-8 es interpretado como Latin-1/Windows-1252.
        
        Soporta doble o triple mojibake aplicando correcciones repetidamente.
        Ejemplo: "AlgodÑƒn" -> "Algodón"
        """
        if not isinstance(text, str):
            return text
        
        result = text
        max_iterations = 3  # Prevenir loops infinitos
        
        for _ in range(max_iterations):
            try:
                # Re-codificar: latin-1 -> bytes -> utf-8
                fixed = result.encode('latin-1').decode('utf-8')
                if fixed == result:
                    # Ya no hay cambios, terminamos
                    break
                result = fixed
            except (UnicodeDecodeError, UnicodeEncodeError):
                # No se puede corregir más
                break
        
        # Corregir caracteres cirílicos DESPUÉS del mojibake
        result = self.fix_cyrillic_homoglyphs(result)
        
        return result

    def fix_dataframe_encoding(self, df):
        """
        Aplica corrección de mojibake a todas las columnas de texto del DataFrame.
        """
        for column in df.columns:
            if df[column].dtype == 'object':  # Columnas de texto
                df[column] = df[column].apply(
                    lambda x: self.fix_mojibake(x) if isinstance(x, str) else x
                )
        return df

    def safe_read_csv(self, filepath):
        """
        Lee CSV probando múltiples codificaciones y corrige problemas de mojibake.
        """
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'windows-1252']
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    sample = f.read(2048)
                    dialect = csv.Sniffer().sniff(sample)
                    f.seek(0)
                    df = pd.read_csv(f, encoding=encoding, dialect=dialect)
                    
                    # Aplicar corrección de mojibake a todo el DataFrame
                    df = self.fix_dataframe_encoding(df)
                    
                    return df
            except (UnicodeDecodeError, csv.Error):
                continue
        
        raise ValueError(f"Could not read {filepath} with any supported encoding or delimiter")

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
        parser.add_argument(
            '--no-fix-encoding',
            action='store_true',
            help='Desactivar corrección automática de caracteres (mojibake)'
        )

    def handle(self, *args, **options):
        self.force = options['force']
        self.dry_run = options['dry_run']
        self.fix_encoding = not options.get('no_fix_encoding', False)
        self.data_dir = os.path.join(settings.BASE_DIR, 'static', 'data')
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('IMPORTACIÓN DE CATEGORÍAS DE PRODUCTOS'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        if self.fix_encoding:
            self.stdout.write(self.style.SUCCESS(
                '\n[OK] Correccion automatica de caracteres (mojibake) ACTIVADA'
            ))
            self.stdout.write('  (Ej: "DiseA+-o" se corrige a "Diseno")\n')
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('\nWARNING MODO DRY-RUN: No se escribirá en la base de datos\n'))
        
        if self.force and not self.dry_run:
            self.stdout.write(self.style.WARNING('\nWARNING Modo FORCE activado: Se eliminarán datos existentes\n'))
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
                self.stdout.write('\nIniciando importación...\n')
                
                categories_count = self.import_categories()
                subcategories_count = self.import_subcategories()
                variant_types_count = self.import_variant_types()
                variant_options_count = self.import_variant_options()
                products_count = self.import_products()
                product_variants_count = self.import_product_variant_types()
                price_tiers_count = self.import_price_tiers()
                
                # Resumen
                self.stdout.write('\n' + '=' * 70)
                self.stdout.write(self.style.SUCCESS('IMPORTACIÓN COMPLETADA CON ÉXITO'))
                self.stdout.write('=' * 70)
                self.stdout.write(f'\nRegistros importados:')
                self.stdout.write(f'   • Categorías: {categories_count}')
                self.stdout.write(f'   • Subcategorías: {subcategories_count}')
                self.stdout.write(f'   • Productos: {products_count}')
                self.stdout.write(f'   • Tipos de variantes: {variant_types_count}')
                self.stdout.write(f'   • Opciones de variantes: {variant_options_count}')
                self.stdout.write(f'   • Variantes de productos: {product_variants_count}')
                self.stdout.write(f'   • Niveles de precios: {price_tiers_count}')
                self.stdout.write(f'\nTotal: {categories_count + subcategories_count + products_count + variant_types_count + variant_options_count + product_variants_count + price_tiers_count} registros')
                
                if self.dry_run:
                    self.stdout.write(self.style.WARNING('\nWARNING DRY-RUN: Revertiendo transacción...'))
                    raise Exception('Dry run - rolling back')
                    
        except Exception as e:
            if not self.dry_run:
                self.stdout.write(self.style.ERROR(f'\nError durante la importación: {str(e)}'))
                raise
            else:
                self.stdout.write(self.style.SUCCESS('\nOK Dry-run completado exitosamente'))

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
        
        self.stdout.write('Verificando archivos CSV...')
        missing_files = []
        
        for filename in required_files:
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                missing_files.append(filename)
            else:
                self.stdout.write(f'   OK {filename}')
        
        if missing_files:
            raise FileNotFoundError(
                f'Archivos CSV faltantes: {", ".join(missing_files)}'
            )
        
        self.stdout.write(self.style.SUCCESS('   OK Todos los archivos encontrados\n'))

    def clear_existing_data(self):
        """Elimina datos existentes de categorías"""
        self.stdout.write('Eliminando datos existentes...')
        
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
        self.stdout.write(f'   OK {total} registros eliminados')
        for model, count in counts.items():
            if count > 0:
                self.stdout.write(f'     - {model}: {count}')
        self.stdout.write('')

    def import_categories(self):
        """Importa categorías desde CSV"""
        self.stdout.write('Importando categorías...')
        filepath = os.path.join(self.data_dir, 'categories_complete.csv')
        df = self.safe_read_csv(filepath)
        
        created = 0
        updated = 0
        
        for _, row in df.iterrows():
            defaults = {
                'name': row['category_name'],
                'description': row['description'] if pd.notna(row['description']) else '',
                'image_url': row['image_url'] if pd.notna(row['image_url']) else None,
                'display_order': int(row['display_order']),
                'status': row['status'] if 'status' in row else 'active'
            }
            if not self.dry_run:
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
        
        self.stdout.write(f'   OK {created} creadas, {updated} actualizadas\n')
        return created + updated

    def import_subcategories(self):
        """Importa subcategorías desde CSV"""
        self.stdout.write('Importando subcategorías...')
        filepath = os.path.join(self.data_dir, 'subcategories_complete.csv')
        df = self.safe_read_csv(filepath)
        
        created = 0
        updated = 0
        errors = 0
        
        for _, row in df.iterrows():
            try:
                if not self.dry_run:
                    category = Category.objects.get(slug=row['category_slug'])
                    defaults = {
                        'name': row['subcategory_name'],
                        'category': category,
                        'description': row['description'] if pd.notna(row['description']) else '',
                        'image_url': row['image_url'] if pd.notna(row['image_url']) else None,
                        'display_order': int(row['display_order']),
                    }
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
                    f'   WARNING Categoría no encontrada: {row["category_slug"]}'
                ))
                errors += 1
        
        self.stdout.write(f'   OK {created} creadas, {updated} actualizadas')
        if errors > 0:
            self.stdout.write(self.style.WARNING(f'   WARNING {errors} errores\n'))
        else:
            self.stdout.write('')
        return created + updated

    def import_variant_types(self):
        """Importa tipos de variantes desde CSV"""
        self.stdout.write('Importando tipos de variantes...')
        filepath = os.path.join(self.data_dir, 'variant_types_complete.csv')
        df = self.safe_read_csv(filepath)
        
        created = 0
        updated = 0
        
        for _, row in df.iterrows():
            defaults = {
                'name': row['variant_type_name'],
                'description': row['description'] if pd.notna(row['description']) else '',
                'display_order': int(row['display_order'])
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
        
        self.stdout.write(f'   OK {created} creados, {updated} actualizados\n')
        return created + updated

    def import_variant_options(self):
        """Importa opciones de variantes desde CSV"""
        self.stdout.write('Importando opciones de variantes...')
        filepath = os.path.join(self.data_dir, 'variant_options_complete.csv')
        df = self.safe_read_csv(filepath)
        
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
                    f'   WARNING Tipo de variante no encontrado: {row["variant_type_slug"]}'
                ))
                errors += 1
        
        self.stdout.write(f'   OK {created} creadas, {updated} actualizadas')
        if errors > 0:
            self.stdout.write(self.style.WARNING(f'   WARNING {errors} errores\n'))
        else:
            self.stdout.write('')
        return created + updated

    def import_products(self):
        """Importa productos desde CSV"""
        self.stdout.write('Importando productos...')
        filepath = os.path.join(self.data_dir, 'products_complete.csv')
        df = self.safe_read_csv(filepath)
        
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
                    f'   WARNING Categoría no encontrada para producto: {row["product_slug"]}'
                ))
                errors += 1
        
        self.stdout.write(f'   OK {created} creados, {updated} actualizados')
        if errors > 0:
            self.stdout.write(self.style.WARNING(f'   WARNING {errors} errores\n'))
        else:
            self.stdout.write('')
        return created + updated

    def import_product_variant_types(self):
        """Importa relaciones producto-variantes desde CSV"""
        self.stdout.write('Importando variantes de productos...')
        filepath = os.path.join(self.data_dir, 'product_variant_types_complete.csv')
        df = self.safe_read_csv(filepath)
        
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
        
        self.stdout.write(f'   OK {created} creadas, {skipped} ya existían')
        if errors > 0:
            self.stdout.write(self.style.WARNING(f'   WARNING {errors} errores\n'))
        else:
            self.stdout.write('')
        return created

    def import_price_tiers(self):
        """Importa niveles de precio desde CSV"""
        self.stdout.write('Importando niveles de precios...')
        filepath = os.path.join(self.data_dir, 'price_tiers_complete.csv')
        df = self.safe_read_csv(filepath)
        
        created = 0
        updated = 0
        errors = 0
        
        for _, row in df.iterrows():
            try:
                if not self.dry_run:
                    product = Product.objects.get(slug=row['product_slug'])
                    defaults = {
                        'max_quantity': int(row['max_quan']),
                        'unit_price': Decimal(str(row['unit_price'])),
                        'discount_percentage': int(row['discount_percent'])
                    }
                    _, was_created = PriceTier.objects.update_or_create(
                        product=product,
                        min_quantity=int(row['min_quan']),
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
        
        self.stdout.write(f'   OK {created} creados, {updated} actualizados')
        if errors > 0:
            self.stdout.write(self.style.WARNING(f'   WARNING {errors} errores\n'))
        else:
            self.stdout.write('')
        return created + updated
