"""
Django management command to import catalog data from CSV files

INCLUDES:
- Categories (with category_type field)
- Subcategories (with display_style field)
- Products (with colors and sizes for clothing)
- ProductColor (NEW - for clothing colors)
- ProductSize (NEW - for clothing sizes)
- ProductImage (NEW - product images by color)
- Variant Types & Options
- Price Tiers
- Design Templates

Usage:
    python manage.py import_catalog
    python manage.py import_catalog --dry-run
    python manage.py import_catalog --force
    python manage.py import_catalog --only=templates
    python manage.py import_catalog --only=colors
    python manage.py import_catalog --only=polos
"""
import os
import pandas as pd
import csv
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from shop.models import (
    Category,
    Subcategory,
    Product,
    ProductColor,
    ProductSize,
    ProductImage,
    DesignTemplate,
    VariantType,
    VariantOption,
    ProductVariantType,
    PriceTier
)


# =============================================================================
# TALLAS ESTÁNDAR PARA ROPA
# =============================================================================
STANDARD_SIZES = [
    ('XS', 'Extra Small', 0),
    ('S', 'Small', 1),
    ('M', 'Medium', 2),
    ('L', 'Large', 3),
    ('XL', 'Extra Large', 4),
    ('XXL', 'Double Extra Large', 5),
    ('2XL', 'Double Extra Large', 5),
    ('3XL', 'Triple Extra Large', 6),
]


