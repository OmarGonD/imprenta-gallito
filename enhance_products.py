
import pandas as pd
import os

excel_path = r'D:\web_proyects\imprenta_gallito\static\data\products_complete.xlsx'

marketing_data = [
    {
        "name": "Vaso Promocional Impact",
        "description": "Haz que tu marca destaque con este vaso de diseño moderno y alto impacto visual. Ideal para campañas masivas y eventos corporativos. Su superficie ofrece una excelente área de impresión para tu logotipo."
    },
    {
        "name": "Vaso Ejecutivo Elite",
        "description": "Elegancia y funcionalidad en un solo producto. Este vaso es el regalo perfecto para clientes VIP y ejecutivos. Acabado premium que refuerza la imagen profesional de tu empresa."
    },
    {
        "name": "Vaso Eco-Friendly Corporate",
        "description": "Demuestra el compromiso de tu empresa con el medio ambiente. Un vaso reutilizable, práctico y con gran estilo, diseñado para reducir el consumo de plásticos de un solo uso."
    },
    {
        "name": "Vaso Branding Pro",
        "description": "Maximiza la visibilidad de tu marca en cada sorbo. Diseñado pensando en la durabilidad y la estética, este vaso asegura que tu mensaje perdure en manos de tus clientes."
    },
    {
        "name": "Vaso Evento Plus",
        "description": "El complemento indispensable para tu próximo evento o congreso. Ligero, resistente y con un diseño que invita a ser conservado por los asistentes."
    },
    {
        "name": "Vaso Style Urbano",
        "description": "Conecta con un público moderno y dinámico. Su diseño versátil lo hace perfecto para la oficina, el gimnasio o el uso diario, llevando tu marca a todas partes."
    },
    {
        "name": "Vaso Vision 360",
        "description": "Una perspectiva fresca para tu merchandising. Ofrece un diseño ergonómico y elegante, garantizando una experiencia de usuario superior."
    },
    {
        "name": "Vaso Classic Renovado",
        "description": "La evolución de un clásico. Combina la familiaridad de un diseño tradicional con toques modernos que lo hacen destacar en cualquier escritorio o mesa de reuniones."
    },
    {
        "name": "Vaso Tech Modern",
        "description": "Diseño vanguardista para marcas innovadoras. Sus líneas limpias y estructura sólida lo convierten en el soporte ideal para empresas de tecnología y servicios modernos."
    },
    {
        "name": "Vaso Daily Essential",
        "description": "Conviértete en parte de la rutina diaria de tus clientes. Un vaso práctico y resistente, diseñado para acompañarlos en su día a día, manteniendo tu marca siempre presente."
    }
]

try:
    df = pd.read_excel(excel_path)
    
    # Strip whitespace just in case
    df['category_slug'] = df['category_slug'].astype(str).str.strip()
    df['subcategory_slug'] = df['subcategory_slug'].astype(str).str.strip()
    
    print("Unique Categories:", df['category_slug'].unique())
    print("Unique Subcategories:", df['subcategory_slug'].unique())

    mask = (df['category_slug'] == 'productos_promocionales') & \
           (df['subcategory_slug'] == 'vasos')
    
    vasos_indices = df[mask].index.tolist()
    print(f"Found {len(vasos_indices)} products to update.")
    
    for i, idx in enumerate(vasos_indices):
        data = marketing_data[i % len(marketing_data)]
        
        # Get code from existing name or generate suffix
        original_name = str(df.at[idx, 'product_name'])
        suffix = ""
        # Assuming original format "Vaso CODE" or "Vaso V-CODE"
        # We want to keep the distinct code to differentiate products.
        # Let's clean "Vaso " prefix if present to isolate the code.
        
        # If logical name was "Vaso V-0UAJMX0I"
        code = original_name.replace("Vaso ", "") 
        
        new_name = f"{data['name']} {code}"
        
        df.at[idx, 'product_name'] = new_name
        df.at[idx, 'description'] = data["description"]
        # print(f"Updated {original_name} -> {new_name}")

    if len(vasos_indices) > 0:
        df.to_excel(excel_path, index=False)
        print("Successfully updated product names and descriptions.")
    else:
        print("No rows matched criteria. Check slug values.")

except Exception as e:
    print(f"Error: {e}")
