"""
Servicios para el sistema de catálogo personalizable
"""
from .pricing_service import (
    calculate_product_price,
    get_available_variants,
    validate_product_configuration,
    get_price_tiers,
    get_price_estimate,
    compare_configurations
)

from .filter_service import (
    get_products_by_category,
    get_products_by_subcategory,
    apply_filters,
    get_filter_options_for_category,
    search_products,
    get_featured_products,
    get_products_with_variant_option,
    get_similar_products,
    get_categories_with_product_count
)

__all__ = [
    # Pricing services
    'calculate_product_price',
    'get_available_variants',
    'validate_product_configuration',
    'get_price_tiers',
    'get_price_estimate',
    'compare_configurations',
    # Filter services
    'get_products_by_category',
    'get_products_by_subcategory',
    'apply_filters',
    'get_filter_options_for_category',
    'search_products',
    'get_featured_products',
    'get_products_with_variant_option',
    'get_similar_products',
    'get_categories_with_product_count',
]
