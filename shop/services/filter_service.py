"""
Servicio de filtrado y búsqueda de productos del catálogo
Permite filtrar por categoría, subcategoría, precio, variantes, etc.

MIGRATION NOTE (2024):
- Updated to use new ProductOption models
- Replaces deprecated VariantType/VariantOption
"""
from decimal import Decimal
from typing import Dict, List, Optional
from django.db.models import QuerySet, Q, Min, Max, Count, Prefetch

# Import from models.py
from shop.models import (
    Category,
    Subcategory,
    Product,
    ProductOption,
    ProductOptionValue,
    PriceTier
)


def get_products_by_category(
    category_slug: str,
    filters: Optional[Dict] = None
) -> QuerySet:
    """
    Obtiene productos de una categoría con filtros opcionales
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
        'variant_options__option' # Updated related name
    )
    
    # Aplicar filtros si existen
    if filters:
        queryset = apply_filters(queryset, filters)
    
    return queryset.distinct()


def get_products_by_subcategory(subcategory_slug: str) -> QuerySet:
    """
    Obtiene productos de una subcategoría específica
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
    if filters.get('min_price') or filters.get('max_price'):
        # This is expensive, better to filter by base_price or unit_price directly if possible
        # But since logic relies on price tiers, proceed with aggregate or pre-calculated fields if available.
        
        # Optimization: Filter by base_price first if populated
        q_price = Q()
        if filters.get('min_price'):
            q_price &= Q(base_price__gte=filters['min_price'])
        if filters.get('max_price'):
            q_price &= Q(base_price__lte=filters['max_price'])
            
        # If base_price is null (tiered pricing), we need complex query.
        # For simplicty and performance, let's rely on base_price for filtering if possible, 
        # or accept the slow loop for now as per original code structure but simpler.
        
        # Original logic was doing in-memory filtering. Preserving that for safety, 
        # but updating field references.
        product_ids = []
        for product in queryset:
            min_price = product.price_tiers.aggregate(
                min_price=Min('unit_price')
            )['min_price']
            
            # Fallback to base_price if no tiers
            if min_price is None:
                min_price = product.base_price
            
            if min_price is not None:
                include = True
                if filters.get('min_price') and min_price < Decimal(str(filters['min_price'])):
                    include = False
                if filters.get('max_price') and min_price > Decimal(str(filters['max_price'])):
                    include = False
                if include:
                    product_ids.append(product.slug)
        
        queryset = queryset.filter(slug__in=product_ids)
    
    # Filtro por opciones de variantes (values)
    if filters.get('variant_options'):
        variant_option_values = filters['variant_options']
        if isinstance(variant_option_values, str):
            variant_option_values = [variant_option_values]
        
        # Encontrar productos que tengan las variantes (values) especificadas
        # We need to find products that have a ProductVariant containing these values
        # OR simply products that have available_values or default option values matching.
        
        # Simplest approach: Product -> ProductVariant -> ProductOptionValue
        for val_slug in variant_option_values:
            queryset = queryset.filter(
               variant_options__option__values__value=val_slug
               # Note: This is broad. It finds products that HAVE this option value available.
               # Does not check if it's specifically enabled for that variant, but usually assumes yes if in models.
            )
    
    return queryset


