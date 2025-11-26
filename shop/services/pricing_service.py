"""
Servicio de cálculo de precios para productos personalizables del catálogo
Maneja precios dinámicos con descuentos por volumen y costos adicionales por variantes

MIGRATION NOTE (2024):
- Now imports Product, VariantType, VariantOption, PriceTier from shop.models
- Previously imported from catalog_models.py (deprecated)
"""
from decimal import Decimal
from typing import List, Dict, Optional
from django.db.models import Q

# Import from models.py (migrated from catalog_models.py)
from shop.models import (
    Product,
    VariantType,
    VariantOption,
    PriceTier
)


def calculate_product_price(
    product_slug: str,
    quantity: int,
    selected_options: List[str]
) -> Dict:
    """
    Calcula el precio final de un producto con variantes seleccionadas
    
    Args:
        product_slug: Slug del producto
        quantity: Cantidad a comprar
        selected_options: Lista de slugs de opciones seleccionadas
    
    Returns:
        Dict con información detallada del precio:
        {
            'product_name': str,
            'product_slug': str,
            'sku': str,
            'quantity': int,
            'base_price': Decimal,           # Precio base sin opciones
            'additional_cost': Decimal,       # Costo de todas las opciones
            'unit_price': Decimal,            # Precio por unidad con opciones
            'subtotal': Decimal,              # base_price * quantity
            'total_price': Decimal,           # Precio final total
            'discount_percentage': int,       # % de descuento aplicado
            'savings': Decimal,               # Ahorro total
            'options_selected': List[Dict],   # Detalles de opciones seleccionadas
            'tier_range': str,                # Rango de cantidades del tier
            'valid': bool,                    # Si la configuración es válida
            'errors': List[str]               # Lista de errores si no es válida
        }
    
    Raises:
        ValueError: Si el producto no existe
    """
    try:
        product = Product.objects.prefetch_related(
            'price_tiers',
            'product_variant_types__variant_type'
        ).get(slug=product_slug)
    except Product.DoesNotExist:
        raise ValueError(f"Producto no encontrado: {product_slug}")
    
    # Inicializar resultado
    result = {
        'product_name': product.name,
        'product_slug': product.slug,
        'sku': product.sku,
        'quantity': quantity,
        'base_price': Decimal('0.00'),
        'additional_cost': Decimal('0.00'),
        'unit_price': Decimal('0.00'),
        'subtotal': Decimal('0.00'),
        'total_price': Decimal('0.00'),
        'discount_percentage': 0,
        'savings': Decimal('0.00'),
        'options_selected': [],
        'tier_range': '',
        'valid': True,
        'errors': []
    }
    
    # Obtener precio base según cantidad (tier)
    tier = product.price_tiers.filter(
        min_quantity__lte=quantity,
        max_quantity__gte=quantity
    ).first()
    
    if not tier:
        result['valid'] = False
        result['errors'].append(
            f'No hay precios definidos para cantidad {quantity}. '
            f'Intente con una cantidad diferente.'
        )
        return result
    
    result['base_price'] = tier.unit_price
    result['discount_percentage'] = tier.discount_percentage
    result['tier_range'] = tier.get_range_display()
    
    # Procesar opciones seleccionadas
    additional_cost_per_unit = Decimal('0.00')
    
    if selected_options:
        options = VariantOption.objects.filter(
            slug__in=selected_options
        ).select_related('variant_type')
        
        for option in options:
            additional_cost_per_unit += option.additional_price
            result['options_selected'].append({
                'type': option.variant_type.name,
                'type_slug': option.variant_type.slug,
                'option': option.name,
                'option_slug': option.slug,
                'cost': float(option.additional_price),
                'image_url': option.image_url
            })
    
    result['additional_cost'] = additional_cost_per_unit
    result['unit_price'] = result['base_price'] + additional_cost_per_unit
    result['subtotal'] = result['base_price'] * quantity
    result['total_price'] = result['unit_price'] * quantity
    
    # Calcular ahorro si hay descuento
    if result['discount_percentage'] > 0:
        # Calcular precio sin descuento (primer tier)
        first_tier = product.price_tiers.order_by('min_quantity').first()
        if first_tier:
            original_unit_price = first_tier.unit_price + additional_cost_per_unit
            original_total = original_unit_price * quantity
            result['savings'] = original_total - result['total_price']
    
    return result


