"""
URLs para el sistema de catálogo personalizable
"""
from django.urls import path
from . import catalog_views

app_name = 'catalog'

urlpatterns = [
    # Vista principal del catálogo
    path('', catalog_views.catalog_home, name='home'),
    
    # Búsqueda
    path('buscar/', catalog_views.catalog_search, name='search'),
    
    # Categoría
    path('<slug:category_slug>/', catalog_views.category_view, name='category'),
    
    # Subcategoría
    path('<slug:category_slug>/<slug:subcategory_slug>/', 
         catalog_views.subcategory_view, name='subcategory'),
    
    # Detalle de producto
    path('<slug:category_slug>/producto/<slug:product_slug>/', 
         catalog_views.product_detail, name='product_detail'),
    
    # API AJAX endpoints
    path('api/calculate-price/', catalog_views.calculate_price_ajax, name='calculate_price_ajax'),
    path('api/validate-config/', catalog_views.validate_configuration_ajax, name='validate_config_ajax'),
    path('api/product/<slug:product_slug>/variants/', 
         catalog_views.get_product_variants_ajax, name='get_variants_ajax'),
    path('api/product/<slug:product_slug>/price-tiers/', 
         catalog_views.get_price_tiers_ajax, name='get_price_tiers_ajax'),
]
