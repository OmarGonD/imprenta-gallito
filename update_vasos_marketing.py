import pandas as pd
import os

excel_path = r'D:\web_proyects\imprenta_gallito\static\data\products_complete.xlsx'

# Based on the visual analysis of the products, I'll create targeted names and descriptions
# The products show various glass styles: pilsner, wine glasses, tumblers, cocktail glasses, mugs

marketing_templates = [
    {
        "name": "Vaso Pilsner Elegante",
        "description": "Vaso cervecero estilo pilsner de cristal transparente. Ideal para bares, restaurantes y eventos corporativos. Su forma estilizada realza cualquier bebida y tu logo destacará con elegancia."
    },
    {
        "name": "Copa Sin Tallo Premium",
        "description": "Copas modernas sin tallo, perfectas para vino o cócteles. Diseño contemporáneo que combina funcionalidad y estilo. Excelente para regalos corporativos y merchandising de alta gama."
    },
    {
        "name": "Vaso Tumbler Versátil",
        "description": "Vaso tipo tumbler de vidrio transparente con forma cónica. Perfecto para cualquier tipo de bebida. Su diseño clásico garantiza que tu marca sea visible desde cualquier ángulo."
    },
    {
        "name": "Copa Cóctel Profesional",
        "description": "Copa para cócteles con base robusta y diseño profesional. Ideal para hoteles, eventos y promociones de bebidas premium. Dale a tu marca una imagen sofisticada y memorable."
    },
    {
        "name": "Jarra Cervecera con Asa",
        "description": "Jarra de cerveza tipo stein con asa ergonómica. Resistente y de gran capacidad, perfecta para festivales, oktoberfest y eventos temáticos. Tu logo será el protagonista en cada brindis."
    },
    {
        "name": "Vaso Alto Cristalino",
        "description": "Vaso alto de cristal transparente ideal para refrescos, cervezas y bebidas mixtas. Su elegante altura maximiza el espacio para personalización. Perfecto para campañas de gran alcance."
    },
    {
        "name": "Copa Vino Stemless Duo",
        "description": "Set de copas de vino sin tallo, tendencia moderna en vajilla. Perfecto para regalos ejecutivos y kits de bienvenida. Su diseño minimalista realza la presencia de tu marca."
    },
    {
        "name": "Vaso Cónico Base Gruesa",
        "description": "Vaso cónico con base reforzada que transmite calidad y durabilidad. Excelente estabilidad y peso ideal. Tu imagen corporativa lucirá profesional en cada mesa o escritorio."
    },
    {
        "name": "Vaso Everyday Promocional",
        "description": "Vaso de uso diario con diseño práctico y atemporal. Ideal para campañas masivas y regalos promocionales accesibles. Mantén tu marca presente en la rutina de tus clientes."
    },
    {
        "name": "Copa Elegance Premium",
        "description": "Copa de vidrio con diseño elegante y refinado. Perfecta para eventos especiales, bodas corporativas y premios. Asocia tu marca con momentos de celebración y exclusividad."
    }
]

try:
    df = pd.read_excel(excel_path)
    
    # Get all products with subcategory 'vasos' regardless of category
    # (since we saw they exist, let's filter more broadly)
    df['subcategory_slug'] = df['subcategory_slug'].astype(str).str.strip()
    
    vasos_mask = df['subcategory_slug'] == 'vasos'
    vasos_indices = df[vasos_mask].index.tolist()
    
    print(f"Found {len(vasos_indices)} vaso products to update")
    
    if len(vasos_indices) == 0:
        # Debug: show what we have
        print("No vasos found. Showing all unique subcategories:")
        print(df['subcategory_slug'].unique())
    else:
        # Update each product
        for i, idx in enumerate(vasos_indices):
            # Get the template (cycle through if we have more products than templates)
            template = marketing_templates[i % len(marketing_templates)]
            
            # Get the original code/SKU to make names unique
            original_name = str(df.at[idx, 'product_name'])
            sku = str(df.at[idx, 'sku'])
            
            # Extract code from SKU (format: PP-VAS-XXXXXX)
            code_parts = sku.split('-')
            if len(code_parts) >= 3:
                code = code_parts[-1]  # Get the last part (the unique code)
            else:
                code = f"#{i+1:02d}"
            
            # Create unique name by appending code
            # For variety, cycle through the template names
            new_name = f"{template['name']} {code}"
            
            df.at[idx, 'product_name'] = new_name
            df.at[idx, 'description'] = template['description']
            
            print(f"✓ Updated: {new_name}")
        
        # Save the updated Excel
        df.to_excel(excel_path, index=False)
        print(f"\n✅ Successfully updated {len(vasos_indices)} products!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
