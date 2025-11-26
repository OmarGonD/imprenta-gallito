"""
Vistas Django para el sistema de catálogo personalizable

MIGRATION NOTE (2024):
- Now imports Category, Subcategory, CatalogProduct from shop.models
- Previously imported from catalog_models.py (deprecated)
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from decimal import Decimal
import json

# Import from models.py (migrated from catalog_models.py)
from .models import Category, Subcategory, Product
from .services import (
    get_categories_with_product_count,
    get_products_by_category,
    get_filter_options_for_category,
    search_products,
    get_featured_products,
    get_similar_products,
    calculate_product_price,
    get_available_variants,
    validate_product_configuration,
    get_price_tiers
)


def catalog_home(request):
    """
    Vista principal del catálogo
    Muestra todas las categorías con conteo de productos
    """
    categories = get_categories_with_product_count()
    featured_products = get_featured_products(limit=8)
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'page_title': 'Catálogo de Productos Personalizables'
    }
    
    return render(request, 'catalog/catalog_home.html', context)


def category_view(request, category_slug):
    """
    Vista de categoría
    Muestra productos de una categoría con filtros
    """
    category = get_object_or_404(Category, slug=category_slug)
    
    # Obtener filtros de la URL
    filters = {}
    if request.GET.get('subcategory'):
        filters['subcategory'] = request.GET.get('subcategory')
    if request.GET.get('search'):
        filters['search'] = request.GET.get('search')
    if request.GET.get('min_price'):
        filters['min_price'] = float(request.GET.get('min_price'))
    if request.GET.get('max_price'):
        filters['max_price'] = float(request.GET.get('max_price'))
    
    # Obtener productos con filtros
    products = get_products_by_category(category_slug, filters if filters else None)
    
    # Obtener opciones de filtro disponibles
    filter_options = get_filter_options_for_category(category_slug)
    
    # Paginación
    paginator = Paginator(products, 12)  # 12 productos por página
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,
        'filter_options': filter_options,
        'current_filters': filters,
        'page_title': category.name
    }
    
    return render(request, 'catalog/category.html', context)


def subcategory_view(request, category_slug, subcategory_slug):
    """
    Vista de subcategoría
    Muestra productos de una subcategoría específica
    Soporta HTMX para cargas dinámicas
    """
    subcategory = get_object_or_404(Subcategory, slug=subcategory_slug)
    category = subcategory.category
    
    products = subcategory.catalog_products.filter(status='active').select_related(
        'category', 'subcategory'
    ).prefetch_related('price_tiers')
    
    # Check if this is an HTMX request
    is_htmx = request.GET.get('htmx') == '1' or request.headers.get('HX-Request')
    
    if is_htmx:
        # Return only the products grid for HTMX requests (limit to 6 products)
        products_limited = products[:6]
        context = {
            'category': category,
            'subcategory': subcategory,
            'products': products_limited,
        }
        return render(request, 'catalog/_products_grid.html', context)
    
    # Regular request - full page with pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'subcategory': subcategory,
        'products': page_obj,
        'page_title': f'{category.name} - {subcategory.name}'
    }
    
    return render(request, 'catalog/subcategory.html', context)


def product_detail(request, category_slug, product_slug):
    """
    Vista de detalle de producto
    Muestra información completa del producto con configurador
    """
    product = get_object_or_404(
        Product.objects.select_related('category', 'subcategory').prefetch_related(
            'price_tiers',
            'product_variant_types__variant_type__options'
        ),
        slug=product_slug
    )
    
    # Obtener variantes disponibles
    variants = get_available_variants(product_slug)
    
    # Obtener tiers de precio
    price_tiers = get_price_tiers(product_slug)
    
    # Obtener productos similares
    similar_products = get_similar_products(product_slug, limit=4)
    
    # Cantidad inicial predeterminada
    default_quantity = price_tiers[0]['min_quantity'] if price_tiers else 1
    
    context = {
        'product': product,
        'variants': variants,
        'price_tiers': price_tiers,
        'similar_products': similar_products,
        'default_quantity': default_quantity,
        'page_title': product.name
    }
    
    return render(request, 'catalog/product_detail.html', context)


@require_http_methods(["POST"])
def calculate_price_ajax(request):
    """
    API endpoint para calcular precio en tiempo real
    """
    try:
        data = json.loads(request.body)
        product_slug = data.get('product_slug')
        quantity = int(data.get('quantity', 1))
        selected_options = data.get('selected_options', [])
        
        # Calcular precio
        price_info = calculate_product_price(
            product_slug=product_slug,
            quantity=quantity,
            selected_options=selected_options
        )
        
        # Convertir Decimals a float para JSON
        price_info['base_price'] = float(price_info['base_price'])
        price_info['additional_cost'] = float(price_info['additional_cost'])
        price_info['unit_price'] = float(price_info['unit_price'])
        price_info['subtotal'] = float(price_info['subtotal'])
        price_info['total_price'] = float(price_info['total_price'])
        price_info['savings'] = float(price_info['savings'])
        
        return JsonResponse({
            'success': True,
            'price_info': price_info
        })
    
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al calcular precio: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def validate_configuration_ajax(request):
    """
    API endpoint para validar configuración de producto
    """
    try:
        data = json.loads(request.body)
        product_slug = data.get('product_slug')
        selected_options = data.get('selected_options', [])
        
        # Validar configuración
        validation = validate_product_configuration(
            product_slug=product_slug,
            selected_options=selected_options
        )
        
        return JsonResponse({
            'success': True,
            'validation': validation
        })
    
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al validar configuración: {str(e)}'
        }, status=500)


def catalog_search(request):
    """
    Vista de búsqueda en el catálogo
    """
    search_term = request.GET.get('q', '').strip()
    
    if len(search_term) < 3:
        context = {
            'search_term': search_term,
            'products': [],
            'message': 'Por favor ingrese al menos 3 caracteres para buscar',
            'page_title': 'Búsqueda en Catálogo'
        }
        return render(request, 'catalog/search.html', context)
    
    # Buscar productos
    results = search_products(search_term, limit=50)
    
    # Paginación
    paginator = Paginator(results, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'search_term': search_term,
        'products': page_obj,
        'total_results': results.count() if hasattr(results, 'count') else len(results),
        'page_title': f'Resultados para "{search_term}"'
    }
    
    return render(request, 'catalog/search.html', context)


@require_http_methods(["GET"])
def get_product_variants_ajax(request, product_slug):
    """
    API endpoint para obtener variantes de un producto
    """
    try:
        variants = get_available_variants(product_slug)
        
        return JsonResponse({
            'success': True,
            'variants': variants
        })
    
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener variantes: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def get_price_tiers_ajax(request, product_slug):
    """
    API endpoint para obtener tiers de precio de un producto
    """
    try:
        tiers = get_price_tiers(product_slug)
        
        return JsonResponse({
            'success': True,
            'tiers': tiers
        })
    
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener precios: {str(e)}'
        }, status=500)
