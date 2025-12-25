"""
Django management command to import catalog data from Excel files (xlsx)

ACTUALIZADO PARA SISTEMA DE OPCIONES GENÉRICAS
==============================================
Usa: ProductOption + ProductOptionValue + ProductVariant
En lugar de: ProductColor + ProductSize

Usage:
    python manage.py import_catalog
    python manage.py import_catalog --dry-run
    python manage.py import_catalog --force
    python manage.py import_catalog --only=templates
    python manage.py import_catalog --only=options
    python manage.py import_catalog --only=polos
"""
import os
import pandas as pd
# import csv # YA NO ES NECESARIO
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from shop.models import (
    Category,
    Subcategory,
    Product,
    ProductOption,
    ProductOptionValue,
    ProductVariant,
    ProductImage,
    DesignTemplate,
    DesignTemplate,
    PriceTier,
    Peru
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
    # Ayuda actualizada para Excel
    help = 'Importa el catálogo de productos desde archivos Excel (xlsx)'

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
        """Corrige caracteres mojibake en un texto. Menos necesario para Excel."""
        if not isinstance(text, str):
            return text
        
        result = text
        max_iterations = 3
        
        for _ in range(max_iterations):
            try:
                fixed = result.encode('latin-1').decode('utf-8')
                if fixed == result:
                    break
                result = fixed
            except (UnicodeDecodeError, UnicodeEncodeError):
                break
        
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

    # --- MÉTODO OBSOLETO PARA EXCEL (reemplazado) ---
    # def detect_delimiter(self, filepath):
    #    ...

    # NUEVO MÉTODO PARA LEER EXCEL
    def safe_read_excel(self, filename, sheet_name=0):
        """Lee un archivo Excel (xlsx) y aplica corrección de encoding si está activo."""
        filepath = os.path.join(self.data_dir, filename)
        
        # pd.read_excel maneja la codificación y los tipos de datos de Excel
        df = pd.read_excel(filepath, sheet_name=sheet_name)
        
        # Limpiar nombres de columnas
        df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
        
        if self.fix_encoding:
            df = self.fix_dataframe_encoding(df)
        
        return df

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar reimportación (elimina datos existentes)'
        )
        # Se mantiene --dry-run con guion medio
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular importación sin escribir en base de datos'
        )
        # Se mantiene --no-fix-encoding con guion medio
        parser.add_argument(
            '--no-fix-encoding',
            action='store_true',
            help='Desactivar corrección automática de caracteres'
        )
        parser.add_argument(
            '--only',
            type=str,
            choices=['categories', 'subcategories', 'products', 'options',
                     'prices', 'templates', 'images', 'polos', 'ubigeo'],
            help='Importa solo un tipo específico de datos'
        )

    def handle(self, *args, **options):
        # FIX: Acceder a los argumentos con guion bajo (_)
        self.force = options['force']
        self.dry_run = options['dry_run'] # <-- CORRECCIÓN: 'dry-run' -> 'dry_run'
        self.fix_encoding = not options.get('no_fix_encoding', False) # <-- CORRECCIÓN: 'no_fix-encoding' -> 'no_fix_encoding'
        self.only = options.get('only')
        self.data_dir = os.path.join(settings.BASE_DIR, 'static', 'data')
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('IMPORTACIÓN DEL CATÁLOGO DE PRODUCTOS (EXCEL)')) # Título actualizado
        self.stdout.write(self.style.SUCCESS('Sistema de Opciones Genéricas'))
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
            # if not self.confirm_action('¿Está seguro de que desea continuar?'):
            #     self.stdout.write(self.style.ERROR('Operación cancelada'))
            #     return
        
        try:
            with transaction.atomic():
                self.verify_excel_files() # <--- Llamada al método de verificación de Excel
                
                if self.force and not self.dry_run:
                    self.clear_existing_data()
                
                self.stdout.write('\nIniciando importación...\n')
                
                counts = {}
                
                if not self.only or self.only == 'categories':
                    counts['categories'] = self.import_categories()
                
                if not self.only or self.only == 'subcategories':
                    counts['subcategories'] = self.import_subcategories()
                
                # NUEVO: Importar opciones base (color, talla, etc.)
                if not self.only or self.only in ['options', 'polos']:
                    counts['product_options'] = self.import_product_options()
                    counts['option_values'] = self.import_option_values()
                
                if not self.only or self.only in ['products', 'polos']:
                    counts['products'] = self.import_products()
                
                # NUEVO: Importar imágenes con option_value
                if not self.only or self.only in ['images', 'polos']:
                    counts['product_images'] = self.import_product_images()
                    # Also import product images from static files (files mapping)
                    counts['product_images'] += self.import_product_images_from_static()
                
                if not self.only or self.only == 'prices':
                    counts['price_tiers'] = self.import_price_tiers()
                
                if not self.only or self.only == 'templates':
                    counts['design_templates'] = self.import_design_templates()
                    # Also import templates from static files
                    counts['design_templates'] += self.import_templates_from_static()

                # NUEVO: Actualizar códigos HEX de colores (lógica integrada de update_polo_hexes)
                if not self.only or self.only in ['product_options', 'polos', 'colors']:
                    self.update_hex_codes()

                # NUEVO: Importar Ubigeo
                if not self.only or self.only == 'ubigeo':
                    counts['ubigeo'] = self.import_ubigeo()

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
                self.stdout.write(self.style.SUCCESS('\n Dry-run completado'))


    def update_hex_codes(self):
        """Actualiza los códigos hexadecimales de los colores basándose en un mapa predefinido."""
        self.stdout.write('\nActualizando códigos HEX de colores...')
        
        COLOR_MAP = {
            'amarillo': '#FFEE58',
            'azul': '#1E88E5',
            'azul-claro': '#BBDEFB',
            'azul-marino': '#1A237E',
            'azul-real': '#0D47A1',
            'azul-cielo-nocturno': '#283593',
            'blanco': '#FFFFFF',
            'blanco-brillante': '#F5F5F5',
            'negro': '#212121',
            'negro-profundo': '#000000',
            'rojo': '#E53935',
            'gris': '#9E9E9E',
            'gris-terreno': '#616161',
            'arena': '#C2B280',
            'asfalto': '#424242',
            'azalea': '#F06292',
            'carbon': '#333333',
            'cardenal': '#C62828',
            'ceniza': '#E0E0E0',
            'coral': '#FF7043',
            'coral-seda': '#FF8A65',
            'deep-forest': '#1B5E20',
            'dorado': '#FBC02D',
            'fuchsia': '#D81B60',
            'fuchsia-frost': '#C2185B',
            'granate': '#880E4F',
            'graphite': '#455A64',
            'heather-peach': '#FFCCBC',
            'heather-sangria': '#AD1457',
            'indigo': '#3F51B5',
            'kelly': '#43A047',
            'light-steel': '#B0BEC5',
            'lila': '#CE93D8',
            'margarita': '#FFF176',
            'marron': '#5D4037',
            'morado': '#7B1FA2',
            'morado-equipo': '#4A148C',
            'naranja': '#FB8C00',
            'natural': '#F5F5DC',
            'rosa': '#F06292',
            'rosa-claro': '#F8BBD0',
            'rosa-fucsia': '#E91E63',
            'sangria': '#92113D',
            'shiraz': '#880E4F',
            'sky': '#81D4FA',
            'smoked-paprika': '#B71C1C',
            'turquoise': '#00CED1',
            'turquoise-frost': '#4DD0E1',
            'verde': '#4CAF50',
            'verde-bosque': '#2E7D32',
            'verde-irlandes': '#388E3C',
            'verde-kelly': '#2E7D32',
            'verde-militar': '#558B2F',
            'verde-oscuro': '#1B5E20',
            'vintage-turquoise': '#40E0D0',
            'violeta': '#9C27B0',
            'zafiro': '#0277BD'
        }
        
        updated_count = 0
        qs = ProductOptionValue.objects.filter(option__key='color')
        
        for val in qs:
            slug = val.value.lower().strip()
            
            # Direct match
            new_hex = COLOR_MAP.get(slug)
            
            # Fuzzy match attempt if not found
            if not new_hex:
                for k, v in COLOR_MAP.items():
                    if k in slug:
                        new_hex = v
                        break
            
            if new_hex and val.hex_code != new_hex:
                val.hex_code = new_hex
                val.save()
                updated_count += 1
                # self.stdout.write(f"   Updated {slug} -> {new_hex}")
        
        self.stdout.write(f'   OK {updated_count} colores actualizados con HEX')
                

    def confirm_action(self, message):
        """Solicita confirmación del usuario"""
        response = input(f'{message} (si/no): ').lower()
        return response in ['si', 'yes', 'y', 's']

    # VERIFICACIÓN DE ARCHIVOS ACTUALIZADA PARA EXCEL
    def verify_excel_files(self):
        """Verifica que existan los archivos Excel (.xlsx) necesarios"""
        required_files = [
            'categories_complete.xlsx',
            'subcategories_complete.xlsx',
            'products_complete.xlsx',
            'price_tiers_complete.xlsx',
        ]
        
        optional_files = [
            'design_templates.xlsx',
            'polos_colors.xlsx',
            'polos_images.xlsx',
            'product_options.xlsx',
            'option_values.xlsx',
        ]
        
        self.stdout.write('Verificando archivos Excel...')
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
                f'Archivos Excel faltantes: {", ".join(missing_files)}'
            )
        
        self.stdout.write(self.style.SUCCESS('    Verificación completada\n'))

    def clear_existing_data(self):
        """Elimina datos existentes"""
        self.stdout.write('Eliminando datos existentes...')
        
        counts = {
            'ProductImage': ProductImage.objects.all().delete()[0],
            'DesignTemplate': DesignTemplate.objects.all().delete()[0],
            'PriceTier': PriceTier.objects.all().delete()[0],
            'ProductVariant': ProductVariant.objects.all().delete()[0],
            'Product': Product.objects.all().delete()[0],
            'ProductOptionValue': ProductOptionValue.objects.all().delete()[0],
            'ProductOption': ProductOption.objects.all().delete()[0],
            'Subcategory': Subcategory.objects.all().delete()[0],
            'Category': Category.objects.all().delete()[0],
        }
        
        total = sum(counts.values())
        self.stdout.write(f'   OK {total} registros eliminados')
        for model, count in counts.items():
            if count > 0:
                self.stdout.write(f'     - {model}: {count}')
        self.stdout.write('')

    # =========================================================================
    # NUEVO: IMPORTAR OPCIONES BASE (color, size, material, etc.)
    # =========================================================================
    def import_product_options(self):
        """
        Importa tipos de opciones desde Excel o crea las opciones base.
        ProductOption: color, size, material, finish, cassette, etc.
        """
        self.stdout.write('Importando tipos de opciones...')
        
        # Primero, crear opciones base que siempre existen
        base_options = [
            {'key': 'color', 'name': 'Color', 'display_order': 1, 'is_required': True, 'selection_type': 'single'},
            {'key': 'size', 'name': 'Talla', 'display_order': 2, 'is_required': True, 'selection_type': 'single'},
            # Opciones para banners (futuro)
            {'key': 'material', 'name': 'Material', 'display_order': 3, 'is_required': True, 'selection_type': 'single'},
            {'key': 'finish', 'name': 'Acabado', 'display_order': 4, 'is_required': False, 'selection_type': 'single'},
            {'key': 'cassette', 'name': 'Sistema de Sujeción', 'display_order': 5, 'is_required': False, 'selection_type': 'single'},
        ]
        
        created = 0
        updated = 0
        
        for opt_data in base_options:
            if not self.dry_run:
                _, was_created = ProductOption.objects.update_or_create(
                    key=opt_data['key'],
                    defaults={
                        'name': opt_data['name'],
                        'display_order': opt_data['display_order'],
                        'is_required': opt_data['is_required'],
                        'selection_type': opt_data['selection_type'],
                    }
                )
                if was_created:
                    created += 1
                else:
                    updated += 1
            else:
                created += 1
        
        # Luego, importar desde Excel si existe
        filename = 'product_options.xlsx' # Extensión actualizada
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            # Llamada al nuevo método safe_read_excel
            df = self.safe_read_excel(filename) 
            
            for _, row in df.iterrows():
                try:
                    key = str(row.get('key', '')).strip()
                    if not key:
                        continue
                    
                    if not self.dry_run:
                        _, was_created = ProductOption.objects.update_or_create(
                            key=key,
                            defaults={
                                'name': row.get('name', key.title()),
                                # Conversión explícita a int
                                'display_order': int(row.get('display_order', 0)),
                                'is_required': str(row.get('is_required', 'True')).lower() == 'true',
                                'selection_type': row.get('selection_type', 'single'),
                            }
                        )
                        if was_created:
                            created += 1
                        else:
                            updated += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'   WARNING Error: {e}'))
        
        self.stdout.write(f'   OK {created} creados, {updated} actualizados\n')
        return created + updated

    # =========================================================================
    # NUEVO: IMPORTAR VALORES DE OPCIONES (colores, tallas, materiales)
    # =========================================================================
    def import_option_values(self):
        """
        Importa valores de opciones desde Excel.
        Incluye colores desde polos_colors.xlsx y tallas estándar.
        """
        self.stdout.write('Importando valores de opciones...')
        
        created = 0
        updated = 0
        
        # 1. Importar tallas estándar
        try:
            size_option = ProductOption.objects.get(key='size')
            
            for name, display_name, order in STANDARD_SIZES:
                if not self.dry_run:
                    _, was_created = ProductOptionValue.objects.update_or_create(
                        option=size_option,
                        value=name,
                        defaults={
                            'display_name': display_name,
                            'display_order': order,
                            'is_active': True,
                        }
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                else:
                    created += 1
                    
            self.stdout.write(f'   • Tallas estándar: {len(STANDARD_SIZES)}')
        except ProductOption.DoesNotExist:
            self.stdout.write(self.style.WARNING('   WARNING: Opción "size" no encontrada'))
        
        # 2. Importar colores desde polos_colors.xlsx
        filename = 'polos_colors.xlsx' # Extensión actualizada
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            try:
                color_option = ProductOption.objects.get(key='color')
                # Llamada al nuevo método safe_read_excel
                df = self.safe_read_excel(filename)
                color_count = 0
                
                for _, row in df.iterrows():
                    try:
                        slug = str(row.get('slug', '')).strip()
                        if not slug:
                            continue
                        
                        hex_code = str(row.get('hex_code', '')).strip()
                        if not hex_code.startswith('#'):
                            hex_code = f'#{hex_code}'
                        
                        if not self.dry_run:
                            _, was_created = ProductOptionValue.objects.update_or_create(
                                option=color_option,
                                value=slug,
                                defaults={
                                    'display_name': row.get('name', slug.replace('-', ' ').title()),
                                    'hex_code': hex_code,
                                    # Conversión explícita a int
                                    'display_order': int(row.get('display_order', 0)),
                                    'is_active': str(row.get('is_active', 'True')).lower() == 'true',
                                }
                            )
                            if was_created:
                                created += 1
                                color_count += 1
                            else:
                                updated += 1
                        else:
                            created += 1
                            color_count += 1
                            
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(
                            f'   WARNING Error en color {row.get("slug")}: {e}'
                        ))
                
                self.stdout.write(f'   • Colores desde Excel: {color_count}')
                
            except ProductOption.DoesNotExist:
                self.stdout.write(self.style.WARNING('   WARNING: Opción "color" no encontrada'))
        else:
            self.stdout.write(self.style.WARNING(f'   SKIP: {filename} no encontrado'))
        
        # 3. Importar desde option_values.xlsx si existe (para materiales, acabados, etc.)
        filename = 'option_values.xlsx' # Extensión actualizada
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            # Llamada al nuevo método safe_read_excel
            df = self.safe_read_excel(filename)
            extra_count = 0
            
            for _, row in df.iterrows():
                try:
                    option_key = str(row.get('option_key', '')).strip()
                    value = str(row.get('value', '')).strip()
                    
                    if not option_key or not value:
                        continue
                    
                    option = ProductOption.objects.get(key=option_key)
                    
                    if not self.dry_run:
                        defaults = {
                            'display_name': row.get('display_name', value.replace('-', ' ').title()),
                            # Conversión explícita a int
                            'display_order': int(row.get('display_order', 0)),
                            'is_active': str(row.get('is_active', 'True')).lower() == 'true',
                        }
                        
                        # Campos opcionales
                        if pd.notna(row.get('hex_code')):
                            defaults['hex_code'] = str(row['hex_code'])
                        if pd.notna(row.get('additional_price')):
                            # Conversión a Decimal a través de str para evitar errores de precisión
                            defaults['additional_price'] = Decimal(str(row['additional_price']))
                        
                        _, was_created = ProductOptionValue.objects.update_or_create(
                            option=option,
                            value=value,
                            defaults=defaults
                        )
                        if was_created:
                            created += 1
                            extra_count += 1
                        else:
                            updated += 1
                    else:
                        created += 1
                        extra_count += 1
                        
                except ProductOption.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f'   WARNING: Opción "{option_key}" no encontrada'
                    ))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'   WARNING Error: {e}'))
            
            if extra_count > 0:
                self.stdout.write(f'   • Valores adicionales: {extra_count}')
        
        self.stdout.write(f'   OK {created} creados, {updated} actualizados\n')
        return created + updated

    def import_categories(self):
        """Importa categorías desde Excel"""
        self.stdout.write('Importando categorías...')
        filename = 'categories_complete.xlsx' # Extensión actualizada
        # Llamada al nuevo método safe_read_excel
        df = self.safe_read_excel(filename)
        
        created = 0
        updated = 0
        
        for _, row in df.iterrows():
            defaults = {
                'name': row['category_name'],
                # Maneja mejor los nulos de Excel para strings/int
                'description': str(row['description']) if pd.notna(row['description']) else '',
                'image_url': str(row['image_url']) if pd.notna(row['image_url']) else None,
                # Conversión explícita a int
                'display_order': int(row['display_order']),
                'status': str(row['status']) if 'status' in row and pd.notna(row['status']) else 'active',
            }
            
            if 'category_type' in row and pd.notna(row['category_type']):
                defaults['category_type'] = str(row['category_type'])
            
            if not self.dry_run:
                _, was_created = Category.objects.update_or_create(
                    # Asegura que el slug es string
                    slug=str(row['category_slug']).strip(),
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
        """Importa subcategorías desde Excel"""
        self.stdout.write('Importando subcategorías...')
        filename = 'subcategories_complete.xlsx' # Extensión actualizada
        # Llamada al nuevo método safe_read_excel
        df = self.safe_read_excel(filename)
        
        created = 0
        updated = 0
        errors = 0
        
        for _, row in df.iterrows():
            try:
                category_slug = str(row['category_slug']).strip()
                subcategory_slug = str(row['subcategory_slug']).strip()
                
                if not self.dry_run:
                    category = Category.objects.get(slug=category_slug)
                    defaults = {
                        'name': row['subcategory_name'],
                        'category': category,
                        'description': str(row['description']) if pd.notna(row['description']) else '',
                        'image_url': str(row['image_url']) if pd.notna(row['image_url']) else None,
                        # Conversión explícita a int
                        'display_order': int(row['display_order']),
                    }
                    
                    if 'display_style' in row and pd.notna(row['display_style']):
                        defaults['display_style'] = str(row['display_style'])
                    
                    _, was_created = Subcategory.objects.update_or_create(
                        slug=subcategory_slug,
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
                    f'   WARNING Categoría no encontrada: {category_slug}'
                ))
                errors += 1
            except Exception as e:
                 self.stdout.write(self.style.WARNING(
                    f'   WARNING Error en subcategoría {subcategory_slug}: {str(e)}'
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
        
        # Asegura que es string antes de split
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
        """
        Importa productos desde Excel.
        ACTUALIZADO: Crea ProductVariant para asignar opciones.
        """
        print("DEBUG: Executing import_products STARTS")
        self.stdout.write('Importando productos...')
        filename = 'products_complete.xlsx' # Extensión actualizada
        # Llamada al nuevo método safe_read_excel
        df = self.safe_read_excel(filename)
        
        created = 0
        updated = 0
        errors = 0
        
        # Obtener opciones de color y talla
        color_option = None
        size_option = None
        try:
            color_option = ProductOption.objects.get(key='color')
            size_option = ProductOption.objects.get(key='size')
        except ProductOption.DoesNotExist:
            pass
        
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
                        # Asegura que SKU es string
                        'sku': str(row['sku']), 
                        'description': str(row['description']) if pd.notna(row['description']) else '',
                        'base_image_url': str(row['base_image_url']) if pd.notna(row['base_image_url']) else '',
                        'status': str(row.get('status')) if pd.notna(row.get('status')) else 'active',
                    }
                    
                    # Guardar marca en material
                    if 'marca' in row and pd.notna(row['marca']):
                        defaults['material'] = str(row['marca'])
                    
                    # Guardar características en features
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
                    
                    # NUEVO: Asignar colores via ProductVariant
                    colors_hex_str = row.get('available_colors')
                    if pd.isna(colors_hex_str):
                        colors_hex_str = row.get('colores_hex')
                    
                    # Log DEBUG simplificado
                    # self.stdout.write(f"DEBUG: {product_slug} | Colors: {colors_hex_str}")

                    # Log DEBUG simplificado
                    # self.stdout.write(f"DEBUG: {product_slug} | Colors: {colors_hex_str}")

                    if pd.notna(colors_hex_str) and colors_hex_str and color_option:
                        if 'polo' in product_slug:
                             self.stdout.write(f'✅ FOUND POLO COLOR DATA: {product_slug} -> {colors_hex_str}')
                        colors_data = self.parse_colors_hex(str(colors_hex_str)) # Asegura string
                        
                        # Crear/obtener ProductVariant para color
                        variant, _ = ProductVariant.objects.get_or_create(
                            product=product,
                            option=color_option,
                            defaults={'display_order': 1}
                        )
                        
                        # Limpiar valores previos si se está forzando actualización o para asegurar exactitud
                        if self.force or not self.dry_run:
                             # No limpiamos todo, pero recolectaremos los valores activos para este producto
                             active_values = []
                        
                        # Añadir valores de color disponibles
                        for color_slug, hex_code in colors_data.items():
                            # Asegurar que el color existe o actualizar hex
                            color_val, created_val = ProductOptionValue.objects.get_or_create(
                                option=color_option,
                                value=color_slug,
                                defaults={
                                    'display_name': color_slug.replace('-', ' ').title(),
                                    'hex_code': hex_code,
                                    'is_active': True,
                                    'display_order': 0 # Default, podría mejorarse
                                }
                            )
                            
                            # Si ya existía, actualizar hex si es diferente (y viene del excel)
                            if not created_val and hex_code and color_val.hex_code != hex_code:
                                color_val.hex_code = hex_code
                                color_val.save()
                            
                            active_values.append(color_val)
                        
                        # Asignar ESTRICTAMENTE los colores del excel al variante
                        if active_values:
                            variant.available_values.set(active_values)
                        else:
                            variant.available_values.clear()
                    
                    # NUEVO: Asignar tallas para ropa
                    # Nota: Hay que asegurar que 'category_slug' sea 'ropa-bolsos'
                    if category_slug == 'ropa-bolsos' and size_option:
                        # Crear/obtener ProductVariant para talla
                        variant, _ = ProductVariant.objects.get_or_create(
                            product=product,
                            option=size_option,
                            defaults={'display_order': 2}
                        )
                        
                        # Añadir tallas estándar
                        sizes = ProductOptionValue.objects.filter(
                            option=size_option,
                            value__in=['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                            is_active=True
                        )
                        variant.available_values.set(sizes)
                    
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

    def import_product_images(self):
        """
        Importa imágenes de productos desde Excel.
        ACTUALIZADO: Usa option_value en lugar de color.
        """
        self.stdout.write('Importando imágenes de productos...')
        filename = 'polo_imagenes_colores.xlsx' # Extensión actualizada y nombre corregido
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            # Fallback a nombre antiguo si no existe el nuevo
            alt_filename = 'polos_images.xlsx'
            alt_filepath = os.path.join(self.data_dir, alt_filename)
            if os.path.exists(alt_filepath):
                filename = alt_filename
                filepath = alt_filepath
            else:
                self.stdout.write(self.style.WARNING(
                    f'   SKIP Archivo {filename} no encontrado\n'
                ))
                return 0
        
        # Llamada al nuevo método safe_read_excel
        df = self.safe_read_excel(filename)
        
        created = 0
        skipped = 0
        errors = 0
        
        # Obtener opción de color
        color_option = None
        try:
            color_option = ProductOption.objects.get(key='color')
        except ProductOption.DoesNotExist:
            pass
        
        processed = 0
        for _, row in df.iterrows():
            processed += 1
            if processed <= 5:
                print(f"DEBUG LOOP: {row.get('product_slug')}")
            try:
                product_slug = str(row.get('product_slug', '')).strip()
                image_url = str(row.get('image_url', '')).strip()
                
                if not product_slug or not image_url:
                    skipped += 1
                    continue
                
                if not self.dry_run:
                    try:
                        # Buscamos el producto exacto o todos los que empiecen por este slug
                        # (para casos donde cada color es un producto separado con slug compuesto)
                        from django.db.models import Q
                        products_to_process = Product.objects.filter(
                            Q(slug=product_slug) | Q(slug__startswith=product_slug + "-")
                        )
                        if not products_to_process.exists():
                            skipped += 1
                            continue
                    except Exception:
                        skipped += 1
                        continue
                    
                    for product in products_to_process:
                    
                        # NUEVO: Buscar option_value en lugar de color
                        option_value = None
                        color_slug = str(row.get('color_slug', '')).strip()
                        display_order = int(row.get('display_order', 0))
                        
                        if color_slug and color_option:
                            # Auto-create color if missing (from image filename source)
                            # Try to find standard color first to get 'hex' if possible? 
                            # For now, just create with default if missing.
                            option_value, created_val = ProductOptionValue.objects.get_or_create(
                                option=color_option,
                                value=color_slug,
                                defaults={
                                    'display_name': color_slug.replace('-', ' ').title(),
                                    'hex_code': '#CCCCCC', # Default placeholder
                                    'is_active': True,
                                    'display_order': display_order
                                }
                            )
                            
                            # CRITICAL: Ensure this color is available for the product variant!
                            # This enables the swatch to appear even if products.xlsx was missing it.
                            variant, _ = ProductVariant.objects.get_or_create(
                                product=product, 
                                option=color_option,
                                defaults={'display_order': 1}
                            )
                            variant.available_values.add(option_value)
                        
                        is_primary = str(row.get('is_primary', 'False')).lower() == 'true'
                        
                        _, was_created = ProductImage.objects.update_or_create(
                            product=product,
                            image_url=image_url, # Key by URL to avoid dupes logic (or product+option?)
                            # Using product + option_value as unique might be better, but multiple images per color allowed
                            # update_or_create defaults to lookup by first args. 
                            # We want to create or update specific image entry. 
                            # Let's map by image_url as unique ID for import? 
                            # Actually previous code used product, option_value, image_url as lookup?
                            # No, previous code used (product=product, option_value=..., image_url=...) which means GET by all 3.
                            # That's strict. Let's stick to update_or_create on image_url + product
                            defaults={
                                'option_value': option_value,
                                'is_primary': is_primary,
                                'display_order': display_order,
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

    def import_price_tiers(self):
        """Importa niveles de precio desde Excel"""
        self.stdout.write('Importando niveles de precios...')
        filename = 'price_tiers_complete.xlsx' # Extensión actualizada
        # Llamada al nuevo método safe_read_excel
        df = self.safe_read_excel(filename)
        
        created = 0
        updated = 0
        errors = 0
        
        for _, row in df.iterrows():
            try:
                product_slug = str(row['product_slug']).strip()
                
                if not self.dry_run:
                    product = Product.objects.get(slug=product_slug)
                    defaults = {
                        # Conversión explícita a int
                        'max_quantity': int(row['max_quan']),
                        # Conversión a Decimal a través de string
                        'unit_price': Decimal(str(row['unit_price'])),
                        # Conversión explícita a int
                        'discount_percentage': int(row['discount_percent'])
                    }
                    _, was_created = PriceTier.objects.update_or_create(
                        product=product,
                        # Conversión explícita a int
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
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'   WARNING Error en precio para {product_slug}: {str(e)}'))
                errors += 1
        
        self.stdout.write(f'   OK {created} creados, {updated} actualizados')
        if errors > 0:
            self.stdout.write(self.style.WARNING(f'   WARNING {errors} errores\n'))
        else:
            self.stdout.write('')
        return created + updated

    def import_design_templates(self):
        """Importa templates de diseño desde Excel - VERSIÓN FINAL SIN ERRORES"""
        self.stdout.write('Importando templates de diseño...')
        filename = 'design_templates.xlsx' # Extensión actualizada
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            self.stdout.write(self.style.WARNING(f'    SKIP Archivo {filename} no encontrado\n'))
            return 0
        
        # Llamada al nuevo método safe_read_excel
        df = self.safe_read_excel(filename)
        self.stdout.write(f'    Leyendo {len(df)} filas...')

        created = 0
        updated = 0
        errors = 0

        for index, row in df.iterrows():
            template_slug = row.get('template_slug')
            if not template_slug or pd.isna(template_slug):
                errors += 1
                continue
            template_slug = str(template_slug).strip()

            try:
                if self.dry_run:
                    created += 1
                    continue

                # Limpiar URLs
                def clean_url(url):
                    if pd.isna(url) or not isinstance(url, str):
                        return ''
                    return str(url).strip() # Asegura string antes de strip

                thumbnail_url = clean_url(row.get('thumbnail_url'))
                preview_url = clean_url(row.get('preview_url'))

                category_slug = str(row.get('category_slug', '')).strip()
                if not category_slug:
                    errors += 1
                    continue

                category = Category.objects.get(slug=category_slug)

                subcategory = None
                subcategory_slug = row.get('subcategory_slug')
                if pd.notna(subcategory_slug):
                    subcategory_slug = str(subcategory_slug).strip()
                    if subcategory_slug:
                        try:
                            subcategory = Subcategory.objects.get(category=category, slug=subcategory_slug)
                        except Subcategory.DoesNotExist:
                            pass

                # Orden de visualización
                display_order = 0
                if pd.notna(row.get('display_order')):
                    try:
                        # La conversión a float antes de int es robusta para Excel
                        display_order = int(float(row['display_order']))
                    except:
                        display_order = index + 1

                # Banderas
                is_popular = str(row.get('is_popular', 'false')).lower() in ('true', '1', 'yes', 'sí')
                is_new = str(row.get('is_new', 'false')).lower() in ('true', '1', 'yes', 'sí')

                defaults = {
                    'name': str(row.get('template_name', template_slug)),
                    'category': category,
                    'subcategory': subcategory,
                    'description': str(row.get('description', '')) if pd.notna(row.get('description')) else '',
                    'thumbnail_url': thumbnail_url,
                    'preview_url': preview_url or thumbnail_url,
                    'is_popular': is_popular,
                    'is_new': is_new,
                    'display_order': display_order,
                }

                obj, was_created = DesignTemplate.objects.update_or_create(
                    slug=template_slug,
                    defaults=defaults
                )

                if was_created:
                    created += 1
                else:
                    updated += 1

            except Category.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'    Categoría no encontrada: {category_slug}'))
                errors += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'    ERROR {template_slug}: {e}'))
                errors += 1

        self.stdout.write(self.style.SUCCESS(f'    {created} creados | {updated} actualizados | {errors} errores'))
        self.stdout.write('')
        return created + updated

    # =========================================================================
    # NUEVO: IMPORTAR TEMPLATES DESDE ARCHIVOS ESTÁTICOS
    # =========================================================================
    def import_templates_from_static(self):
        """Importa templates de diseño desde carpetas de archivos estáticos."""
        self.stdout.write('Importando templates desde archivos estáticos...')
        
        base_path = os.path.join(settings.BASE_DIR, 'static', 'media', 'template_images')
        
        if not os.path.exists(base_path):
            self.stdout.write(self.style.WARNING(f'    SKIP Directorio no encontrado: {base_path}\n'))
            return 0
        
        # Mapeo de carpetas a categorías
        category_mappings = {
            'tarjetas_presentacion': 'tarjetas-presentacion',
            'invitaciones_papeleria': 'invitaciones-papeleria',
            'calendarios_regalos': 'calendarios-regalos',
            'letreros_banners': 'letreros-banners',
            'productos_promocionales': 'productos-promocionales',
            'postales_publicidad': 'postales-publicidad',
        }
        
        total_created = 0
        total_updated = 0
        
        for folder_name, category_slug in category_mappings.items():
            folder_path = os.path.join(base_path, folder_name)
            if not os.path.isdir(folder_path):
                continue
            
            try:
                category = Category.objects.get(slug=category_slug)
            except Category.DoesNotExist:
                # Auto-create category if it doesn't exist (useful for static-only categories like letreros)
                name = category_slug.replace('-', ' ').title()
                category = Category.objects.create(
                    slug=category_slug,
                    name=name,
                    status='active'
                )
                self.stdout.write(self.style.SUCCESS(f'    Categoría creada: {name} ({category_slug})'))
            
            self.stdout.write(f'\n  Procesando: {folder_name} -> {category.name}')
            
            # SPECIAL CASE: CALENDARIOS (Products as folders)
            if category_slug == 'calendarios-regalos':
                 # Passing the BASE folder path (e.g. static/media/template_images/calendarios_regalos)
                 created, updated = self._import_calendarios_nested(folder_path, category)
                 total_created += created
                 total_updated += updated
                 continue

            # Check if this folder has subfolders (like bodas has product subfolders)
            items = os.listdir(folder_path)
            subdirs = [d for d in items if os.path.isdir(os.path.join(folder_path, d))]
            
            if subdirs:
                # Has subfolders - each is a product/subcategory
                
                # SPECIAL CASE: LETREROS_BANNERS (3-level nested structure)
                if category_slug == 'letreros-banners':
                    created, updated = self._import_letreros_banners_nested(folder_path, category)
                    total_created += created
                    total_updated += updated
                    continue
                
                for subdir in subdirs:
                    subdir_path = os.path.join(folder_path, subdir)
                    subcategory_slug = subdir.replace('_', '-')
                    
                    try:
                        subcategory = Subcategory.objects.get(slug=subcategory_slug, category=category)
                    except Subcategory.DoesNotExist:
                        subcategory = None
                    
                    # SPECIAL CASE: BODAS (Nested products)
                    if subcategory_slug == 'bodas':
                         created, updated = self._import_bodas_nested(subdir_path, category, subcategory)
                         total_created += created
                         total_updated += updated
                         continue

                    # Removed previous calendarios check here because we handle it at category level now
                    
                    created, updated = self._import_templates_from_folder(
                        subdir_path, category, subcategory, f'{folder_name}/{subdir}'
                    )
                    total_created += created
                    total_updated += updated
            else:
                # No subfolders - images directly in category folder
                created, updated = self._import_templates_from_folder(
                    folder_path, category, None, folder_name
                )
                total_created += created
                total_updated += updated
        
        self.stdout.write(self.style.SUCCESS(f'\n    Archivos estáticos: {total_created} creados | {total_updated} actualizados'))
        self.stdout.write('')
        return total_created + total_updated

    def _import_templates_from_folder(self, folder_path, category, subcategory, prefix):
        """Importa templates desde una carpeta específica."""
        image_extensions = ('.jpg', '.jpeg', '.png', '.webp')
        
        try:
            files = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
        except OSError:
            return 0, 0
        
        if not files:
            return 0, 0
        
        self.stdout.write(f'    • {prefix}: {len(files)} imágenes')
        
        created = 0
        updated = 0
        
        for i, image_file in enumerate(files):
            # Create slug from filename
            file_slug = os.path.splitext(image_file)[0].lower()
            template_slug = f'{category.slug}-{file_slug}'[:100]
            
            # Image URL calculation
            relative_path = folder_path.replace(str(settings.BASE_DIR), '').replace('\\', '/')
            if relative_path.startswith('/'):
                relative_path = relative_path[1:]
            
            # Remove 'static/' from start if present
            if relative_path.startswith('static/'):
                relative_path = relative_path[7:]
            
            image_url = f'{relative_path}/{image_file}'
            
            # Template name
            template_name = file_slug.replace('-', ' ').replace('_', ' ').title()[:200]
            
            if not self.dry_run:
                try:
                    template, was_created = DesignTemplate.objects.update_or_create(
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
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                except Exception as e:
                    pass  # Silently skip errors
            else:
                created += 1
        
        return created, updated

    def _import_letreros_banners_nested(self, base_path, category):
        """
        Importa templates de letreros_banners que tienen estructura anidada de 3 niveles.
        Estructura: letreros_banners/banderas/banderines/imagen.jpg
        """
        total_created = 0
        total_updated = 0
        
        if not os.path.exists(base_path):
            return 0, 0
        
        try:
            subdirs = os.listdir(base_path)
        except OSError:
            return 0, 0
        
        # Iterate through first-level subdirectories (banderas, banners, letreros, etc.)
        for subdir in subdirs:
            subdir_path = os.path.join(base_path, subdir)
            
            if not os.path.isdir(subdir_path):
                continue
            
            subcategory_slug = subdir.replace('_', '-')
            
            # Try to get subcategory
            try:
                subcategory = Subcategory.objects.get(slug=subcategory_slug, category=category)
            except Subcategory.DoesNotExist:
                subcategory = None
            
            # Check if this subdirectory has further nesting (e.g., banderas/banderines)
            try:
                subdir_items = os.listdir(subdir_path)
            except OSError:
                continue
            
            nested_dirs = [d for d in subdir_items if os.path.isdir(os.path.join(subdir_path, d))]
            image_extensions = ('.jpg', '.jpeg', '.png', '.webp')
            direct_images = [f for f in subdir_items if f.lower().endswith(image_extensions)]
            
            if nested_dirs:
                # Has 3rd level nesting (e.g., banderas/banderines, banderas/banderas_pluma)
                for nested_dir in nested_dirs:
                    nested_path = os.path.join(subdir_path, nested_dir)
                    
                    # Get images from this nested directory
                    try:
                        nested_images = [f for f in os.listdir(nested_path) if f.lower().endswith(image_extensions)]
                    except OSError:
                        continue
                    
                    if not nested_images:
                        continue
                    
                    self.stdout.write(f'    • letreros_banners/{subdir}/{nested_dir}: {len(nested_images)} imágenes')
                    
                    # Import templates from this nested folder
                    for i, image_file in enumerate(nested_images):
                        file_slug = os.path.splitext(image_file)[0].lower()
                        template_slug = f'letreros-{nested_dir.replace("_", "-")}-{file_slug}'[:100]
                        
                        # Image URL
                        image_url = f'media/template_images/letreros_banners/{subdir}/{nested_dir}/{image_file}'
                        
                        # Template name
                        template_name = file_slug.replace('-', ' ').replace('_', ' ').title()[:200]
                        
                        if not self.dry_run:
                            try:
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
                            except Exception as e:
                                pass  # Silently skip errors
                        else:
                            total_created += 1
            
            if direct_images:
                # Has images directly in this subdirectory (2-level structure)
                self.stdout.write(f'    • letreros_banners/{subdir}: {len(direct_images)} imágenes')
                
                for i, image_file in enumerate(direct_images):
                    file_slug = os.path.splitext(image_file)[0].lower()
                    template_slug = f'letreros-{subcategory_slug}-{file_slug}'[:100]
                    
                    # Image URL
                    image_url = f'media/template_images/letreros_banners/{subdir}/{image_file}'
                    
                    # Template name
                    template_name = file_slug.replace('-', ' ').replace('_', ' ').title()[:200]
                    
                    if not self.dry_run:
                        try:
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
                        except Exception as e:
                            pass  # Silently skip errors
                    else:
                        total_created += 1
        
        return total_created, total_updated

    def _import_bodas_nested(self, base_path, category, subcategory):
        """
        Importa templates de bodas que tienen un nivel extra de anidamiento (por producto).
        Estructura: bodas/guarda_la_fecha/imagen.jpg
        """
        folder_to_product = {
            'guarda_la_fecha': 'guarda-la-fecha',
            'servilletas': 'servilletas',
            'carteles_carton_espuma': 'carteles-carton-espuma',
            'invitaciones_despedida_soltera': 'invitaciones-despedida-de-soltera',
            'libro_firmas_invitados': 'libro-de-firmas',
            'programas_boda': 'programas-boda',
            'tarjetas_de_gracias': 'tarjetas-de-gracias',
            'tarjetas_informativas': 'tarjetas-informativas',
            'tarjetas_itinerario': 'tarjetas-itinerario',
            'tarjetas_itineario': 'tarjetas-itinerario',
            'tarjetas_menu': 'tarjetas-menu',
            'tarjetas_rsvp': 'tarjetas-rsvp',
        }
        
        total_created = 0
        total_updated = 0
        
        # Iterate through each product folder inside bodas
        if not os.path.exists(base_path):
            return 0, 0
            
        try:
            items = os.listdir(base_path)
        except OSError:
            return 0, 0

        for folder_name in items:
            folder_path = os.path.join(base_path, folder_name)
            
            if not os.path.isdir(folder_path):
                continue
            
            product_slug = folder_to_product.get(folder_name, folder_name.replace('_', '-'))
            
            # Get all image files
            image_extensions = ('.jpg', '.jpeg', '.png', '.webp')
            try:
                images = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
            except OSError:
                continue
            
            if not images:
                continue
                
            self.stdout.write(f'     > Bodas: {product_slug} ({len(images)} imgs)')

            for i, image_file in enumerate(images):
                # Create slug from filename
                file_slug = os.path.splitext(image_file)[0].lower()
                template_slug = f'bodas-{product_slug}-{file_slug}'[:100]
                
                # Image URL
                image_url = f'media/template_images/invitaciones_papeleria/bodas/{folder_name}/{image_file}'
                
                # Create template name
                template_name = file_slug.replace('-', ' ').replace('_', ' ').title()[:200]
                
                if not self.dry_run:
                    try:
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
                    except Exception as e:
                         # Silently skip
                         pass
                else:
                    total_created += 1
                    
        return total_created, total_updated
                    
    def import_product_images_from_static(self):
        """
        Importa imágenes de productos desde static/media/product_images
        Convención:
        - slug.jpg -> Imagen Principal (Product.base_image_url)
        - slug-detalle.jpg -> Imagen de Galería (ProductImage)
        """
        self.stdout.write('Importando imágenes de productos desde archivos estáticos...')
        
        base_path = os.path.join(settings.BASE_DIR, 'static', 'media', 'product_images')
        
        if not os.path.exists(base_path):
            self.stdout.write(self.style.WARNING(f'    SKIP Directorio no encontrado: {base_path}\n'))
            return 0
            
        total_updated_main = 0
        total_created_detail = 0
        
        # Walk through all directories
        for root, dirs, files in os.walk(base_path):
            if not files:
                continue
                
            relative_path = os.path.relpath(root, base_path)
            self.stdout.write(f'  Escaneando: {relative_path}')
            
            image_extensions = ('.jpg', '.jpeg', '.png', '.webp')
            images = [f for f in files if f.lower().endswith(image_extensions)]
            
            for image_file in images:
                file_slug = os.path.splitext(image_file)[0].lower()
                
                # Determine type and product slug
                is_detail = False
                product_slug = file_slug
                
                if file_slug.endswith('-detalle'):
                    is_detail = True
                    product_slug = file_slug[:-8] # Remove '-detalle'
                
                # Try to find product
                try:
                    product = Product.objects.get(slug=product_slug)
                except Product.DoesNotExist:
                    # Silent skip or verbose debug?
                    # self.stdout.write(f'    SKIP Producto no encontrado: {product_slug}')
                    continue
                
                # Construct URL relative to static folder (for use with {% static %})
                rel_dir = os.path.relpath(root, settings.BASE_DIR).replace('\\', '/')
                
                # Remove 'static/' prefix if present
                if rel_dir.startswith('static/'):
                    rel_dir = rel_dir[7:]
                
                # Ensure no leading slash
                if rel_dir.startswith('/'):
                    rel_dir = rel_dir[1:]
                
                image_url = f'{rel_dir}/{image_file}'
                
                if not self.dry_run:
                    if is_detail:
                        # Gallery Image
                        _, created = ProductImage.objects.update_or_create(
                            product=product,
                            image_url=image_url,
                            defaults={
                                'is_primary': True, # It's a high res detail image
                                'display_order': 0,
                                'alt_text': f'{product.name} - Detalle'
                            }
                        )
                        if created:
                            total_created_detail += 1
                    else:
                        # Main Image (Thumbnail)
                        # Only update if empty or if forced? 
                        # Let's update to ensure it matches file
                        product.base_image_url = image_url
                        if not product.hover_image_url:
                            product.hover_image_url = image_url
                        product.save()
                        total_updated_main += 1
                else:
                    if is_detail:
                        total_created_detail += 1
                    else:
                        total_updated_main += 1
        
        self.stdout.write(self.style.SUCCESS(f'    ✓ Imágenes: {total_updated_main} principales actualizadas | {total_created_detail} detalles creados/actualizados'))
        self.stdout.write('')
        return total_created_detail # Return count of new records (ProductImage)

    def _import_calendarios_nested(self, base_path, category):
        """
        Importa templates de calendarios que tienen estructura anidada.
        """
        try:
            subcategory = Subcategory.objects.get(slug='calendarios-familiares', category=category)
        except Subcategory.DoesNotExist:
            self.stdout.write(self.style.WARNING('    Subcategoría "calendarios-familiares" no encontrada, omitiendo...'))
            return 0, 0
            
        folder_to_product = {
            'calendarios_magneticos': 'calendario-magnetico',
            'calendarios_escritorio': 'calendario-escritorio', 
            'calendarios_marcapaginas': 'calendario-marcapaginas',
            'calendarios_mousepad': 'calendario-mousepad',
            'calendarios_pared': 'calendario-pared',
            'calendarios_poster': 'tipos-calendario-poster',
            'calendarios': 'calendarios-familiares', # Generic/Fallback
            'calendarios_familiares': 'calendarios-familiares', # Generic/Fallback
        }
        
        total_created = 0
        total_updated = 0
        
        if not os.path.exists(base_path):
            return 0, 0
            
        try:
            items = os.listdir(base_path)
        except OSError:
            return 0, 0

        for folder_name in items:
            folder_path = os.path.join(base_path, folder_name)
            
            if not os.path.isdir(folder_path):
                continue

            # Determine product slug
            product_slug = folder_to_product.get(folder_name)
            if not product_slug:
                 # If not mapped, use folder name as product slug (or generic identifier)
                 # User asked to load ALL.
                 product_slug = folder_name.replace('_', '-')
            
            # Get all image files
            image_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.svg')
            try:
                images = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
            except OSError:
                continue
            
            if not images:
                continue

            self.stdout.write(f'     > Calendarios: {product_slug} ({len(images)} imgs)')
            
            for i, image_file in enumerate(images):
                file_slug = os.path.splitext(image_file)[0].lower()
                # Slug format: calendarios-{product_slug}-{file_slug}
                # Keep 'calendarios' prefix to identify typical calendar templates
                template_slug = f'calendarios-{product_slug}-{file_slug}'[:100]
                
                # Image URL
                # Construct relative path from static root
                # base_path is .../calendarios_regalos
                # folder_path is .../calendarios_regalos/folder_name
                image_url = f'media/template_images/calendarios_regalos/{folder_name}/{image_file}'
                
                # Template name
                template_name = file_slug.replace('-', ' ').replace('_', ' ').title()[:200]
                
                if not self.dry_run:
                    try:
                        template, created = DesignTemplate.objects.update_or_create(
                            slug=template_slug,
                            defaults={
                                'name': template_name,
                                'category': category,
                                'subcategory': subcategory,
                                'thumbnail_url': image_url,
                                'preview_url': image_url,
                                'is_popular': i < 10,  # Arbitrary popular logic
                                'is_new': i < 5,
                                'display_order': i,
                            }
                        )
                        
                        if created:
                            total_created += 1
                        else:
                            total_updated += 1
                    except Exception as e:
                         # Silently skip errors (e.g. duplicate slug if shortened)
                         pass
                else:
                    total_created += 1
                    
        return total_created, total_updated