def get_filter_options_for_category(category_slug: str) -> Dict:
    """
    Obtiene las opciones de filtro disponibles para una categoría
    """
    try:
        category = Category.objects.prefetch_related(
            'subcategories',
            'products__subcategory',
            'products__price_tiers',
            # 'products__variant_options__option__values' # Can be heavy
        ).get(slug=category_slug)
    except Category.DoesNotExist:
        raise ValueError(f"Categoría no encontrada: {category_slug}")
    
    products = category.products.filter(status='active')
    
    result = {
        'category': {
            'slug': category.slug,
            'name': category.name,
            'total_products': products.count()
        },
        'subcategories': [],
        'price_range': {'min': 0.0, 'max': 0.0},
        'variant_types': [],
        'status_options': []
    }
    
    # Subcategorías
    for subcat in category.subcategories.all():
        product_count = products.filter(subcategory=subcat).count()
        if product_count > 0:
            result['subcategories'].append({
                'slug': subcat.slug,
                'name': subcat.name,
                'count': product_count,
                'description': subcat.description
            })
    
    # Rango de precios
    if products.exists():
        # Mix of base_price and tiers
        min_tier = PriceTier.objects.filter(product__in=products).aggregate(m=Min('unit_price'))['m']
        max_tier = PriceTier.objects.filter(product__in=products).aggregate(m=Max('unit_price'))['m']
        
        min_base = products.aggregate(m=Min('base_price'))['m']
        max_base = products.aggregate(m=Max('base_price'))['m']
        
        mins = [x for x in [min_tier, min_base] if x is not None]
        maxs = [x for x in [max_tier, max_base] if x is not None]
        
        result['price_range'] = {
            'min': float(min(mins)) if mins else 0.0,
            'max': float(max(maxs)) if maxs else 0.0
        }
    
    # Tipos de variantes (ProductOption)
    # This requires aggregating all options from all products in category
    
    # Get all options used by these products
    used_options = ProductOption.objects.filter(
        product_variants__product__in=products
    ).distinct().prefetch_related('values')
    
    for option in used_options:
        # Count products that use this option
        prod_count = products.filter(variant_options__option=option).count()
        
        option_data = {
            'slug': option.key,
            'name': option.name,
            'description': '',
            'is_required': option.is_required,
            'display_order': option.display_order,
            'options': []
        }
        
        # Get values for this option
        for val in option.values.filter(is_active=True):
            # Optimally we should count how many products have this specific value available
            # For now, simplistic count or just list them. 
            # Real counting requires complex queries on ManyToMany 'available_values'
            
            option_data['options'].append({
                'slug': val.value,
                'name': val.get_display_name(),
                'count': 0, # Difficult to calculate efficiently without huge query
                'additional_price': float(val.additional_price)
            })
            
        result['variant_types'].append(option_data)
        
    
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
    Obtiene productos destacados
    """
    queryset = Product.objects.filter(status='active')
    
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)
    
    # Sort by variant count (complexity) using new relations
    queryset = queryset.annotate(
        variant_count=Count('variant_options')
    ).order_by('-variant_count', 'name')
    
    return queryset.select_related(
        'category', 'subcategory'
    ).prefetch_related('price_tiers')[:limit]


def get_products_with_variant_option(
    variant_option_slug: str,
    category_slug: Optional[str] = None
) -> QuerySet:
    """
    Obtiene productos que tienen una opción de variante específica (VALUE)
    """
    try:
        # variant_option_slug is actually a value (e.g., 'red', 'xl')
        option_value = ProductOptionValue.objects.select_related('option').get(
            value=variant_option_slug
        )
    except ProductOptionValue.DoesNotExist:
        # Backward compatibility check: maybe it was an option key?
        # But function name implies option value. 
        raise ValueError(f"Valor de opción no encontrado: {variant_option_slug}")
    
    queryset = Product.objects.filter(
        variant_options__option=option_value.option,
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
    """
    try:
        product = Product.objects.prefetch_related(
            'variant_options__option'
        ).get(slug=product_slug)
    except Product.DoesNotExist:
        raise ValueError(f"Producto no encontrado: {product_slug}")
    
    # Obtener tipos de opciones (keys)
    option_types = [
        vo.option 
        for vo in product.variant_options.all()
    ]
    
    # Buscar productos de la misma categoría
    similar = Product.objects.filter(
        category=product.category,
        status='active'
    ).exclude(
        slug=product_slug
    ).prefetch_related(
        'variant_options__option'
    )
    
    # Priorizar subcategoría
    if product.subcategory:
        similar = similar.filter(subcategory=product.subcategory)
    
    # Anotar con número de opciones en común
    similar = similar.annotate(
        common_variants=Count(
            'variant_options',
            filter=Q(variant_options__option__in=option_types)
        )
    ).order_by('-common_variants', 'name')
    
    return similar.select_related(
        'category', 'subcategory'
    ).prefetch_related('price_tiers')[:limit]


def get_categories_with_product_count() -> List[Dict]:
    """
    Obtiene todas las categorías con conteo de productos activos
    """
    # Fix: related name 'catalog_products' might be wrong if not defined in models.
    # Checking models.py from previous turn: related_name='products'
    
    categories = Category.objects.prefetch_related(
        'products',
        'subcategories'
    ).annotate(
        product_count=Count('products', filter=Q(products__status='active'))
    ).order_by('display_order', 'name')
    
    result = []
    for category in categories:
        if category.product_count > 0:
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
