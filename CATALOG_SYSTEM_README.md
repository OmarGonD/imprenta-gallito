# Sistema de Categorías Personalizable - Imprenta Gallito

## 📋 Descripción General

Sistema completo de ecommerce para productos personalizables con las siguientes características:

- **Categorías dinámicas** de productos con subcategorías
- **Configurador de productos** en tiempo real con cálculo de precios
- **Sistema de variantes** (tamaño, material, acabado, etc.)
- **Precios escalonados** por volumen con descuentos automáticos
- **Filtros avanzados** de productos
- **Búsqueda inteligente**
- **Panel de administración** completo
- **Importación masiva** desde archivos CSV

---

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
shop/
├── catalog_models.py          # Modelos de datos del catálogo
├── catalog_views.py           # Vistas del catálogo
├── catalog_urls.py            # URLs del catálogo
├── catalog_admin.py           # Configuración del admin
├── services/
│   ├── pricing_service.py     # Lógica de precios
│   └── filter_service.py      # Lógica de filtros
├── management/commands/
│   └── import_catalog.py      # Comando de importación
├── migrations/
│   └── 0017_catalog_system.py # Migración de base de datos
└── templates/catalog/
    ├── catalog_home.html      # Página principal
    ├── category.html          # Vista de categoría
    ├── subcategory.html       # Vista de subcategoría
    ├── product_detail.html    # Detalle del producto
    └── search.html            # Búsqueda

static/
├── css/
│   ├── catalog.css            # Estilos del catálogo
│   └── product-configurator.css # Estilos del configurador
└── js/
    ├── catalog.js             # JavaScript general
    └── product-configurator.js # Configurador interactivo
```

---

## 🚀 Instalación y Configuración

### 1. Ejecutar Migraciones

```bash
python manage.py migrate
```

Esto creará todas las tablas necesarias:
- `CatalogCategory`
- `CatalogSubcategory`
- `CatalogProduct`
- `CatalogVariantType`
- `CatalogVariantOption`
- `CatalogProductVariantType`
- `CatalogPriceTier`

### 2. Importar Datos desde CSV

```bash
python manage.py import_categories
```

Este comando importará automáticamente los datos desde los archivos CSV ubicados en `static/data/`:
- `categories_complete.csv`
- `subcategories_complete.csv`
- `products_complete.csv`
- `variant_types_complete.csv`
- `variant_options_complete.csv`
- `product_variant_types_complete.csv`
- `price_tiers_complete.csv`

**Opciones del comando:**

```bash
# Forzar re-importación (elimina datos existentes)
python manage.py import_categories --force

# Simulación sin escribir en base de datos
python manage.py import_categories --dry-run