def get_available_variants(product_slug: str) -> Dict:
    """
    Obtiene todas las variantes disponibles para un producto
    
    Args:
        product_slug: Slug del producto
    
    Returns:
        Dict con tipos de variantes y sus opciones:
        {
            'variant_type_slug': {
                'name': str,
                'description': str,
                'is_required': bool,
                'allows_multiple': bool,
                'display_order': int,
                'options': [
                    {
                        'option_slug': str,
                        'option_name': str,
                        'description': str,
                        'additional_price': float,
                        'image_url': str,
                        'display_order': int
                    }
                ]
            }
        }
    
    Raises:
        ValueError: Si el producto no existe
    """
    try:
        product = Product.objects.prefetch_related(
            'product_variant_types__variant_type__options'
        ).get(slug=product_slug)
    except Product.DoesNotExist:
        raise ValueError(f"Producto no encontrado: {product_slug}")
    
    variants_dict = {}
    
    # Obtener tipos de variantes asociados al producto
    for pvt in product.product_variant_types.all():
        variant_type = pvt.variant_type
        
        # Obtener opciones del tipo de variante
        options = []
        for option in variant_type.options.all():
            options.append({
                'option_slug': option.slug,
                'option_name': option.name,
                'description': option.description,
                'additional_price': float(option.additional_price),
                'has_additional_cost': option.has_additional_cost(),
                'image_url': option.image_url,
                'display_order': option.display_order
            })
        
        variants_dict[variant_type.slug] = {
            'name': variant_type.name,
            'description': variant_type.description,
            'is_required': variant_type.is_required,
            'allows_multiple': variant_type.allows_multiple,
            'display_order': variant_type.display_order,
            'applies_to': variant_type.applies_to,
            'options': options
        }
    
    return variants_dict


def validate_product_configuration(
    product_slug: str,
    selected_options: List[str]
) -> Dict:
    """
    Valida que la configuración seleccionada sea válida
    
    Args:
        product_slug: Slug del producto
        selected_options: Lista de slugs de opciones seleccionadas
    
    Returns:
        Dict con resultado de validación:
        {
            'valid': bool,
            'errors': List[str],        # Errores que impiden la compra
            'warnings': List[str],      # Advertencias opcionales
            'missing_required': List[Dict],  # Variantes requeridas faltantes
            'invalid_options': List[str]     # Opciones que no aplican al producto
        }
    
    Raises:
        ValueError: Si el producto no existe
    """
    try:
        product = Product.objects.prefetch_related(
            'product_variant_types__variant_type__options'
        ).get(slug=product_slug)
    except Product.DoesNotExist:
        raise ValueError(f"Producto no encontrado: {product_slug}")
    
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'missing_required': [],
        'invalid_options': []
    }
    
    # Obtener variantes del producto
    product_variant_types = {
        pvt.variant_type.slug: pvt.variant_type 
        for pvt in product.product_variant_types.all()
    }
    
    # Mapear opciones seleccionadas por tipo de variante
    selected_by_type = {}
    if selected_options:
        options = VariantOption.objects.filter(
            slug__in=selected_options
        ).select_related('variant_type')
        
        for option in options:
            variant_type_slug = option.variant_type.slug
            
            # Verificar que la opción aplique al producto
            if variant_type_slug not in product_variant_types:
                result['invalid_options'].append(option.slug)
                result['errors'].append(
                    f'La opción "{option.name}" no está disponible para este producto'
                )
                result['valid'] = False
                continue
            
            if variant_type_slug not in selected_by_type:
                selected_by_type[variant_type_slug] = []
            selected_by_type[variant_type_slug].append(option)
    
    # Verificar variantes requeridas
    for variant_type_slug, variant_type in product_variant_types.items():
        if variant_type.is_required:
            if variant_type_slug not in selected_by_type:
                result['missing_required'].append({
                    'type_slug': variant_type_slug,
                    'type_name': variant_type.name,
                    'description': variant_type.description
                })
                result['errors'].append(
                    f'Debe seleccionar una opción para: {variant_type.name}'
                )
                result['valid'] = False
        
        # Verificar allows_multiple
        if variant_type_slug in selected_by_type:
            selected_count = len(selected_by_type[variant_type_slug])
            if selected_count > 1 and not variant_type.allows_multiple:
                result['errors'].append(
                    f'Solo puede seleccionar una opción para: {variant_type.name}'
                )
                result['valid'] = False
    
    return result


