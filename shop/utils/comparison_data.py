def get_comparison_data(category_slug):
    """
    Returns a dictionary with table headers and rows for the 'Compare Options' section
    based on the category slug.
    """
    # Default (Paper/Printing)
    default_data = {
        'headers': ['Característica', 'Estándar', 'Premium', 'Deluxe'],
        'rows': [
            {'label': 'Grosor', 'values': ['300g', '350g', '400g+']},
            {'label': 'Acabados', 'values': ['Mate, Brillante', '+ Soft Touch', '+ Foil, Relieve']},
            {'label': 'Bordes pintados', 'values': ['<i class="fas fa-times cross-icon"></i>', '<i class="fas fa-times cross-icon"></i>', '<i class="fas fa-check check-icon"></i>']},
            {'label': 'Precio desde', 'values': ['<strong class="text-blue-600">S/ 25</strong>', '<strong class="text-blue-600">S/ 45</strong>', '<strong class="text-blue-600">S/ 75</strong>']}
        ]
    }

    data_map = {
        'ropa-bolsos': {
            'headers': ['Característica', 'Estándar', 'Premium', 'Deluxe'],
            'rows': [
                {'label': 'Tela / Material', 'values': ['Jersey 30/1', 'Algodón Reactivo', 'Algodón Pima 50/1']},
                {'label': 'Tipo de Estampado', 'values': ['Transfer / Vinil', 'Serigrafía Tacto Cero', 'DTG / Bordado']},
                {'label': 'Durabilidad', 'values': ['Buena', 'Alta', 'Excelente']},
                {'label': 'Precio desde', 'values': ['<strong class="text-blue-600">S/ 25</strong>', '<strong class="text-blue-600">S/ 35</strong>', '<strong class="text-blue-600">S/ 55</strong>']}
            ]
        },
        'letreros-banners': {
            'headers': ['Material', 'Económico', 'Estándar', 'Reforzado'],
            'rows': [
                {'label': 'Material', 'values': ['Lona 10oz', 'Lona 13oz', 'Lona 13oz + Laminado']},
                {'label': 'Uso ideal', 'values': ['Interiores / Eventos cortos', 'Exteriores / Negocios', 'Larga duración / Sol directo']},
                {'label': 'Acabados', 'values': ['Corte al ras', 'Ojalillos / Bolsillos', 'Refuerzos perimetrales']},
                {'label': 'Precio m²', 'values': ['<strong class="text-blue-600">S/ 15</strong>', '<strong class="text-blue-600">S/ 25</strong>', '<strong class="text-blue-600">S/ 40</strong>']}
            ]
        },
        'stickers-etiquetas': {
            'headers': ['Tipo', 'Papel Adhesivo', 'Vinil Blanco', 'Vinil Transparente'],
            'rows': [
                {'label': 'Resistencia al agua', 'values': ['Baja', 'Alta (Impermeable)', 'Alta (Impermeable)']},
                {'label': 'Acabado', 'values': ['Brillo / Mate', 'Brillo / Mate', 'Brillo']},
                {'label': 'Uso', 'values': ['Etiquetas de producto (seco)', 'Botellas, Vehículos', 'Vidrios, Envases claros']},
                {'label': 'Precio (100u)', 'values': ['<strong class="text-blue-600">S/ 35</strong>', '<strong class="text-blue-600">S/ 55</strong>', '<strong class="text-blue-600">S/ 65</strong>']}
            ]
        },
        'productos-promocionales': {
            'headers': ['Artículos', 'Económicos', 'Ejecutivos', 'Premium'],
            'rows': [
                {'label': 'Material', 'values': ['Plástico / Textil simple', 'Metal / Cerámica', 'Tecnología / Cuero']},
                {'label': 'Personalización', 'values': ['Serigrafía 1 color', 'Láser / Sublimación', 'Full Color / Grabado']},
                {'label': 'Pedido Mínimo', 'values': ['100 unidades', '50 unidades', '10 unidades']},
                {'label': 'Ideal para', 'values': ['Masivos / Ferias', 'Regalos corporativos', 'Clientes VIP']}
            ]
        },
        'calendarios-regalos': {
            'headers': ['Tipo', 'Pared', 'Escritorio', 'Bolsillo / Imán'],
            'rows': [
                {'label': 'Papel', 'values': ['Couché 150g', 'Cartulina 300g + Base', 'Magnético / Cartulina']},
                {'label': 'Hojas', 'values': ['1 hoja / 12 hojas', '7 hojas / 13 hojas', '1 pieza']},
                {'label': 'Acabado', 'values': ['Varilla metálica', 'Anillado Doble Ring', 'Laminado Brillante']},
                {'label': 'Precio desde', 'values': ['<strong class="text-blue-600">S/ 5.00</strong>', '<strong class="text-blue-600">S/ 12.00</strong>', '<strong class="text-blue-600">S/ 1.50</strong>']}
            ]
        },
         'packaging-alimentario': {
            'headers': ['Material', 'Cartulina Folcote', 'Kraft Liner', 'Ecológico (Caña)'],
            'rows': [
                {'label': 'Resistencia Grasa', 'values': ['Media (con barniz)', 'Media', 'Alta (Biodegradable)']},
                {'label': 'Impresión', 'values': ['Full Color (Calidad Foto)', '1-2 Colores (Rústico)', 'Sin impresión / Sello']},
                {'label': 'Uso', 'values': ['Tortas, Pastelería', 'Hamburguesas, Snacks', 'Comida Caliente']},
                {'label': 'Precio', 'values': ['<strong class="text-blue-600">$$$</strong>', '<strong class="text-blue-600">$$</strong>', '<strong class="text-blue-600">$$$$</strong>']}
            ]
        }
    }

    return data_map.get(category_slug, default_data)
