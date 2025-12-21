"""
Servicio de cálculo de precios para productos personalizables del catálogo
Maneja precios dinámicos con descuentos por volumen y costos adicionales por variantes

MIGRATION NOTE (2024):
- Updated to use ProductOption and ProductOptionValue from shop.models
- Replaces deprecated VariantType/VariantOption
"""
from decimal import Decimal
from typing import List, Dict, Optional
from django.db.models import Q

# Import from models.py
from shop.models import (
    Product,
    ProductOption,
    ProductOptionValue,
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
        selected_options: Lista de values (slugs) de opciones seleccionadas
    
    Returns:
        Dict con información detallada del precio
    """
    try:
        product = Product.objects.prefetch_related(
            'price_tiers',
            'variant_options__option' # Updated related name
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
        # Fallback logic or error? 
        # For now, if no tier matches exact range, try finding closest or just error out.
        # But usually we want at least one tier.
        
        # Try finding the highest tier that is less than quantity if open-ended?
        # The filter logic `max_quantity__gte=quantity` handles ranges.
        # If open ended max is 999999, it covers it.
        
        result['valid'] = False
        result['errors'].append(
            f'No hay precios definidos para cantidad {quantity}. '
            f'Intente con una cantidad diferente.'
        )
        # If invalid, still might want base info
        first_tier = product.price_tiers.order_by('min_quantity').first()
        if first_tier:
             result['base_price'] = first_tier.unit_price
        
        return result
    
    result['base_price'] = tier.unit_price
    result['discount_percentage'] = tier.discount_percentage
    result['tier_range'] = tier.get_range_display()
    
    # Procesar opciones seleccionadas
    additional_cost_per_unit = Decimal('0.00')
    
    if selected_options:
        # ProductOptionValue uses 'value' instead of 'slug'
        options = ProductOptionValue.objects.filter(
            value__in=selected_options
        ).select_related('option')
        
        for option_val in options:
            additional_cost_per_unit += option_val.additional_price
            
            # Handle image url safely
            img_url = option_val.image.url if option_val.image else None
            
            result['options_selected'].append({
                'type': option_val.option.name,
                'type_slug': option_val.option.key, # key is the slug equivalent
                'option': option_val.get_display_name(),
                'option_slug': option_val.value, # value is the slug equivalent
                'cost': float(option_val.additional_price),
                'image_url': img_url
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
    """
    try:
        product = Product.objects.prefetch_related(
            'variant_options__option__values', # New path
            'variant_options__available_values'
        ).get(slug=product_slug)
    except Product.DoesNotExist:
        raise ValueError(f"Producto no encontrado: {product_slug}")
    
    variants_dict = {}
    
    # Use the product's method to get variants if possible, or reconstruct manually
    # Reconstruction to match expected dict output:
    
    for variant in product.variant_options.all().order_by('display_order'):
        option_type = variant.option
        
        # Get values available for this specific product variant
        values_qs = variant.get_available_values()
        
        options_list = []
        for val in values_qs:
            img_url = val.image.url if val.image else None
            options_list.append({
                'option_slug': val.value,
                'option_name': val.get_display_name(),
                'description': '', # OptionValue doesn't have description
                'additional_price': float(val.additional_price),
                'has_additional_cost': val.has_additional_cost(),
                'image_url': img_url,
                'display_order': val.display_order
            })
        
        variants_dict[option_type.key] = {
            'name': option_type.name,
            'description': '', # ProductOption doesn't have description
            'is_required': option_type.is_required,
            'allows_multiple': option_type.selection_type == 'multiple',
            'display_order': variant.display_order, # Use variant display order
            'applies_to': 'all', # Default or deprecated
            'options': options_list
        }
    
    return variants_dict


def validate_product_configuration(
    product_slug: str,
    selected_options: List[str]
) -> Dict:
    """
    Valida que la configuración seleccionada sea válida
    """
    try:
        product = Product.objects.prefetch_related(
            'variant_options__option'
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
    
    # Map valid options for this product
    valid_option_keys = {
        variant.option.key: variant.option
        for variant in product.variant_options.all()
    }
    
    # Process selected options
    selected_by_type = {}
    
    if selected_options:
        # Filter by value
        options = ProductOptionValue.objects.filter(
            value__in=selected_options
        ).select_related('option')
        
        for option_val in options:
            option_key = option_val.option.key
            
            # Verify if this option applies to the product
            if option_key not in valid_option_keys:
                result['invalid_options'].append(option_val.value)
                result['errors'].append(
                    f'La opción "{option_val.get_display_name()}" no está disponible para este producto'
                )
                result['valid'] = False
                continue
            
            if option_key not in selected_by_type:
                selected_by_type[option_key] = []
            selected_by_type[option_key].append(option_val)

    # Check required options
    for key, option_obj in valid_option_keys.items():
        if option_obj.is_required:
            if key not in selected_by_type:
                result['missing_required'].append({
                    'type_slug': key,
                    'type_name': option_obj.name,
                    'description': ''
                })
                result['errors'].append(
                    f'Debe seleccionar una opción para: {option_obj.name}'
                )
                result['valid'] = False
        
        # Check multiple selection
        if key in selected_by_type:
            selected_count = len(selected_by_type[key])
            if selected_count > 1 and option_obj.selection_type != 'multiple':
                result['errors'].append(
                    f'Solo puede seleccionar una opción para: {option_obj.name}'
                )
                result['valid'] = False
                
    return result


def get_price_tiers(product_slug: str) -> List[Dict]:
    """
    Obtiene todos los niveles de precio para un producto
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
