"""
Servicio de filtrado y búsqueda de productos del catálogo
Permite filtrar por categoría, subcategoría, precio, variantes, etc.

MIGRATION NOTE (2024):
- Now imports Category, Subcategory, Product from shop.models
- Previously imported from catalog_models.py (deprecated)
"""
from decimal import Decimal
from typing import Dict, List, Optional
from django.db.models import QuerySet, Q, Min, Max, Count, Prefetch

# Import from models.py (migrated from catalog_models.py)
from shop.models import (
    Category,
    Subcategory,
    Product,
    VariantType,
    VariantOption,
    PriceTier
)


def get_products_by_category(
    category_slug: str,
    filters: Optional[Dict] = None
) -> QuerySet:
    """
    Obtiene productos de una categoría con filtros opcionales
    
    Args:
        category_slug: Slug de la categoría
        filters: Dict opcional con filtros:
            {
                'subcategory': str (slug de subcategoría),
                'min_price': Decimal,
                'max_price': Decimal,
                'status': str ('active' o 'seasonal'),
                'search': str (búsqueda en nombre/descripción),
                'variant_options': List[str] (slugs de opciones)
            }
    
    Returns:
        QuerySet de CatalogProduct filtrado y optimizado
    
    Raises:
        ValueError: Si la categoría no existe
    """
    try:
        category = Category.objects.get(slug=category_slug)
    except Category.DoesNotExist:
        raise ValueError(f"Categoría no encontrada: {category_slug}")
    
    # Query base
    queryset = Product.objects.filter(
        category=category
    ).select_related(
        'category', 'subcategory'
    ).prefetch_related(
        'price_tiers',
        'product_variant_types__variant_type'
    )
    
    # Aplicar filtros si existen
    if filters:
        queryset = apply_filters(queryset, filters)
    
    return queryset.distinct()


def get_products_by_subcategory(subcategory_slug: str) -> QuerySet:
    """
    Obtiene productos de una subcategoría específica
    
    Args:
        subcategory_slug: Slug de la subcategoría
    
    Returns:
        QuerySet de productos
    
    Raises:
        ValueError: Si la subcategoría no existe
    """
    try:
        subcategory = Subcategory.objects.get(slug=subcategory_slug)
    except Subcategory.DoesNotExist:
        raise ValueError(f"Subcategoría no encontrada: {subcategory_slug}")
    
    return Product.objects.filter(
        subcategory=subcategory,
        status='active'
    ).select_related(
        'category', 'subcategory'
    ).prefetch_related('price_tiers')


def apply_filters(queryset: QuerySet, filters: Dict) -> QuerySet:
    """
    Aplica múltiples filtros a un QuerySet de productos
    
    Args:
        queryset: QuerySet base de productos
        filters: Dict con filtros a aplicar
    
    Returns:
        QuerySet filtrado
    """
    # Filtro por subcategoría
    if filters.get('subcategory'):
        queryset = queryset.filter(
            subcategory__slug=filters['subcategory']
        )
    
    # Filtro por estado
    if filters.get('status'):
        queryset = queryset.filter(status=filters['status'])
    
    # Búsqueda por texto
    if filters.get('search'):
        search_term = filters['search']
        queryset = queryset.filter(
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(sku__icontains=search_term)
        )
    
    # Filtro por rango de precio
    # Nota: Esto filtra por el precio mínimo de cada producto
    if filters.get('min_price') or filters.get('max_price'):
        product_ids = []
        for product in queryset:
            min_price = product.price_tiers.aggregate(
                min_price=Min('unit_price')
            )['min_price']
            
            if min_price:
                include = True
                if filters.get('min_price') and min_price < Decimal(str(filters['min_price'])):
                    include = False
                if filters.get('max_price') and min_price > Decimal(str(filters['max_price'])):
                    include = False
                if include:
                    product_ids.append(product.slug)
        
        queryset = queryset.filter(slug__in=product_ids)
    
    # Filtro por opciones de variantes
    if filters.get('variant_options'):
        variant_option_slugs = filters['variant_options']
        if isinstance(variant_option_slugs, str):
            variant_option_slugs = [variant_option_slugs]
        
        # Encontrar productos que tengan las variantes especificadas
        options = VariantOption.objects.filter(
            slug__in=variant_option_slugs
        ).select_related('variant_type')
        
        for option in options:
            queryset = queryset.filter(
                product_variant_types__variant_type=option.variant_type
            )
    
    return queryset


