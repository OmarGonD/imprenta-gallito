from django.core.management.base import BaseCommand
from shop.models import (
    ClothingCategory, ClothingSubCategory, ClothingColor, 
    ClothingSize, ClothingProduct, ClothingProductPricing
)


class Command(BaseCommand):
    help = 'Populate sample clothing data for the VistaPrint clone'

    def handle(self, *args, **options):
        self.stdout.write('Creating clothing categories...')
        
        # Create Colors
        colors_data = [
            {'name': 'Negro', 'slug': 'negro', 'hex_code': '#000000', 'order': 1},
            {'name': 'Blanco', 'slug': 'blanco', 'hex_code': '#FFFFFF', 'order': 2},
            {'name': 'Rojo', 'slug': 'rojo', 'hex_code': '#E53935', 'order': 3},
            {'name': 'Azul', 'slug': 'azul', 'hex_code': '#1E88E5', 'order': 4},
            {'name': 'Verde', 'slug': 'verde', 'hex_code': '#43A047', 'order': 5},
            {'name': 'Amarillo', 'slug': 'amarillo', 'hex_code': '#FDD835', 'order': 6},
            {'name': 'Naranja', 'slug': 'naranja', 'hex_code': '#FF6B00', 'order': 7},
            {'name': 'Gris', 'slug': 'gris', 'hex_code': '#757575', 'order': 8},
            {'name': 'Rosa', 'slug': 'rosa', 'hex_code': '#E91E63', 'order': 9},
            {'name': 'Morado', 'slug': 'morado', 'hex_code': '#9C27B0', 'order': 10},
            {'name': 'Celeste', 'slug': 'celeste', 'hex_code': '#03A9F4', 'order': 11},
            {'name': 'Marrón', 'slug': 'marron', 'hex_code': '#795548', 'order': 12},
        ]
        
        colors = {}
        for color_data in colors_data:
            color, created = ClothingColor.objects.get_or_create(
                slug=color_data['slug'],
                defaults=color_data
            )
            colors[color.slug] = color
            if created:
                self.stdout.write(f'  Created color: {color.name}')
        
        # Create Sizes - Clothing
        clothing_sizes_data = [
            {'name': 'XS', 'display_name': 'Extra Small', 'size_type': 'clothing', 'order': 1},
            {'name': 'S', 'display_name': 'Small', 'size_type': 'clothing', 'order': 2},
            {'name': 'M', 'display_name': 'Medium', 'size_type': 'clothing', 'order': 3},
            {'name': 'L', 'display_name': 'Large', 'size_type': 'clothing', 'order': 4},
            {'name': 'XL', 'display_name': 'Extra Large', 'size_type': 'clothing', 'order': 5},
            {'name': 'XXL', 'display_name': '2X Large', 'size_type': 'clothing', 'order': 6},
            {'name': '3XL', 'display_name': '3X Large', 'size_type': 'clothing', 'order': 7},
        ]
        
        # Create Sizes - Hats
        hat_sizes_data = [
            {'name': 'Único', 'display_name': 'Talla Única', 'size_type': 'hat', 'order': 1},
            {'name': 'S/M', 'display_name': 'Small/Medium', 'size_type': 'hat', 'order': 2},
            {'name': 'L/XL', 'display_name': 'Large/Extra Large', 'size_type': 'hat', 'order': 3},
        ]
        
        # Create Sizes - Bags
        bag_sizes_data = [
            {'name': 'Pequeño', 'display_name': 'Pequeño', 'size_type': 'bag', 'order': 1},
            {'name': 'Mediano', 'display_name': 'Mediano', 'size_type': 'bag', 'order': 2},
            {'name': 'Grande', 'display_name': 'Grande', 'size_type': 'bag', 'order': 3},
        ]
        
        sizes = {'clothing': [], 'hat': [], 'bag': []}
        for size_data in clothing_sizes_data + hat_sizes_data + bag_sizes_data:
            size, created = ClothingSize.objects.get_or_create(
                name=size_data['name'],
                size_type=size_data['size_type'],
                defaults=size_data
            )
            sizes[size.size_type].append(size)
            if created:
                self.stdout.write(f'  Created size: {size.name} ({size.size_type})')
        
        # Create Categories
        categories_data = [
            {
                'name': 'Camisetas',
                'slug': 'camisetas',
                'description': 'Camisetas personalizadas de alta calidad',
                'icon': 'fa-tshirt',
                'order': 1,
                'subcategories': [
                    {'name': 'Camisetas Clásicas', 'slug': 'camisetas-clasicas', 'order': 1},
                    {'name': 'Camisetas Cuello V', 'slug': 'camisetas-cuello-v', 'order': 2},
                    {'name': 'Camisetas Manga Larga', 'slug': 'camisetas-manga-larga', 'order': 3},
                    {'name': 'Camisetas Premium', 'slug': 'camisetas-premium', 'order': 4},
                ]
            },
            {
                'name': 'Polos',
                'slug': 'polos',
                'description': 'Polos empresariales y casuales',
                'icon': 'fa-user-tie',
                'order': 2,
                'subcategories': [
                    {'name': 'Polos Clásicos', 'slug': 'polos-clasicos', 'order': 1},
                    {'name': 'Polos Performance', 'slug': 'polos-performance', 'order': 2},
                    {'name': 'Polos Piqué', 'slug': 'polos-pique', 'order': 3},
                ]
            },
            {
                'name': 'Gorras',
                'slug': 'gorras',
                'description': 'Gorras personalizadas para tu marca',
                'icon': 'fa-hat-cowboy',
                'order': 3,
                'subcategories': [
                    {'name': 'Gorras Trucker', 'slug': 'gorras-trucker', 'order': 1},
                    {'name': 'Gorras Snapback', 'slug': 'gorras-snapback', 'order': 2},
                    {'name': 'Gorras Deportivas', 'slug': 'gorras-deportivas', 'order': 3},
                    {'name': 'Viseras', 'slug': 'viseras', 'order': 4},
                ]
            },
            {
                'name': 'Bolsas',
                'slug': 'bolsas',
                'description': 'Bolsas ecológicas y promocionales',
                'icon': 'fa-shopping-bag',
                'order': 4,
                'subcategories': [
                    {'name': 'Bolsas Tote', 'slug': 'bolsas-tote', 'order': 1},
                    {'name': 'Bolsas de Yute', 'slug': 'bolsas-yute', 'order': 2},
                    {'name': 'Mochilas', 'slug': 'mochilas', 'order': 3},
                    {'name': 'Bolsas Plegables', 'slug': 'bolsas-plegables', 'order': 4},
                ]
            },
            {
                'name': 'Chalecos',
                'slug': 'chalecos',
                'description': 'Chalecos de trabajo y promocionales',
                'icon': 'fa-vest',
                'order': 5,
                'subcategories': [
                    {'name': 'Chalecos de Seguridad', 'slug': 'chalecos-seguridad', 'order': 1},
                    {'name': 'Chalecos Corporativos', 'slug': 'chalecos-corporativos', 'order': 2},
                ]
            },
            {
                'name': 'Accesorios',
                'slug': 'accesorios',
                'description': 'Accesorios personalizados',
                'icon': 'fa-mitten',
                'order': 6,
                'subcategories': [
                    {'name': 'Pulseras', 'slug': 'pulseras', 'order': 1},
                    {'name': 'Lanyards', 'slug': 'lanyards', 'order': 2},
                    {'name': 'Delantales', 'slug': 'delantales', 'order': 3},
                ]
            },
        ]
        
        categories = {}
        subcategories = {}
        for cat_data in categories_data:
            subs = cat_data.pop('subcategories')
            category, created = ClothingCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[category.slug] = category
            if created:
                self.stdout.write(f'  Created category: {category.name}')
            
            for sub_data in subs:
                sub_data['category'] = category
                sub, sub_created = ClothingSubCategory.objects.get_or_create(
                    category=category,
                    slug=sub_data['slug'],
                    defaults=sub_data
                )
                subcategories[sub.slug] = sub
                if sub_created:
                    self.stdout.write(f'    Created subcategory: {sub.name}')
        
        # Create Sample Products
        self.stdout.write('Creating sample products...')
        
        products_data = [
            # Camisetas
            {
                'name': 'Camiseta Clásica 100% Algodón',
                'slug': 'camiseta-clasica-algodon',
                'sku': 'CAM-CLA-001',
                'description': 'Camiseta clásica de algodón 100%, perfecta para personalizar con tu logo o diseño. Tejido de alta calidad, cómodo y duradero.',
                'short_description': 'Camiseta de algodón 100%, ideal para personalizar',
                'category': categories['camisetas'],
                'subcategory': subcategories['camisetas-clasicas'],
                'base_price': 25.00,
                'material': '100% Algodón',
                'weight': '180 gr/m²',
                'features': 'Algodón peinado,Costuras reforzadas,Cuello redondo,Etiqueta removible',
                'is_featured': True,
                'is_bestseller': True,
                'colors': ['negro', 'blanco', 'rojo', 'azul', 'verde', 'amarillo', 'gris'],
                'size_type': 'clothing',
                'pricing_tiers': [(1, 9, 25.00), (10, 24, 22.00), (25, 49, 20.00), (50, None, 18.00)]
            },
            {
                'name': 'Camiseta Cuello V Premium',
                'slug': 'camiseta-cuello-v-premium',
                'sku': 'CAM-CV-001',
                'description': 'Camiseta con cuello en V, perfecta para un look más elegante.',
                'short_description': 'Cuello en V elegante',
                'category': categories['camisetas'],
                'subcategory': subcategories['camisetas-cuello-v'],
                'base_price': 28.00,
                'material': '100% Algodón Peinado',
                'weight': '160 gr/m²',
                'features': 'Algodón peinado,Cuello V,Corte slim fit',
                'is_new': True,
                'colors': ['negro', 'blanco', 'azul', 'gris'],
                'size_type': 'clothing',
                'pricing_tiers': [(1, 9, 28.00), (10, 24, 25.00), (25, 49, 23.00), (50, None, 21.00)]
            },
            # Polos
            {
                'name': 'Polo Empresarial Piqué',
                'slug': 'polo-empresarial-pique',
                'sku': 'POL-EMP-001',
                'description': 'Polo de tejido piqué ideal para uniformes corporativos.',
                'short_description': 'Polo piqué para uniformes',
                'category': categories['polos'],
                'subcategory': subcategories['polos-pique'],
                'base_price': 38.00,
                'sale_price': 32.00,
                'material': '60% Algodón, 40% Poliéster',
                'weight': '220 gr/m²',
                'features': 'Tejido piqué,Cuello con botones,Resistente al lavado',
                'is_featured': True,
                'colors': ['negro', 'blanco', 'azul', 'celeste'],
                'size_type': 'clothing',
                'pricing_tiers': [(1, 9, 32.00), (10, 24, 29.00), (25, 49, 27.00), (50, None, 25.00)]
            },
            # Gorras
            {
                'name': 'Gorra Trucker Clásica',
                'slug': 'gorra-trucker-clasica',
                'sku': 'GOR-TRU-001',
                'description': 'Gorra trucker con malla trasera transpirable. Ideal para sublimación o bordado.',
                'short_description': 'Gorra con malla trasera',
                'category': categories['gorras'],
                'subcategory': subcategories['gorras-trucker'],
                'base_price': 18.00,
                'material': 'Algodón y malla de poliéster',
                'features': 'Malla trasera,Cierre snapback,Visera curva',
                'is_bestseller': True,
                'colors': ['negro', 'blanco', 'rojo', 'azul'],
                'size_type': 'hat',
                'pricing_tiers': [(1, 9, 18.00), (10, 24, 16.00), (25, 49, 14.00), (50, None, 12.00)]
            },
            {
                'name': 'Gorra Snapback Premium',
                'slug': 'gorra-snapback-premium',
                'sku': 'GOR-SNA-001',
                'description': 'Gorra snapback de alta calidad con visera plana.',
                'short_description': 'Visera plana estilo urbano',
                'category': categories['gorras'],
                'subcategory': subcategories['gorras-snapback'],
                'base_price': 22.00,
                'material': 'Acrílico y lana',
                'features': 'Visera plana,Cierre snapback,Estructura rígida',
                'is_new': True,
                'colors': ['negro', 'gris', 'rojo'],
                'size_type': 'hat',
                'pricing_tiers': [(1, 9, 22.00), (10, 24, 20.00), (25, 49, 18.00), (50, None, 16.00)]
            },
            # Bolsas
            {
                'name': 'Bolsa Tote Ecológica',
                'slug': 'bolsa-tote-ecologica',
                'sku': 'BOL-TOT-001',
                'description': 'Bolsa tote de algodón reutilizable, perfecta para compras y promociones.',
                'short_description': 'Bolsa de algodón reutilizable',
                'category': categories['bolsas'],
                'subcategory': subcategories['bolsas-tote'],
                'base_price': 12.00,
                'material': '100% Algodón',
                'features': 'Ecológica,Lavable,Asas largas',
                'is_featured': True,
                'colors': ['blanco', 'negro'],
                'size_type': 'bag',
                'pricing_tiers': [(1, 9, 12.00), (10, 24, 10.00), (25, 49, 8.00), (50, None, 6.00)]
            },
            {
                'name': 'Mochila Promocional',
                'slug': 'mochila-promocional',
                'sku': 'BOL-MOC-001',
                'description': 'Mochila con cordones, ideal para eventos y promociones.',
                'short_description': 'Mochila con cordones',
                'category': categories['bolsas'],
                'subcategory': subcategories['mochilas'],
                'base_price': 15.00,
                'material': 'Nylon',
                'features': 'Ligera,Compacta,Cierre con cordones',
                'colors': ['negro', 'rojo', 'azul', 'verde'],
                'size_type': 'bag',
                'pricing_tiers': [(1, 9, 15.00), (10, 24, 13.00), (25, 49, 11.00), (50, None, 9.00)]
            },
            # Chalecos
            {
                'name': 'Chaleco de Seguridad Reflectivo',
                'slug': 'chaleco-seguridad-reflectivo',
                'sku': 'CHA-SEG-001',
                'description': 'Chaleco de alta visibilidad con bandas reflectivas.',
                'short_description': 'Alta visibilidad con reflectivos',
                'category': categories['chalecos'],
                'subcategory': subcategories['chalecos-seguridad'],
                'base_price': 25.00,
                'material': 'Poliéster',
                'features': 'Bandas reflectivas,Alta visibilidad,Cierre frontal',
                'colors': ['amarillo', 'naranja'],
                'size_type': 'clothing',
                'pricing_tiers': [(1, 9, 25.00), (10, 24, 22.00), (25, 49, 20.00), (50, None, 18.00)]
            },
        ]
        
        for prod_data in products_data:
            color_slugs = prod_data.pop('colors')
            size_type = prod_data.pop('size_type')
            pricing_tiers_data = prod_data.pop('pricing_tiers')
            
            product, created = ClothingProduct.objects.get_or_create(
                sku=prod_data['sku'],
                defaults=prod_data
            )
            
            if created:
                self.stdout.write(f'  Created product: {product.name}')
                
                # Add colors
                for color_slug in color_slugs:
                    if color_slug in colors:
                        product.available_colors.add(colors[color_slug])
                
                # Add sizes
                for size in sizes[size_type]:
                    product.available_sizes.add(size)
                
                # Add pricing tiers
                for min_qty, max_qty, price in pricing_tiers_data:
                    ClothingProductPricing.objects.create(
                        product=product,
                        min_quantity=min_qty,
                        max_quantity=max_qty,
                        price_per_unit=price
                    )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated clothing data!'))
