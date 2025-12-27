# Imprenta Gallito - Sistema E-commerce Backend

Este repositorio contiene el código fuente del sistema de e-commerce para **Imprenta Gallito Perú**. A continuación se detalla cómo operar el sistema, gestionar el catálogo y administrar los precios.

---

## 🛠️ Requisitos Previos

- Python 3.8+
- Virtual Environment (recomendado)

### Instalación Rápida
```bash
# Activar entorno virtual
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Migraciones base
python manage.py migrate

# Crear superusuario (para admin)
python manage.py createsuperuser
```

---

## 📦 Gestión del Catálogo (`import_catalog`)

El sistema utiliza archivos **Excel** como la "Fuente de la Verdad" para el catálogo de productos. Esto facilita la edición masiva de datos sin necesidad de usar el panel de administración uno por uno.

### Archivos de Datos
Los archivos se encuentran en: `static/data/`

| Archivo | Descripción |
|---------|-------------|
| `categories_complete.xlsx` | Categorías principales (ej. Ropa, Stickers) |
| `subcategories_complete.xlsx` | Subcategorías y jerarquía |
| `products_complete.xlsx` | Detalles de productos (slugs, nombres, imágenes) |
| `price_tiers_complete.xlsx` | **Precios finales** y descuentos por volumen |

### Comando de Importación
Para actualizar el sitio web con los cambios del Excel, ejecuta:

```bash
python manage.py import_catalog
```

Este comando:
1. Lee los Excel.
2. Crea/Actualiza Categorías, Subcategorías y Productos en la base de datos.
3. Actualiza los precios y tiers.
4. Vincula imágenes automáticamente si están en las carpetas correctas.

---

## 💰 Sistema de "Smart Pricing"

Para categorías complejas como **Ropa** y **Stickers**, los precios se calculan mediante una lógica automática (costos base + márgenes + fees), en lugar de escribirlos manualmente uno por uno.

### Flujo de Trabajo

#### 1. Configurar Reglas
Edita el archivo de configuración:
📂 `shop/utils/smart_pricing_config.py`

Aquí defines:
- Costos base de producción.
- Márgenes de ganancia por cantidad (Tiers).
- Sobrecargos (Surcharges) por color, talla o acabados.

```python
# Ejemplo de configuración
'ropa-bolsos': {
    'base_cost': Decimal('40.00'),
    'tiers': [
        {'min': 1,  'price': Decimal('67.00')},
        {'min': 12, 'price': Decimal('62.00')},
        # ...
    ]
}
```

#### 2. Generar Precios (Excel)
Ejecuta el comando para calcular los precios y escribirlos en `price_tiers_complete.xlsx`:

```bash
python manage.py apply_smart_pricing
```

> **🛡️ Nota de Seguridad:** Este comando **NO** sobrescribirá precios que hayas editado manualmente en el Excel, a menos que uses la bandera `--force`.

**Para forzar un recálculo total:**
```bash
python manage.py apply_smart_pricing --force
```

#### 3. Publicar Cambios
Una vez generado el Excel con los precios nuevos, impórtalos a la web:

```bash
python manage.py import_catalog
```

---

## ✍️ Edición Manual de Precios

Si necesitas un precio especial para un producto específico que rompa la lógica automática:

1. Abre `static/data/price_tiers_complete.xlsx`.
2. Busca la fila del producto.
3. Edita la columna `unit_price`.
4. Guarda el archivo.
5. Ejecuta `python manage.py import_catalog`.

Tu precio manual se mantendrá (incluso si corres `apply_smart_pricing` en el futuro), protegiendo tus ediciones personalizadas.

---

## 📂 Estructura Clave del Proyecto

- `shop/management/commands/`
  - `import_catalog.py`: Lógica de importación masiva.
  - `apply_smart_pricing.py`: Generador de precios inteligentes.
- `shop/utils/`
  - `smart_pricing_config.py`: Reglas de negocio para precios.
- `static/data/`: Archivos Excel del catálogo.
- `static/media/`: Imágenes de productos (organizadas por carpetas).