def get_filter_options_for_category(category_slug: str) -> Dict:
    """
    Obtiene las opciones de filtro disponibles para una categoría
    
    Args:
        category_slug: Slug de la categoría
    
    Returns:
        Dict con opciones de filtro:
        {
            'category': {
                'slug': str,
                'name': str,
                'total_products': int
            },
            'subcategories': [
                {'slug': str, 'name': str, 'count': int}
            ],
            'price_range': {
                'min': float,
                'max': float
            },
            'variant_types': [
                {
                    'slug': str,
                    'name': str,
                    'description': str,
                    'is_required': bool,
                    'options': [
                        {'slug': str, 'name': str, 'count': int}
                    ]
                }
            ],
            'status_options': [
                {'value': str, 'label': str, 'count': int}
            ]
        }
    
    Raises:
        ValueError: Si la categoría no existe
    """
    try:
        category = Category.objects.prefetch_related(
            'subcategories',
            'catalog_products__subcategory',
            'catalog_products__price_tiers',
            'catalog_products__product_variant_types__variant_type__options'
        ).get(slug=category_slug)
    except Category.DoesNotExist:
        raise ValueError(f"Categoría no encontrada: {category_slug}")
    
    result = {
        'category': {
            'slug': category.slug,
            'name': category.name,
            'total_products': category.catalog_products.filter(status='active').count()
        },
        'subcategories': [],
        'price_range': {'min': 0.0, 'max': 0.0},
        'variant_types': [],
        'status_options': []
    }
    
    # Subcategorías con conteo de productos
    subcategories = category.subcategories.all()
    for subcat in subcategories:
        product_count = Product.objects.filter(
            subcategory=subcat,
            status='active'
        ).count()
        
        if product_count > 0:
            result['subcategories'].append({
                'slug': subcat.slug,
                'name': subcat.name,
                'count': product_count,
                'description': subcat.description
            })
    
    # Rango de precios
    products = category.catalog_products.filter(status='active')
    if products.exists():
        price_aggregates = PriceTier.objects.filter(
            product__in=products
        ).aggregate(
            min_price=Min('unit_price'),
            max_price=Max('unit_price')
        )
        
        result['price_range'] = {
            'min': float(price_aggregates['min_price'] or 0),
            'max': float(price_aggregates['max_price'] or 0)
        }
    
    # Tipos de variantes disponibles en la categoría
    variant_types_dict = {}
    
    for product in products:
        for pvt in product.product_variant_types.all():
            variant_type = pvt.variant_type
            
            if variant_type.slug not in variant_types_dict:
                variant_types_dict[variant_type.slug] = {
                    'slug': variant_type.slug,
                    'name': variant_type.name,
                    'description': variant_type.description,
                    'is_required': variant_type.is_required,
                    'display_order': variant_type.display_order,
                    'options': {}
                }
            
            # Contar productos por opción
            for option in variant_type.options.all():
                if option.slug not in variant_types_dict[variant_type.slug]['options']:
                    variant_types_dict[variant_type.slug]['options'][option.slug] = {
                        'slug': option.slug,
                        'name': option.name,
                        'count': 0,
                        'additional_price': float(option.additional_price)
                    }
                variant_types_dict[variant_type.slug]['options'][option.slug]['count'] += 1
    
    # Convertir a lista ordenada
    for vt_slug in sorted(variant_types_dict.keys(), 
                         key=lambda x: variant_types_dict[x]['display_order']):
        vt = variant_types_dict[vt_slug]
        vt['options'] = list(vt['options'].values())
        result['variant_types'].append(vt)
    
    # Opciones de estado
    status_counts = products.values('status').annotate(count=Count('slug'))
    for status in status_counts:
        result['status_options'].append({
            'value': status['status'],
            'label': 'Activo' if status['status'] == 'active' else 'Temporal',
            'count': status['count']
        })
    
    return result


def search_products(search_term: str, limit: int = 20) -> QuerySet:
    """
    Búsqueda global de productos
    
    Args:
        search_term: Término de búsqueda
        limit: Número máximo de resultados
    
    Returns:
        QuerySet de productos que coinciden
    """
    queryset = Product.objects.filter(
        Q(name__icontains=search_term) |
        Q(description__icontains=search_term) |
        Q(sku__icontains=search_term) |
        Q(category__name__icontains=search_term) |
        Q(subcategory__name__icontains=search_term),
        status='active'
    ).select_related(
        'category', 'subcategory'
    ).prefetch_related(
        'price_tiers'
    )[:limit]
    
    return queryset