# Ambas opciones
python manage.py import_categories --force --dry-run
```

### 3. Crear Superusuario (si no existe)

```bash
python manage.py createsuperuser
```

### 4. Acceder al Sistema

- **Categorías públicas**: http://localhost:8000/categorias/
- **Panel de administración**: http://localhost:8000/admin/

---

## 📊 Estructura de Datos CSV

### categories_complete.csv

```csv
name,slug,description,icon,is_active,display_order
Tarjetas de Presentación,tarjetas-presentacion,Tarjetas personalizadas de alta calidad,fa-id-card,True,1
Volantes,volantes,Volantes publicitarios personalizables,fa-file-alt,True,2
```

### products_complete.csv

```csv
name,slug,sku,category_slug,subcategory_slug,description,min_price,status,is_featured
Tarjetas Standard,tarjetas-standard,TC-STD-001,tarjetas-presentacion,standard,Tarjetas de presentación estándar,45.00,active,True
```

### variant_types_complete.csv

```csv
name,slug,description,icon,display_order
Tamaño,tamano,Tamaño del producto,fa-ruler,1
Material,material,Tipo de material,fa-layer-group,2
```

### variant_options_complete.csv

```csv
variant_type_slug,value,additional_cost,is_default,display_order
tamano,8.5cm x 5.5cm,0.00,True,1
tamano,9cm x 5cm,5.00,False,2
material,Papel Couché,0.00,True,1
material,Papel Bond,2.50,False,2
```

### price_tiers_complete.csv

```csv
product_slug,min_quantity,max_quantity,price_per_unit,discount_percentage
tarjetas-standard,100,499,0.45,0
tarjetas-standard,500,999,0.40,11.11
tarjetas-standard,1000,,0.35,22.22
```

---

## 🎨 Uso del Sistema

### Panel de Administración

#### Gestión de Categorías

1. Ir a **Admin > Catálogo > Categorías**
2. Crear/Editar categorías con:
   - Nombre y descripción
   - Slug (URL amigable)
   - Icono (clase de Font Awesome)
   - Estado activo/inactivo
   - Orden de visualización

#### Gestión de Productos

1. Ir a **Admin > Catálogo > Productos**
2. Crear producto con información básica
3. Agregar **Tipos de Variante** disponibles
4. Configurar **Tiers de Precio** por volumen

#### Tipos de Variante

Los tipos de variante definen las opciones de personalización:

- **Tamaño**: Dimensiones del producto
- **Material**: Tipo de papel o material
- **Acabado**: Mate, brillante, UV, etc.
- **Orientación**: Vertical u horizontal
- **Impresión**: Una cara o ambas caras

Cada tipo de variante puede tener múltiples opciones con costos adicionales.

### Frontend - Experiencia del Usuario

#### Navegación del Sistema

1. **Página Principal** (`/categorias/`)
   - Muestra todas las categorías con conteo de productos
   - Barra de búsqueda global
   - Productos destacados

2. **Vista de Categoría** (`/categorias/{categoria}/`)
   - Grid de productos de la categoría
   - Filtros por subcategoría y precio
   - Búsqueda dentro de la categoría

3. **Vista de Producto** (`/categorias/{categoria}/producto/{producto}/`)
   - Imágenes del producto
   - Configurador interactivo
   - Cálculo de precios en tiempo real
   - Información de tiers de precio

#### Configurador de Productos

El configurador permite:

1. **Seleccionar cantidad** con botones +/-
2. **Elegir variantes** (tamaño, material, etc.)
3. **Ver precio actualizado** en tiempo real:
   - Precio base unitario
   - Costos adicionales por variantes
   - Subtotal
   - Descuentos por volumen
   - **Precio total**

4. **Agregar al carrito** con configuración validada

---

## 🔧 API Endpoints

### Cálculo de Precios (AJAX)

**POST** `/categorias/api/calculate-price/`

```json
{
  "product_slug": "tarjetas-standard",
  "quantity": 500,
  "selected_options": [
    {
      "variant_type_id": 1,
      "option_id": 2
    }
  ]
}
```

**Respuesta:**

```json
{
  "success": true,
  "price_info": {
    "base_price": 0.40,
    "additional_cost": 5.00,
    "unit_price": 5.40,
    "subtotal": 2700.00,
    "total_price": 2700.00,
    "savings": 25.00,
    "tier": {
      "min_quantity": 500,
      "max_quantity": 999,
      "price_per_unit": 0.40
    }
  }
}
```

### Validación de Configuración

**POST** `/categorias/api/validate-config/`

```json
{
  "product_slug": "tarjetas-standard",
  "selected_options": [...]
}
```

### Obtener Variantes

**GET** `/categorias/api/product/{slug}/variants/`

### Obtener Tiers de Precio

**GET** `/categorias/api/product/{slug}/price-tiers/`

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Crear Producto con Variantes

```python
from shop.catalog_models import (
    CatalogProduct, CatalogVariantType, 
    CatalogVariantOption, CatalogPriceTier
)

# Crear producto
producto = CatalogProduct.objects.create(
    name="Tarjetas Premium",
    slug="tarjetas-premium",
    sku="TC-PREM-001",
    category=categoria,
    description="Tarjetas de presentación premium",
    min_price=65.00,
    status='active'
)

# Agregar tipo de variante
variant_type = CatalogVariantType.objects.get(slug='tamano')
producto.product_variant_types.create(
    variant_type=variant_type,
    is_required=True
)

# Crear tiers de precio
CatalogPriceTier.objects.create(
    product=producto,
    min_quantity=100,
    max_quantity=499,
    price_per_unit=0.65
)
```

### Ejemplo 2: Calcular Precio Programáticamente

```python
from shop.services.pricing_service import calculate_product_price