def get_price_tiers(product_slug: str) -> List[Dict]:
    """
    Obtiene todos los niveles de precio para un producto
    
    Args:
        product_slug: Slug del producto
    
    Returns:
        Lista de tiers de precio:
        [
            {
                'min_quantity': int,
                'max_quantity': int,
                'unit_price': float,
                'discount_percentage': int,
                'range_display': str,
                'savings_vs_first': float  # Ahorro vs primer tier
            }
        ]
    
    Raises:
        ValueError: Si el producto no existe
    """
    try:
        product = Product.objects.prefetch_related('price_tiers').get(
            slug=product_slug
        )
    except Product.DoesNotExist:
        raise ValueError(f"Producto no encontrado: {product_slug}")
    
    tiers = []
    first_tier_price = None
    
    for tier in product.price_tiers.all():
        if first_tier_price is None:
            first_tier_price = tier.unit_price
        
        savings = float(first_tier_price - tier.unit_price) if first_tier_price else 0.0
        
        tiers.append({
            'min_quantity': tier.min_quantity,
            'max_quantity': tier.max_quantity,
            'unit_price': float(tier.unit_price),
            'discount_percentage': tier.discount_percentage,
            'range_display': tier.get_range_display(),
            'savings_vs_first': savings,
            'total_savings_percentage': int((savings / float(first_tier_price)) * 100) if first_tier_price and first_tier_price > 0 else 0
        })
    
    return tiers


def get_price_estimate(
    product_slug: str,
    quantity: int
) -> Dict:
    """
    Obtiene una estimación rápida de precio sin opciones
    
    Args:
        product_slug: Slug del producto
        quantity: Cantidad
    
    Returns:
        Dict con estimación:
        {
            'base_price': float,
            'total': float,
            'discount_percentage': int,
            'tier_range': str
        }
    """
    try:
        product = Product.objects.get(slug=product_slug)
    except Product.DoesNotExist:
        raise ValueError(f"Producto no encontrado: {product_slug}")
    
    tier = product.price_tiers.filter(
        min_quantity__lte=quantity,
        max_quantity__gte=quantity
    ).first()
    
    if not tier:
        return {
            'base_price': 0.0,
            'total': 0.0,
            'discount_percentage': 0,
            'tier_range': 'N/A',
            'error': f'No hay precios para cantidad {quantity}'
        }
    
    return {
        'base_price': float(tier.unit_price),
        'total': float(tier.unit_price * quantity),
        'discount_percentage': tier.discount_percentage,
        'tier_range': tier.get_range_display()
    }


def compare_configurations(
    product_slug: str,
    quantity: int,
    config1: List[str],
    config2: List[str]
) -> Dict:
    """
    Compara dos configuraciones diferentes del mismo producto
    
    Args:
        product_slug: Slug del producto
        quantity: Cantidad
        config1: Primera lista de opciones
        config2: Segunda lista de opciones
    
    Returns:
        Dict con comparación:
        {
            'config1': Dict,  # Resultado de calculate_product_price
            'config2': Dict,  # Resultado de calculate_product_price
            'price_difference': float,
            'cheaper_config': int  # 1 o 2
        }
    """
    price1 = calculate_product_price(product_slug, quantity, config1)
    price2 = calculate_product_price(product_slug, quantity, config2)
    
    diff = float(price2['total_price'] - price1['total_price'])
    
    return {
        'config1': price1,
        'config2': price2,
        'price_difference': abs(diff),
        'cheaper_config': 1 if diff > 0 else 2,
        'percentage_difference': abs(int((diff / float(price1['total_price'])) * 100)) if price1['total_price'] > 0 else 0
    }
