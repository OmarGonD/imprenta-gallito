from django.core.management.base import BaseCommand
import pandas as pd
import os
from django.conf import settings
from shop.models import Product, ProductOptionValue

class Command(BaseCommand):
    help = 'Genera un archivo Excel para solicitar cotizaciones a proveedores (Ropa y Bolsos)'

    def handle(self, *args, **options):
        self.stdout.write('Generando archivo de cotización para proveedores...')
        
        # 1. Filtrar productos de Ropa y Bolsos
        products = Product.objects.filter(
            category__slug='ropa-bolsos',
            status='active'
        ).select_related('subcategory').order_by('subcategory__name', 'name')
        
        if not products.exists():
            self.stdout.write(self.style.WARNING('No se encontraron productos en la categoría Ropa y Bolsos'))
            return

        data = []
        
        # 2. Construir datos agrupados por Subcategoría
        # Obtenemos solo las subcategorías únicas que tienen productos activos
        subcategories = list(Product.objects.filter(
            category__slug='ropa-bolsos',
            status='active'
        ).values_list('subcategory__name', flat=True).distinct().order_by('subcategory__name'))
        
        standard_sizes = ['S', 'M', 'L', 'XL', 'XXL']
        standard_materials = ['Algodón', 'Poliéster']
        
        for subcat_name in subcategories:
            # Generamos filas genéricas por subcategoría, talla y material
            for size in standard_sizes:
                for material in standard_materials:
                    data.append({
                        'Categoría': 'Ropa y Bolsos', 
                        'Tipo de Producto (Subcategoría)': subcat_name,
                        'Talla': size,
                        'Material': material, 
                        'Color': 'Blanco/Color',
                        'Costo Unitario (1 un)': '',
                        'Costo Docena (12 un)': '',
                        'Costo Ciento (100 un)': '',
                        'Costo 500 un': '',
                        'Tiempo Producción': '',
                        'Comentarios': ''
                    })
            
            # Espaciador visual (opcional)
            # data.append({})

        # 3. Crear DataFrame
        df = pd.DataFrame(data)
        
        # 4. Guardar archivo
        output_dir = os.path.join(settings.BASE_DIR, 'static', 'data')
        os.makedirs(output_dir, exist_ok=True)
        
        filename = 'cotizacion_format_ropa_bolsos.xlsx'
        filepath = os.path.join(output_dir, filename)
        
        # Ajustar ancho de columnas (básico) con ExcelWriter si fuera necesario, 
        # pero para simpleza usaremos to_excel directo y el usuario puede ajustar.
        # Mejor usamos ExcelWriter para un poco de formato
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Cotización', index=False)
            
            # Auto-ajustar ancho de columnas
            worksheet = writer.sheets['Cotización']
            for idx, col in enumerate(df.columns):
                # Ancho aproximado basado en el header
                header_len = len(str(col)) + 2
                # O un ancho fijo razonable
                width = max(header_len, 15)
                if col == 'Producto': width = 40
                if col == 'Subcategoría': width = 25
                worksheet.column_dimensions[chr(65 + idx)].width = width

        self.stdout.write(self.style.SUCCESS(f'Archivo generado exitosamente en: {filepath}'))
        self.stdout.write(f'Total de productos: {len(data)}')