precio_info = calculate_product_price(
    product_slug='tarjetas-premium',
    quantity=500,
    selected_options=[
        {'variant_type_id': 1, 'option_id': 2}
    ]
)

print(f"Precio total: S/ {precio_info['total_price']}")
```

### Ejemplo 3: Buscar Productos

```python
from shop.services.filter_service import search_products

resultados = search_products('tarjetas', limit=10)
```

---

## 🎯 Características Avanzadas

### 1. Precios Escalonados

El sistema calcula automáticamente el mejor precio según la cantidad:

```python
# Ejemplo de tiers
100-499 unidades: S/ 0.65 c/u
500-999 unidades: S/ 0.55 c/u (15% desc.)
1000+ unidades: S/ 0.45 c/u (31% desc.)
```

### 2. Costos Adicionales por Variantes

Cada opción de variante puede tener un costo adicional:

```python
# Base: S/ 0.50 c/u
# + Papel couché: S/ 0.05
# + Acabado UV: S/ 0.10
# = Total: S/ 0.65 c/u
```

### 3. Validación de Configuración

El sistema valida que todas las variantes requeridas estén seleccionadas:

```python
validation = validate_product_configuration(
    product_slug='tarjetas-premium',
    selected_options=[]  # Error: faltan variantes requeridas
)
```

### 4. Filtros Dinámicos

Los filtros se generan dinámicamente según los productos disponibles:

- Subcategorías con conteo de productos
- Rango de precios
- Búsqueda por texto

---

## 📱 Responsive Design

El sistema está completamente optimizado para:

- **Desktop** (>992px): Layout completo con sidebar
- **Tablet** (768px-992px): Grid adaptativo
- **Mobile** (<768px): Vista apilada

---

## 🔐 Seguridad

- Validación de tokens CSRF en todas las peticiones AJAX
- Sanitización de entrada de usuarios
- Validación de precios en el backend
- Protección contra inyección SQL (Django ORM)

---

## 🧪 Testing

### Ejecutar Tests

```bash
python manage.py test shop.tests
```

### Tests Incluidos

- Cálculo de precios
- Validación de configuraciones
- Filtros de productos
- Búsqueda
- Importación de datos

---

## 📈 Próximas Mejoras

- [ ] Integración con sistema de carrito existente
- [ ] Generación de cotizaciones PDF
- [ ] Sistema de reviews y ratings
- [ ] Comparador de productos
- [ ] Wishlist de productos
- [ ] Notificaciones de descuentos
- [ ] Export de productos a Excel
- [ ] API REST completa
- [ ] Sistema de cupones específico para catálogo

---

## 🐛 Troubleshooting

### Problema: No se muestran productos

**Solución:**
1. Verificar que las migraciones estén aplicadas
2. Verificar que los datos estén importados
3. Verificar que los productos estén activos

```bash
python manage.py shell
>>> from shop.catalog_models import CatalogProduct
>>> CatalogProduct.objects.filter(status='active').count()
```

### Problema: Error al calcular precios

**Solución:**
1. Verificar que el producto tenga tiers de precio
2. Verificar que las variantes existan
3. Revisar logs del servidor

### Problema: Imágenes no se cargan

**Solución:**
1. Verificar configuración de MEDIA_URL y MEDIA_ROOT
2. Ejecutar `python manage.py collectstatic`
3. Verificar permisos de carpetas

---

## 📞 Soporte

Para preguntas o problemas:

1. Revisar esta documentación
2. Consultar el código fuente (comentado)
3. Revisar logs del sistema
4. Contactar al equipo de desarrollo

---

## 📝 Changelog

### v1.0.0 (2025-01-26)

- ✅ Sistema completo de categorías
- ✅ Configurador de productos
- ✅ Cálculo de precios en tiempo real
- ✅ Importación desde CSV
- ✅ Panel de administración
- ✅ Templates responsive
- ✅ Documentación completa

---

## 👨‍💻 Créditos

Sistema desarrollado para **Imprenta Gallito**

Tecnologías utilizadas:
- Django 4.x
- Python 3.x
- JavaScript ES6+
- Bootstrap 4
- Font Awesome 5

---

## 📄 Licencia

Todos los derechos reservados © 2025 Imprenta Gallito