class Command(BaseCommand):
    help = 'Importa el catálogo de productos desde archivos CSV'

    # Mapeo de caracteres cirílicos a latinos acentuados
    CYRILLIC_TO_LATIN = {
        '\u0443': 'ó',  # у -> ó
        '\u0423': 'Ó',  # У -> Ó
        '\u0431': 'á',  # б -> á
        '\u0411': 'Á',  # Б -> Á
        '\u0441': 'ñ',  # с -> ñ
        '\u0421': 'Ñ',  # С -> Ñ
        '\u043d': 'í',  # н -> í
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
        """Reemplaza caracteres cirílicos que parecen latinos."""
        if not isinstance(text, str):
            return text
        
        result = text
        for cyrillic, latin in self.CYRILLIC_TO_LATIN.items():
            result = result.replace(cyrillic, latin)
        return result

    def fix_mojibake(self, text):
        """Corrige caracteres mojibake en un texto."""
        if not isinstance(text, str):
            return text
        
        result = text
        max_iterations = 3
        
        for _ in range(max_iterations):
            try:
                # Intenta corregir UTF-8 que fue leído como Latin-1
                fixed = result.encode('latin-1').decode('utf-8')
                if fixed == result:
                    break
                result = fixed
            except (UnicodeDecodeError, UnicodeEncodeError):
                # Si falla, el texto ya está bien o es Latin-1 puro
                break
        
        # Siempre aplicar limpieza de cirílicos
        result = self.fix_cyrillic_homoglyphs(result)
        return result

    def fix_dataframe_encoding(self, df):
        """Aplica corrección de mojibake a todas las columnas de texto."""
        for column in df.columns:
            if df[column].dtype == 'object':
                df[column] = df[column].apply(
                    lambda x: self.fix_mojibake(x) if isinstance(x, str) else x
                )
        return df

    def detect_delimiter(self, filepath):
        """Detecta el delimitador del CSV."""
        with open(filepath, 'r', encoding='latin-1') as f:
            sample = f.read(4096)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
                return dialect.delimiter
            except csv.Error:
                # Si hay más ; que , probablemente sea ;
                if sample.count(';') > sample.count(','):
                    return ';'
                return ','

    def safe_read_csv(self, filepath, encoding='latin-1'):
        """
        Lee CSV con encoding mixto (Latin-1 + UTF-8).
        
        Estrategia:
        1. Intentar primero UTF-8 para archivos nuevos
        2. Si falla, usar Latin-1 (acepta cualquier byte 0-255)
        3. Aplicar fix_mojibake()
        """
        # Detectar delimitador
        delimiter = self.detect_delimiter(filepath)
        
        # Intentar primero con UTF-8 para archivos nuevos
        try:
            df = pd.read_csv(filepath, encoding='utf-8', delimiter=delimiter)
        except UnicodeDecodeError:
            # Si falla, usar Latin-1
            df = pd.read_csv(filepath, encoding=encoding, delimiter=delimiter)
        
        # Aplicar correcciones de encoding si está habilitado
        if self.fix_encoding:
            df = self.fix_dataframe_encoding(df)
        
        return df

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar reimportación (elimina datos existentes)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular importación sin escribir en base de datos'
        )
        parser.add_argument(
            '--no-fix-encoding',
            action='store_true',
            help='Desactivar corrección automática de caracteres'
        )
        parser.add_argument(
            '--only',
            type=str,
            choices=['categories', 'subcategories', 'products', 'variants', 
                     'prices', 'templates', 'colors', 'sizes', 'images', 'polos'],
            help='Importar solo un tipo específico de datos'
        )

    def handle(self, *args, **options):
        self.force = options['force']
        self.dry_run = options['dry_run']
        self.fix_encoding = not options.get('no_fix_encoding', False)
        self.only = options.get('only')
        self.data_dir = os.path.join(settings.BASE_DIR, 'static', 'data')
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('IMPORTACIÓN DEL CATÁLOGO DE PRODUCTOS'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        if self.fix_encoding:
            self.stdout.write(self.style.SUCCESS(
                '\n[OK] Corrección automática de caracteres ACTIVADA'
            ))
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('\nMODO DRY-RUN: No se escribirá en la base de datos\n'))
        
        if self.only:
            self.stdout.write(self.style.WARNING(f'\nIMPORTANDO SOLO: {self.only}\n'))
        
        if self.force and not self.dry_run:
            self.stdout.write(self.style.WARNING('\nModo FORCE activado: Se eliminarán datos existentes\n'))
            if not self.confirm_action('¿Está seguro de que desea continuar?'):
                self.stdout.write(self.style.ERROR('Operación cancelada'))
                return
        
        try:
            with transaction.atomic():
                # Verificar archivos CSV
                self.verify_csv_files()
                
                # Limpiar datos si force=True
                if self.force and not self.dry_run:
                    self.clear_existing_data()
                
                self.stdout.write('\nIniciando importación...\n')
                
                # Contadores
                counts = {}
                
                # Importar según --only o todo
                if not self.only or self.only == 'categories':
                    counts['categories'] = self.import_categories()
                
                if not self.only or self.only == 'subcategories':
                    counts['subcategories'] = self.import_subcategories()
                
                # NUEVO: Importar colores y tallas primero (antes de productos)
                if not self.only or self.only in ['colors', 'polos']:
                    counts['colors'] = self.import_colors()
                
                if not self.only or self.only in ['sizes', 'polos']:
                    counts['sizes'] = self.import_sizes()
                
                if not self.only or self.only == 'variants':
                    counts['variant_types'] = self.import_variant_types()
                    counts['variant_options'] = self.import_variant_options()
                
                if not self.only or self.only in ['products', 'polos']:
                    counts['products'] = self.import_products()
                    counts['product_variants'] = self.import_product_variant_types()
                
                # NUEVO: Importar imágenes de productos por color
                if not self.only or self.only in ['images', 'polos']:
                    counts['product_images'] = self.import_product_images()
                
                if not self.only or self.only == 'prices':
                    counts['price_tiers'] = self.import_price_tiers()
                
                if not self.only or self.only == 'templates':
                    counts['design_templates'] = self.import_design_templates()
                
                # Resumen
                self.stdout.write('\n' + '=' * 70)
                self.stdout.write(self.style.SUCCESS('IMPORTACIÓN COMPLETADA'))
                self.stdout.write('=' * 70)
                self.stdout.write(f'\nRegistros importados:')
                
                for key, count in counts.items():
                    if count > 0:
                        self.stdout.write(f'   • {key.replace("_", " ").title()}: {count}')
                
                total = sum(counts.values())
                self.stdout.write(f'\nTotal: {total} registros')
                
                if self.dry_run:
                    self.stdout.write(self.style.WARNING('\nDRY-RUN: Revertiendo transacción...'))
                    raise Exception('Dry run - rolling back')
                    
        except Exception as e:
            if not self.dry_run:
                self.stdout.write(self.style.ERROR(f'\nError: {str(e)}'))
                raise
            else:
                self.stdout.write(self.style.SUCCESS('\n✓ Dry-run completado'))

    def confirm_action(self, message):
        """Solicita confirmación del usuario"""
        response = input(f'{message} (si/no): ').lower()
        return response in ['si', 'yes', 'y', 's']

    def verify_csv_files(self):
        """Verifica que existan los archivos CSV necesarios"""
        required_files = [
            'categories_complete.csv',
            'subcategories_complete.csv',
            'products_complete.csv',
            'price_tiers_complete.csv',
            'variant_types_complete.csv',
            'variant_options_complete.csv',
            'product_variant_types_complete.csv'
        ]
        
        optional_files = [
            'design_templates.csv',
            'polos_colors.csv',      # NUEVO
            'polos_images.csv',      # NUEVO
        ]
        
        self.stdout.write('Verificando archivos CSV...')
        missing_files = []
        
        for filename in required_files:
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                missing_files.append(filename)
            else:
                self.stdout.write(f'   OK {filename}')
        
        for filename in optional_files:
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                self.stdout.write(f'   OK {filename} (opcional)')
            else:
                self.stdout.write(self.style.WARNING(f'   -- {filename} (no encontrado, opcional)'))
        
        if missing_files:
            raise FileNotFoundError(
                f'Archivos CSV faltantes: {", ".join(missing_files)}'
            )
        
        self.stdout.write(self.style.SUCCESS('   ✓ Verificación completada\n'))

    def clear_existing_data(self):
        """Elimina datos existentes"""
        self.stdout.write('Eliminando datos existentes...')
        
        counts = {
            'ProductImage': ProductImage.objects.all().delete()[0],
            'DesignTemplate': DesignTemplate.objects.all().delete()[0],
            'PriceTier': PriceTier.objects.all().delete()[0],
            'ProductVariantType': ProductVariantType.objects.all().delete()[0],
            'Product': Product.objects.all().delete()[0],
            'VariantOption': VariantOption.objects.all().delete()[0],
            'VariantType': VariantType.objects.all().delete()[0],
            'Subcategory': Subcategory.objects.all().delete()[0],
            'Category': Category.objects.all().delete()[0],
            'ProductColor': ProductColor.objects.all().delete()[0],
            'ProductSize': ProductSize.objects.all().delete()[0],
        }
        
        total = sum(counts.values())
        self.stdout.write(f'   OK {total} registros eliminados')
        for model, count in counts.items():
            if count > 0:
                self.stdout.write(f'     - {model}: {count}')
        self.stdout.write('')

    # =========================================================================
    # NUEVO: IMPORTAR COLORES
    # =========================================================================
    def import_colors(self):
        """Importa colores de productos desde CSV"""
        self.stdout.write('Importando colores...')
        filepath = os.path.join(self.data_dir, 'polos_colors.csv')
        
        if not os.path.exists(filepath):
            self.stdout.write(self.style.WARNING(
                '   SKIP Archivo polos_colors.csv no encontrado\n'
            ))
            return 0
        
        df = self.safe_read_csv(filepath, encoding='utf-8')
        
        created = 0
        updated = 0
        
        for _, row in df.iterrows():
            try:
                slug = str(row.get('slug', '')).strip()
                if not slug:
                    continue
                
                hex_code = str(row.get('hex_code', '')).strip()
                if not hex_code.startswith('#'):
                    hex_code = f'#{hex_code}'
                
                defaults = {
                    'name': row.get('name', slug.replace('-', ' ').title()),
                    'hex_code': hex_code,
                    'display_order': int(row.get('display_order', 0)),
                    'is_active': str(row.get('is_active', 'True')).lower() == 'true',
                }
                
                if not self.dry_run:
                    _, was_created = ProductColor.objects.update_or_create(
                        slug=slug,
                        defaults=defaults
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                else:
                    created += 1
                    
            except Exception as e:
                self.stdout.write(self.style.WARNING(
                    f'   WARNING Error en color {row.get("slug")}: {str(e)}'
                ))
        
        self.stdout.write(f'   OK {created} creados, {updated} actualizados\n')
        return created + updated

    # =========================================================================
    # NUEVO: IMPORTAR TALLAS
    # =========================================================================
    def import_sizes(self):
        """Importa tallas estándar de ropa"""
        self.stdout.write('Importando tallas estándar...')
        
        created = 0
        updated = 0
        
        for name, display_name, order in STANDARD_SIZES:
            defaults = {
                'display_name': display_name,
                'size_type': 'clothing',
                'display_order': order,
                'is_active': True,
            }
            
            if not self.dry_run:
                _, was_created = ProductSize.objects.update_or_create(
                    name=name,
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

    # =========================================================================
    # NUEVO: IMPORTAR IMÁGENES DE PRODUCTOS POR COLOR
    # =========================================================================
    def import_product_images(self):
        """Importa imágenes de productos por color desde CSV"""
        self.stdout.write('Importando imágenes de productos...')
        filepath = os.path.join(self.data_dir, 'polos_images.csv')
        
        if not os.path.exists(filepath):
            self.stdout.write(self.style.WARNING(
                '   SKIP Archivo polos_images.csv no encontrado\n'
            ))
            return 0
        
        df = self.safe_read_csv(filepath, encoding='utf-8')
        
        created = 0
        skipped = 0
        errors = 0
        
        for _, row in df.iterrows():
            try:
                product_slug = str(row.get('product_slug', '')).strip()
                image_url = str(row.get('image_url', '')).strip()
                
                if not product_slug or not image_url:
                    skipped += 1
                    continue
                
                if not self.dry_run:
                    try:
                        product = Product.objects.get(slug=product_slug)
                    except Product.DoesNotExist:
                        skipped += 1
                        continue
                    
                    color = None
                    color_slug = str(row.get('color_slug', '')).strip()
                    if color_slug:
                        try:
                            color = ProductColor.objects.get(slug=color_slug)
                        except ProductColor.DoesNotExist:
                            pass
                    
                    is_primary = str(row.get('is_primary', 'False')).lower() == 'true'
                    
                    _, was_created = ProductImage.objects.update_or_create(
                        product=product,
                        color=color,
                        image_url=image_url,
                        defaults={
                            'is_primary': is_primary,
                            'display_order': int(row.get('display_order', 0)),
                        }
                    )
                    if was_created:
                        created += 1
                else:
                    created += 1
                    
            except Exception as e:
                errors += 1
                self.stdout.write(self.style.WARNING(
                    f'   WARNING Error en imagen: {str(e)}'
                ))
        
        self.stdout.write(f'   OK {created} creadas, {skipped} omitidas')
        if errors > 0:
            self.stdout.write(self.style.WARNING(f'   WARNING {errors} errores\n'))
        else:
            self.stdout.write('')
        return created

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
                'status': row['status'] if 'status' in row else 'active',
            }
            
            # Nuevo campo category_type (si existe en CSV)
            if 'category_type' in row and pd.notna(row['category_type']):
                defaults['category_type'] = row['category_type']
            
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
                    
                    # Nuevo campo display_style (si existe en CSV)
                    if 'display_style' in row and pd.notna(row['display_style']):
                        defaults['display_style'] = row['display_style']
                    
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

    def parse_colors_hex(self, colors_hex_str):
        """
        Parsea el string de colores con hex
        Formato: "negro:04080b|blanco:ffffff|rojo:cd2f3c"
        Retorna: {slug: hex_code}
        """
        colors = {}
        if not colors_hex_str or pd.isna(colors_hex_str):
            return colors
        
        for item in str(colors_hex_str).split('|'):
            if ':' in item:
                parts = item.split(':', 1)
                if len(parts) == 2:
                    slug, hex_code = parts
                    hex_code = hex_code.strip()
                    if not hex_code.startswith('#'):
                        hex_code = f'#{hex_code}'
                    colors[slug.strip()] = hex_code
        
        return colors

    def import_products(self):
        """Importa productos desde CSV - ACTUALIZADO para soportar colores y campos adicionales"""
        self.stdout.write('Importando productos...')
        filepath = os.path.join(self.data_dir, 'products_complete.csv')
        df = self.safe_read_csv(filepath)
        
        created = 0
        updated = 0
        errors = 0
        
        for _, row in df.iterrows():
            try:
                product_slug = str(row.get('product_slug', '')).strip()
                if not product_slug:
                    continue
                
                if not self.dry_run:
                    category_slug = str(row.get('category_slug', '')).strip()
                    if not category_slug:
                        continue
                    
                    category = Category.objects.get(slug=category_slug)
                    subcategory = None
                    
                    subcategory_slug = row.get('subcategory_slug')
                    if pd.notna(subcategory_slug) and subcategory_slug:
                        try:
                            subcategory = Subcategory.objects.get(slug=str(subcategory_slug).strip())
                        except Subcategory.DoesNotExist:
                            pass
                    
                    defaults = {
                        'name': row['product_name'],
                        'category': category,
                        'subcategory': subcategory,
                        'sku': row['sku'],
                        'description': row['description'] if pd.notna(row['description']) else '',
                        'base_image_url': row['base_image_url'] if pd.notna(row['base_image_url']) else '',
                        'status': row['status'] if pd.notna(row.get('status')) else 'active',
                    }
                    
                    # NUEVO: guardar marca en material (campo existente)
                    if 'marca' in row and pd.notna(row['marca']):
                        defaults['material'] = row['marca']
                    
                    # NUEVO: guardar género/tipo_cuello/tipo_manga en features
                    features_parts = []
                    if 'genero' in row and pd.notna(row['genero']):
                        features_parts.append(f"genero:{row['genero']}")
                    if 'tipo_cuello' in row and pd.notna(row['tipo_cuello']):
                        features_parts.append(f"cuello:{row['tipo_cuello']}")
                    if 'tipo_manga' in row and pd.notna(row['tipo_manga']):
                        features_parts.append(f"manga:{row['tipo_manga']}")
                    
                    if features_parts:
                        defaults['features'] = ','.join(features_parts)
                    
                    product, was_created = Product.objects.update_or_create(
                        slug=product_slug,
                        defaults=defaults
                    )
                    
                    # NUEVO: Asignar colores si existen
                    colors_hex_str = row.get('colores_hex', '')
                    if colors_hex_str and pd.notna(colors_hex_str):
                        colors_data = self.parse_colors_hex(colors_hex_str)
                        
                        for color_slug, hex_code in colors_data.items():
                            color, _ = ProductColor.objects.get_or_create(
                                slug=color_slug,
                                defaults={
                                    'name': color_slug.replace('-', ' ').title(),
                                    'hex_code': hex_code,
                                    'is_active': True,
                                }
                            )
                            product.available_colors.add(color)
                    
                    # NUEVO: Asignar tallas estándar para ropa
                    if category_slug == 'ropa-bolsos':
                        sizes = ProductSize.objects.filter(
                            name__in=['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                            is_active=True
                        )
                        product.available_sizes.set(sizes)
                    
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                else:
                    created += 1
                    
            except Category.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'   WARNING Categoría no encontrada: {row.get("category_slug")}'
                ))
                errors += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(
                    f'   WARNING Error en producto {row.get("product_slug")}: {str(e)}'
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
            except (Product.DoesNotExist, VariantType.DoesNotExist):
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

    def import_design_templates(self):
        """Importa templates de diseño desde CSV"""
        self.stdout.write('Importando templates de diseño...')
        filepath = os.path.join(self.data_dir, 'design_templates.csv')
        
        # El archivo es opcional
        if not os.path.exists(filepath):
            self.stdout.write(self.style.WARNING(
                '   SKIP Archivo design_templates.csv no encontrado\n'
            ))
            return 0
        
        df = self.safe_read_csv(filepath)
        
        created = 0
        updated = 0
        errors = 0
        
        for _, row in df.iterrows():
            try:
                # Saltar filas vacías
                if pd.isna(row.get('template_slug')) or not row.get('template_slug'):
                    continue
                
                if not self.dry_run:
                    # Obtener categoría
                    category = Category.objects.get(slug=row['category_slug'])
                    
                    # Obtener subcategoría (opcional)
                    subcategory = None
                    if pd.notna(row.get('subcategory_slug')) and row.get('subcategory_slug'):
                        try:
                            subcategory = Subcategory.objects.get(slug=row['subcategory_slug'])
                        except Subcategory.DoesNotExist:
                            pass  # Subcategoría opcional
                    
                    # Preparar defaults
                    defaults = {
                        'name': row['template_name'],
                        'category': category,
                        'subcategory': subcategory,
                        'description': row['description'] if pd.notna(row.get('description')) else '',
                        'thumbnail_url': row['thumbnail_url'] if pd.notna(row.get('thumbnail_url')) else '',
                        'preview_url': row['preview_url'] if pd.notna(row.get('preview_url')) else '',
                        'is_popular': str(row.get('is_popular', 'false')).lower() == 'true',
                        'display_order': int(row['display_order']) if pd.notna(row.get('display_order')) else 0,
                    }
                    
                    # Crear o actualizar
                    _, was_created = DesignTemplate.objects.update_or_create(
                        slug=row['template_slug'],
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
                    f'   WARNING Categoría no encontrada: {row.get("category_slug")}'
                ))
                errors += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'   ERROR en template {row.get("template_slug")}: {str(e)}'
                ))
                errors += 1
        
        self.stdout.write(f'   OK {created} creados, {updated} actualizados')
        if errors > 0:
            self.stdout.write(self.style.WARNING(f'   WARNING {errors} errores\n'))
        else:
            self.stdout.write('')
        
        return created + updated