def get_featured_products(category_slug: Optional[str] = None, limit: int = 10) -> QuerySet:
    """
    Obtiene productos destacados, opcionalmente de una categoría específica
    
    Args:
        category_slug: Slug de categoría opcional
        limit: Número máximo de productos
    
    Returns:
        QuerySet de productos
    """
    queryset = Product.objects.filter(status='active')
    
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)
    
    # Ordenar por productos con más variantes (más complejos/personalizables)
    queryset = queryset.annotate(
        variant_count=Count('product_variant_types')
    ).order_by('-variant_count', 'name')
    
    return queryset.select_related(
        'category', 'subcategory'
    ).prefetch_related('price_tiers')[:limit]


def get_products_with_variant_option(
    variant_option_slug: str,
    category_slug: Optional[str] = None
) -> QuerySet:
    """
    Obtiene productos que tienen una opción de variante específica
    
    Args:
        variant_option_slug: Slug de la opción de variante
        category_slug: Slug de categoría opcional para filtrar
    
    Returns:
        QuerySet de productos
    
    Raises:
        ValueError: Si la opción de variante no existe
    """
    try:
        option = VariantOption.objects.select_related('variant_type').get(
            slug=variant_option_slug
        )
    except VariantOption.DoesNotExist:
        raise ValueError(f"Opción de variante no encontrada: {variant_option_slug}")
    
    queryset = Product.objects.filter(
        product_variant_types__variant_type=option.variant_type,
        status='active'
    )
    
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)
    
    return queryset.select_related(
        'category', 'subcategory'
    ).prefetch_related('price_tiers').distinct()


def get_similar_products(product_slug: str, limit: int = 5) -> QuerySet:
    """
    Obtiene productos similares basándose en categoría y variantes
    
    Args:
        product_slug: Slug del producto de referencia
        limit: Número máximo de productos similares
    
    Returns:
        QuerySet de productos similares
    
    Raises:
        ValueError: Si el producto no existe
    """
    try:
        product = Product.objects.prefetch_related(
            'product_variant_types__variant_type'
        ).get(slug=product_slug)
    except Product.DoesNotExist:
        raise ValueError(f"Producto no encontrado: {product_slug}")
    
    # Obtener variantes del producto
    variant_types = [
        pvt.variant_type 
        for pvt in product.product_variant_types.all()
    ]
    
    # Buscar productos de la misma categoría/subcategoría con variantes similares
    similar = Product.objects.filter(
        category=product.category,
        status='active'
    ).exclude(
        slug=product_slug
    ).prefetch_related(
        'product_variant_types__variant_type'
    )
    
    # Priorizar productos de la misma subcategoría
    if product.subcategory:
        similar = similar.filter(subcategory=product.subcategory)
    
    # Anotar con número de variantes en común
    similar = similar.annotate(
        common_variants=Count(
            'product_variant_types',
            filter=Q(product_variant_types__variant_type__in=variant_types)
        )
    ).order_by('-common_variants', 'name')
    
    return similar.select_related(
        'category', 'subcategory'
    ).prefetch_related('price_tiers')[:limit]


def get_categories_with_product_count() -> List[Dict]:
    """
    Obtiene todas las categorías con conteo de productos activos
    
    Returns:
        Lista de dicts con información de categorías:
        [
            {
                'slug': str,
                'name': str,
                'description': str,
                'image_url': str,
                'display_order': int,
                'status': str,
                'product_count': int,
                'subcategory_count': int
            }
        ]
    """
    categories = Category.objects.prefetch_related(
        'catalog_products',
        'subcategories'
    ).annotate(
        product_count=Count('catalog_products', filter=Q(catalog_products__status='active'))
    ).order_by('display_order', 'name')
    
    result = []
    for category in categories:
        if category.product_count > 0:  # Solo incluir categorías con productos
            result.append({
                'slug': category.slug,
                'name': category.name,
                'description': category.description,
                'image_url': category.image_url,
                'display_order': category.display_order,
                'status': category.status,
                'product_count': category.product_count,
                'subcategory_count': category.subcategories.count()
            })
    
    return result
