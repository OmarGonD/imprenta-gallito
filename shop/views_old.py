"""
Shop Views - SISTEMA UNIFICADO
===============================
Todas las vistas usan el sistema Category → Subcategory → Product.
Las vistas de ropa ahora usan los mismos modelos que el resto del catálogo.
"""
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.db import transaction
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import redirect, HttpResponseRedirect, render, get_object_or_404
from django.template.loader import get_template
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings

from shop.models import (
    Profile, Peru, Category, Subcategory, Product, 
    ProductColor, ProductSize, ProductImage,
    TarjetaPresentacion, Folleto, Poster, Etiqueta, Empaque,
    DesignTemplate, PriceTier
)
from shop.tokens import account_activation_token
from cart.models import Cart, CartItem
from .forms import SignUpForm, StepOneForm, StepTwoForm, ProfileForm, StepOneForm_Sample, StepTwoForm_Sample
from marketing.forms import EmailSignUpForm
from shop.utils.pricing import PricingService
from .template_loader import TemplateLoader

import os
import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Min, Prefetch
import json


from .models import (
    Category,
    Subcategory,
    Product,
    ProductColor,
    ProductSize,
    ProductImage,
)

# ============================================================================
# HOME PAGE VIEW
# ============================================================================

def Home(request):
    """
    E-commerce style homepage for Imprenta Gallito
    """
    popular_categories = []
    new_products = []
    special_offers = []
    
    try:
        from django.db import connection
        table_names = connection.introspection.table_names()
        has_categories = 'categories' in table_names or 'shop_category' in table_names
        has_products = 'products' in table_names or 'shop_product' in table_names
    except:
        has_categories = False
        has_products = False
    
    if has_categories:
        try:
            popular_categories = list(Category.objects.filter(
                status='active'
            ).prefetch_related('subcategories').order_by('display_order')[:6])
        except Exception as e:
            print(f"Error loading categories: {e}")
            popular_categories = []
    
    if has_categories and has_products and popular_categories:
        try:
            new_products = list(Product.objects.filter(
                status='active'
            ).select_related('category').order_by('-created_at')[:6])
        except Exception as e:
            print(f"Error loading new products: {e}")
            new_products = []
    
    if has_categories and has_products and popular_categories:
        try:
            special_offers = list(Product.objects.filter(
                status='active'
            ).select_related('category').order_by('?')[:4])
        except Exception as e:
            print(f"Error loading special offers: {e}")
            special_offers = []
    
    hero_banners = []
    
    testimonials = [
        {
            'name': 'María García',
            'company': 'Café Peruano',
            'text': 'Excelente calidad en los stickers para nuestros productos.',
            'rating': 5,
            'avatar': 'MG',
        },
        {
            'name': 'Carlos Mendoza',
            'company': 'Tech Solutions',
            'text': 'Las tarjetas de presentación quedaron increíbles.',
            'rating': 5,
            'avatar': 'CM',
        },
        {
            'name': 'Ana Rodríguez',
            'company': 'Boutique Luna',
            'text': 'Los empaques personalizados le dieron un toque especial a nuestra marca.',
            'rating': 5,
            'avatar': 'AR',
        },
    ]
    
    context = {
        'popular_categories': popular_categories,
        'new_products': new_products,
        'special_offers': special_offers,
        'hero_banners': hero_banners,
        'testimonials': testimonials,
    }
    
    return render(request, 'shop/home.html', context)


# ============================================================================
# CATEGORY & SUBCATEGORY VIEWS (Sistema Unificado)
# ============================================================================

def category_view(request, category_slug):
    """
    Vista genérica para mostrar una categoría y sus productos.
    Detecta si la categoría tiene un template personalizado.
    """
    try:
        category = Category.objects.get(slug=category_slug, status='active')
    except Category.DoesNotExist:
        raise Http404("Categoría no encontrada")
    
    # Si la categoría tiene un template personalizado, usarlo
    if category.custom_template:
        # Redirigir a la vista específica según el template
        if 'ropa_bolsos' in category.custom_template:
            return ropa_bolsos(request)
    
    subcategories = category.subcategories.filter(status='active').order_by('display_order')
    
    products = Product.objects.filter(
        category=category,
        status='active'
    ).select_related('category', 'subcategory').prefetch_related('price_tiers', 'available_colors', 'available_sizes')
    
    subcategory_filter = request.GET.get('subcategory', '')
    if subcategory_filter:
        products = products.filter(subcategory__slug=subcategory_filter)
    
    products = products.order_by('subcategory__display_order', 'name')
    
    context = {
        'category': category,
        'subcategories': subcategories,
        'products': products,
        'product_count': products.count(),
        'selected_subcategory': subcategory_filter,
    }
    
    return render(request, 'shop/category.html', context)


def subcategory_view(request, category_slug, subcategory_slug):
    """
    Vista para mostrar una subcategoría y sus productos.
    """
    try:
        category = Category.objects.get(slug=category_slug, status='active')
        subcategory = Subcategory.objects.get(
            category=category,
            slug=subcategory_slug,
            status='active'
        )
    except (Category.DoesNotExist, Subcategory.DoesNotExist):
        raise Http404("Subcategoría no encontrada")
    
    products = Product.objects.filter(
        subcategory=subcategory,
        status='active'
    ).select_related('category', 'subcategory').prefetch_related('price_tiers', 'available_colors', 'available_sizes')
    
    sibling_subcategories = category.subcategories.filter(status='active').order_by('display_order')
    
    # Filtros adicionales para ropa
    color_filter = request.GET.getlist('color')
    size_filter = request.GET.getlist('size')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    sort_by = request.GET.get('sort', 'featured')
    
    if color_filter:
        products = products.filter(available_colors__slug__in=color_filter).distinct()
    
    if size_filter:
        products = products.filter(available_sizes__name__in=size_filter).distinct()
    
    if price_min:
        products = products.filter(base_price__gte=float(price_min))
    
    if price_max:
        products = products.filter(base_price__lte=float(price_max))
    
    # Ordenamiento
    if sort_by == 'price_low':
        products = products.order_by('base_price')
    elif sort_by == 'price_high':
        products = products.order_by('-base_price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-is_featured', '-is_bestseller', 'name')
    
    # Obtener colores y tallas disponibles en esta subcategoría
    all_colors = ProductColor.objects.filter(
        products__subcategory=subcategory, is_active=True
    ).distinct()
    all_sizes = ProductSize.objects.filter(
        products__subcategory=subcategory, is_active=True
    ).distinct()
    
    context = {
        'category': category,
        'subcategory': subcategory,
        'subcategories': sibling_subcategories,  # Para navegación
        'sibling_subcategories': sibling_subcategories,
        'products': products,
        'product_count': products.count(),
        'all_colors': all_colors,
        'all_sizes': all_sizes,
        'selected_colors': color_filter,
        'selected_sizes': size_filter,
        'price_min': price_min,
        'price_max': price_max,
        'sort_by': sort_by,
    }
    
    return render(request, 'shop/subcategory.html', context)


def product_detail_view(request, category_slug, product_slug):
    """
    Vista para mostrar el detalle de un producto.
    Soporta tanto productos de imprenta como ropa.
    """
    try:
        category = Category.objects.get(slug=category_slug, status='active')
        product = Product.objects.get(
            category=category,
            slug=product_slug,
            status='active'
        )
    except (Category.DoesNotExist, Product.DoesNotExist):
        raise Http404("Producto no encontrado")
    
    pricing_service = PricingService()
    all_tiers = pricing_service.price_tiers.get(product.slug, [])
    
    if all_tiers:
        base_price = all_tiers[0]['unit_price']
        for tier in all_tiers:
            tier['savings'] = base_price - tier['unit_price']
    
    variant_types = product.get_available_variant_types()
    
    related_products = Product.objects.filter(
        category=category,
        status='active'
    ).exclude(pk=product.pk)[:4]
    
    # Datos adicionales para productos de ropa
    product_images = product.images.all().order_by('display_order')
    
    context = {
        'category': category,
        'product': product,
        'tiers': all_tiers,
        'variant_types': variant_types,
        'related_products': related_products,
        'product_images': product_images,
        'has_colors': product.has_colors(),
        'has_sizes': product.has_sizes(),
    }
    
    # Usar template específico si es ropa
    if category.slug == 'ropa-bolsos':
        return render(request, 'shop/clothing_product_detail.html', context)
    
    return render(request, 'shop/product_detail.html', context)


# ============================================================================
# ROPA Y BOLSOS - VISTAS REFACTORIZADAS (Usando sistema unificado)
# ============================================================================

def ropa_bolsos(request):
    """
    Página principal de Ropa y Bolsos - Estilo VistaPrint.
    Ahora usa el sistema unificado Category/Subcategory/Product.
    """
    # Obtener la categoría principal de ropa
    try:
        category = Category.objects.get(slug='ropa-bolsos', status='active')
    except Category.DoesNotExist:
        category = None
    
    # Obtener subcategorías (Polos, Camisas, Gorros, Bolsos)
    if category:
        subcategories = category.subcategories.filter(
            status='active'
        ).order_by('display_order')
    else:
        subcategories = Subcategory.objects.none()
    
    # Get filter parameters
    subcategory_filter = request.GET.get('subcategory', '')
    color_filter = request.GET.getlist('color')
    size_filter = request.GET.getlist('size')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    sort_by = request.GET.get('sort', 'featured')
    
    # Base queryset
    if category:
        products = Product.objects.filter(
            category=category,
            status='active'
        ).select_related('category', 'subcategory').prefetch_related(
            'available_colors', 'available_sizes', 'price_tiers', 'images'
        )
    else:
        products = Product.objects.none()
    
    # Apply filters
    if subcategory_filter:
        products = products.filter(subcategory__slug=subcategory_filter)
    
    if color_filter:
        products = products.filter(available_colors__slug__in=color_filter).distinct()
    
    if size_filter:
        products = products.filter(available_sizes__name__in=size_filter).distinct()
    
    if price_min:
        try:
            products = products.filter(base_price__gte=float(price_min))
        except ValueError:
            pass
    
    if price_max:
        try:
            products = products.filter(base_price__lte=float(price_max))
        except ValueError:
            pass
    
    # Apply sorting
    if sort_by == 'price_low':
        products = products.order_by('base_price')
    elif sort_by == 'price_high':
        products = products.order_by('-base_price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:  # featured
        products = products.order_by('-is_featured', '-is_bestseller', 'name')
    
    # Get all colors and sizes for filter sidebar
    all_colors = ProductColor.objects.filter(is_active=True).order_by('display_order')
    all_sizes = ProductSize.objects.filter(
        size_type='clothing', is_active=True
    ).order_by('display_order')
    
    context = {
        'category': category,
        'subcategories': subcategories,  # Antes era 'categories'
        'products': products,
        'all_colors': all_colors,
        'all_sizes': all_sizes,
        'selected_subcategory': subcategory_filter,
        'selected_colors': color_filter,
        'selected_sizes': size_filter,
        'price_min': price_min,
        'price_max': price_max,
        'sort_by': sort_by,
        'product_count': products.count(),
    }
    
    return render(request, 'shop/ropa_bolsos.html', context)


def clothing_category(request, category_slug):
    """
    Página de subcategoría de ropa (ej: /ropa-bolsos/polos/).
    Ahora usa Subcategory del sistema unificado.
    """
    try:
        # La "categoría de ropa" es ahora una subcategoría
        subcategory = Subcategory.objects.get(
            slug=category_slug,
            category__slug='ropa-bolsos',
            status='active'
        )
        category = subcategory.category
    except Subcategory.DoesNotExist:
        raise Http404("Categoría no encontrada")
    
    # Obtener todas las subcategorías hermanas para navegación
    sibling_subcategories = category.subcategories.filter(
        status='active'
    ).order_by('display_order')
    
    # Get filter parameters
    color_filter = request.GET.getlist('color')
    size_filter = request.GET.getlist('size')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    sort_by = request.GET.get('sort', 'featured')
    
    # Base queryset
    products = Product.objects.filter(
        subcategory=subcategory,
        status='active'
    ).select_related('category', 'subcategory').prefetch_related(
        'available_colors', 'available_sizes', 'price_tiers', 'images'
    )
    
    # Apply filters
    if color_filter:
        products = products.filter(available_colors__slug__in=color_filter).distinct()
    
    if size_filter:
        products = products.filter(available_sizes__name__in=size_filter).distinct()
    
    if price_min:
        try:
            products = products.filter(base_price__gte=float(price_min))
        except ValueError:
            pass
    
    if price_max:
        try:
            products = products.filter(base_price__lte=float(price_max))
        except ValueError:
            pass
    
    # Apply sorting
    if sort_by == 'price_low':
        products = products.order_by('base_price')
    elif sort_by == 'price_high':
        products = products.order_by('-base_price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-is_featured', '-is_bestseller', 'name')
    
    # Get colors and sizes available in this subcategory
    all_colors = ProductColor.objects.filter(
        products__subcategory=subcategory, is_active=True
    ).distinct().order_by('display_order')
    
    # Determine size type based on subcategory
    size_type = 'clothing'
    if 'gorra' in subcategory.slug or 'gorro' in subcategory.slug:
        size_type = 'hat'
    elif 'bolsa' in subcategory.slug or 'bolso' in subcategory.slug:
        size_type = 'bag'
    
    all_sizes = ProductSize.objects.filter(
        size_type=size_type, is_active=True
    ).order_by('display_order')
    
    context = {
        'category': category,
        'subcategory': subcategory,
        'subcategories': sibling_subcategories,
        'products': products,
        'all_colors': all_colors,
        'all_sizes': all_sizes,
        'selected_subcategory': subcategory.slug,
        'selected_colors': color_filter,
        'selected_sizes': size_filter,
        'price_min': price_min,
        'price_max': price_max,
        'sort_by': sort_by,
        'product_count': products.count(),
    }
    
    return render(request, 'shop/clothing_category.html', context)


def clothing_subcategory(request, category_slug, subcategory_slug):
    """
    Vista de sub-subcategoría de ropa (si se necesita más anidamiento).
    Por ahora redirige a clothing_category.
    """
    return clothing_category(request, subcategory_slug)


def clothing_product_detail(request, category_slug, product_slug):
    """
    Detalle de producto de ropa.
    Usa el sistema unificado Product.
    """
    try:
        subcategory = Subcategory.objects.get(
            slug=category_slug,
            category__slug='ropa-bolsos',
            status='active'
        )
        product = Product.objects.get(
            slug=product_slug,
            subcategory=subcategory,
            status='active'
        )
        category = subcategory.category
    except (Subcategory.DoesNotExist, Product.DoesNotExist):
        raise Http404("Producto no encontrado")
    
    # Obtener imágenes adicionales
    product_images = product.images.all().order_by('display_order')
    
    # Productos relacionados
    related_products = Product.objects.filter(
        subcategory=subcategory,
        status='active'
    ).exclude(pk=product.pk).order_by('-is_featured', '-is_bestseller')[:4]
    
    # Colores con imágenes
    colors_with_images = {}
    for img in product_images:
        if img.color:
            if img.color.slug not in colors_with_images:
                colors_with_images[img.color.slug] = []
            colors_with_images[img.color.slug].append(img.image_url)
    
    context = {
        'category': category,
        'subcategory': subcategory,
        'product': product,
        'product_images': product_images,
        'related_products': related_products,
        'colors_with_images': json.dumps(colors_with_images),
    }
    
    return render(request, 'shop/clothing_product_detail.html', context)


@csrf_exempt
def add_clothing_to_cart(request):
    """AJAX endpoint para agregar producto de ropa al carrito."""
    if request.method == 'POST':
        cart_id = request.COOKIES.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id="Random")
        else:
            cart = Cart.objects.create(cart_id="Random")
            cart_id = cart.id
        
        product_slug = request.POST.get('product_slug')
        color_slug = request.POST.get('color')
        size_name = request.POST.get('size')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            product = Product.objects.get(slug=product_slug, status='active')
            color = ProductColor.objects.get(slug=color_slug) if color_slug else None
            size = ProductSize.objects.get(name=size_name) if size_name else None
            
            # Guardar datos de personalización en comment como JSON
            custom_data = json.dumps({
                'type': 'clothing',
                'color': color.name if color else '',
                'color_hex': color.hex_code if color else '',
                'size': size.name if size else '',
            })
            
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=str(quantity),
                comment=custom_data,
                step_two_complete=True,
            )
            
            # Contar items en el carrito
            total_items = CartItem.objects.filter(
                cart_id=cart_id, 
                step_two_complete=True
            ).count()
            
            response = JsonResponse({
                'success': True,
                'cart_items_counter': total_items,
                'message': 'Producto agregado al carrito'
            })
            response.set_cookie("cart_id", cart_id)
            return response
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


# ============================================================================
# PRICING API
# ============================================================================

def get_product_pricing(request, product_slug, quantity):
    pricing_service = PricingService()
    pricing_data = pricing_service.get_pricing(product_slug, quantity)
    if pricing_data is None:
        return JsonResponse({'error': 'Product not found'}, status=404)
    return JsonResponse(pricing_data)


# ============================================================================
# ADD TO CART
# ============================================================================

@csrf_exempt
def add_product_to_cart(request):
    """AJAX endpoint to add product to cart with file uploads and contact info."""
    if request.method == 'POST':
        cart_id = request.COOKIES.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id="Random")
        else:
            cart = Cart.objects.create(cart_id="Random")
            cart_id = cart.id
        
        # Get form data
        category_slug = request.POST.get('category_slug')
        product_slug = request.POST.get('product_slug')
        quantity_tier = request.POST.get('quantity_tier')
        custom_quantity = request.POST.get('custom_quantity')
        template_slug = request.POST.get('template_slug', '')
        design_type = request.POST.get('design_type', 'custom')
        
        # Contact data
        contact_name = request.POST.get('contact_name', '').strip()
        contact_phone = request.POST.get('contact_phone', '').strip()
        contact_email = request.POST.get('contact_email', '').strip()
        contact_job_title = request.POST.get('contact_job_title', '').strip()
        contact_company = request.POST.get('contact_company', '').strip()
        contact_social = request.POST.get('contact_social', '').strip()
        contact_address = request.POST.get('contact_address', '').strip()
        
        # Edit mode
        edit_item_id = request.POST.get('edit_item_id')
        
        if edit_item_id:
            try:
                cart_item = CartItem.objects.get(id=edit_item_id)
                
                cart_item.contact_name = contact_name or None
                cart_item.contact_phone = contact_phone or None
                cart_item.contact_email = contact_email or None
                cart_item.contact_job_title = contact_job_title or None
                cart_item.contact_company = contact_company or None
                cart_item.contact_social = contact_social or None
                cart_item.contact_address = contact_address or None
                
                if design_type == 'template' and template_slug and template_slug != 'custom':
                    cart_item.comment = f"template:{template_slug[:80]}"
                    if cart_item.design_file:
                        cart_item.design_file.delete(save=False)
                        cart_item.design_file = None
                elif design_type == 'custom':
                    cart_item.comment = "custom"
                    if request.FILES.get('design_file'):
                        if cart_item.design_file:
                            cart_item.design_file.delete(save=False)
                        cart_item.design_file = request.FILES.get('design_file')
                
                if request.FILES.get('logo_file'):
                    if cart_item.logo_file:
                        cart_item.logo_file.delete(save=False)
                    cart_item.logo_file = request.FILES.get('logo_file')
                
                cart_item.save()
                
                response = JsonResponse({
                    'success': True,
                    'message': 'Datos actualizados correctamente',
                    'action': 'updated',
                    'item_id': cart_item.id
                })
                response.set_cookie("cart_id", cart_id)
                return response
                
            except CartItem.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'El item del carrito no existe'
                })
        
        # Create new item
        if quantity_tier == 'custom' and custom_quantity:
            quantity = str(custom_quantity)
        elif quantity_tier:
            quantity = str(quantity_tier)
        else:
            quantity = '100'
        
        quantity = ''.join(filter(str.isdigit, quantity)) or '100'
        
        try:
            product = Product.objects.get(
                category__slug=category_slug,
                slug=product_slug,
                status='active'
            )
            
            if design_type == 'template' and template_slug and template_slug != 'custom':
                comment = f"template:{template_slug[:80]}"
            else:
                comment = "custom"
            
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity,
                design_file=request.FILES.get('design_file'),
                logo_file=request.FILES.get('logo_file'),
                comment=comment,
                step_two_complete=True,
                contact_name=contact_name or None,
                contact_phone=contact_phone or None,
                contact_email=contact_email or None,
                contact_job_title=contact_job_title or None,
                contact_company=contact_company or None,
                contact_social=contact_social or None,
                contact_address=contact_address or None,
            )
            
            total_items = CartItem.objects.filter(
                cart_id=cart_id, 
                step_two_complete=True
            ).count()
            
            response = JsonResponse({
                'success': True,
                'cart_items_counter': total_items,
                'message': 'Producto agregado al carrito',
                'action': 'created',
                'item_id': cart_item.id
            })
            response.set_cookie("cart_id", cart_id)
            response.set_cookie("item_id", cart_item.id)
            return response
            
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Producto no encontrado'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# ============================================================================
# TARJETAS DE PRESENTACIÓN
# ============================================================================

class TarjetasPresentacionListView(ListView):
    model = Product
    template_name = 'shop/tarjetas_presentacion.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.filter(
            category__slug='tarjetas-presentacion',
            status='active'
        ).select_related('category', 'subcategory').prefetch_related('price_tiers')
        
        return queryset.order_by('subcategory__display_order', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            category = Category.objects.get(slug='tarjetas-presentacion')
            context['category'] = category
            context['subcategories'] = category.subcategories.filter(
                status='active'
            ).order_by('display_order')
        except Category.DoesNotExist:
            context['category'] = None
            context['subcategories'] = []
        
        tier_param = self.request.GET.get('tier', '')
        context['selected_subcategory'] = tier_param if tier_param != 'all' else ''
        
        if context['selected_subcategory']:
            try:
                selected_sub = Subcategory.objects.get(slug=context['selected_subcategory'])
                context['selected_subcategory_name'] = selected_sub.name
            except Subcategory.DoesNotExist:
                context['selected_subcategory_name'] = ''
        
        return context


# ============================================================================
# TEMPLATE GALLERY
# ============================================================================

def template_gallery_view(request, category_slug, product_slug):
    """Vista de galería de templates de diseño."""
    category = get_object_or_404(Category, slug=category_slug, status='active')
    product = get_object_or_404(Product, slug=product_slug, category=category, status='active')
    
    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1
    
    filter_type = request.GET.get('filter', 'all')
    if filter_type not in ('all', 'popular', 'new'):
        filter_type = 'all'
    
    edit_item_id = request.GET.get('edit_item')
    edit_item_data = None
    
    if edit_item_id:
        try:
            cart_item = CartItem.objects.get(id=edit_item_id)
            edit_item_data = json.dumps({
                'id': cart_item.id,
                'contact_name': cart_item.contact_name or '',
                'contact_phone': cart_item.contact_phone or '',
                'contact_email': cart_item.contact_email or '',
                'contact_job_title': cart_item.contact_job_title or '',
                'contact_company': cart_item.contact_company or '',
                'contact_social': cart_item.contact_social or '',
                'contact_address': cart_item.contact_address or '',
                'template_slug': cart_item.get_template_slug() if hasattr(cart_item, 'get_template_slug') else '',
                'logo_url': cart_item.logo_file.url if cart_item.logo_file else '',
            })
        except CartItem.DoesNotExist:
            edit_item_data = None
    
    data = TemplateLoader.get_paginated(
        page=page,
        per_page=24,
        filter_type=filter_type,
        category_slug=category_slug
    )
    
    stats = TemplateLoader.get_stats(category_slug)
    
    context = {
        'category': category,
        'product': product,
        'templates': data['templates'],
        'filter_type': filter_type,
        'total_templates': stats['total'],
        'popular_count': stats['popular_count'],
        'new_count': stats['new_count'],
        'page_obj': {
            'number': data['page'],
            'has_previous': data['has_prev'],
            'has_next': data['has_next'],
            'previous_page_number': data['prev_page'],
            'next_page_number': data['next_page'],
            'paginator': {
                'num_pages': data['total_pages'],
                'page_range': range(1, data['total_pages'] + 1),
            }
        },
        'showing_count': len(data['templates']),
        'edit_item_data': edit_item_data,
    }
    
    return render(request, 'shop/template_gallery.html', context)


# ============================================================================
# LEGACY LIST VIEWS
# ============================================================================

class FolletosListView(ListView):
    model = Folleto
    template_name = 'shop/folletos.html'
    context_object_name = 'folletos-list'


class PostersListView(ListView):
    model = Poster
    template_name = 'shop/posters.html'
    context_object_name = 'posters'


class EtiquetasListView(ListView):
    model = Etiqueta
    template_name = 'shop/etiquetas.html'
    context_object_name = 'etiquetas'


class EmpaquesListView(ListView):
    model = Empaque
    template_name = 'shop/empaques.html'
    context_object_name = 'empaques'


# ============================================================================
# STATIC PAGES
# ============================================================================

def productos_promocionales(request):
    return render(request, 'shop/productos_promocionales.html')

def empaques(request):
    return render(request, 'shop/empaques.html')

def invitaciones_regalos(request):
    return render(request, 'shop/invitaciones_regalos.html')

def bodas(request):
    return render(request, 'shop/bodas.html')

def servicios_diseno(request):
    return render(request, 'shop/servicios_diseno.html')


# ============================================================================
# PROFILE VIEWS
# ============================================================================

@login_required
def profile_view(request):
    """View user profile"""
    profile = request.user.profile
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
@transaction.atomic
def profile_edit_view(request):
    """Edit user profile"""
    peru = Peru.objects.all()
    department_list = sorted(set(p.departamento for p in peru))
    
    profile = request.user.profile
    
    if request.method == 'POST':
        department = request.POST.get('shipping_department')
        province = request.POST.get('shipping_province')
        
        province_list = sorted(set(Peru.objects.filter(
            departamento=department
        ).values_list("provincia", flat=True)))
        
        district_list = sorted(set(Peru.objects.filter(
            departamento=department, 
            provincia=province
        ).values_list("distrito", flat=True)))
        
        profile_form = ProfileForm(
            district_list, province_list, department_list,
            request.POST, request.FILES, instance=profile
        )
        
        if profile_form.is_valid():
            profile_form.save()
            return redirect('shop:profile')
    else:
        if profile.shipping_department:
            province_list = sorted(set(Peru.objects.filter(
                departamento=profile.shipping_department
            ).values_list("provincia", flat=True)))
        else:
            province_list = []
            
        if profile.shipping_department and profile.shipping_province:
            district_list = sorted(set(Peru.objects.filter(
                departamento=profile.shipping_department,
                provincia=profile.shipping_province
            ).values_list("distrito", flat=True)))
        else:
            district_list = []
        
        profile_form = ProfileForm(
            district_list, province_list, department_list,
            instance=profile
        )
    
    return render(request, 'accounts/profile_edit.html', {
        'profile_form': profile_form,
        'profile': profile
    })


# ============================================================================
# AJAX UTILITIES
# ============================================================================

@csrf_exempt
def update_template_only(request):
    """AJAX para actualizar solo la plantilla de un CartItem."""
    if request.method == 'POST':
        try:
            item_id = request.POST.get('item_id')
            template_slug = request.POST.get('template_slug', '')
            design_file = request.FILES.get('design_file')
            
            if not item_id:
                return JsonResponse({
                    'success': False,
                    'error': 'No se especificó el item'
                })
            
            cart_item = CartItem.objects.get(id=item_id)
            
            if template_slug == 'custom':
                cart_item.comment = 'custom'
                if design_file:
                    if cart_item.design_file:
                        cart_item.design_file.delete(save=False)
                    cart_item.design_file = design_file
            else:
                cart_item.comment = f'template:{template_slug[:80]}'
                if cart_item.design_file:
                    cart_item.design_file.delete(save=False)
                    cart_item.design_file = None
            
            cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Plantilla actualizada correctamente'
            })
            
        except CartItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Item no encontrado'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


def get_province(request):
    d_name = request.GET.get("d_name")
    data = Peru.objects.filter(departamento=d_name).values_list("provincia", flat=True)
    return render(request, "accounts/province_dropdown.html", {
        "provinces": set(list(data))
    })


def get_district(request):
    d_name = request.GET.get("d_name")
    p_name = request.GET.get("p_name")
    data = Peru.objects.filter(departamento=d_name, provincia=p_name).values_list("distrito", flat=True)
    return render(request, "accounts/district_dropdown.html", {
        "districts": set(list(data))
    })


### ¿Quiénes somos? ###

def quienes_somos(request):
    return render(request, "footer_links/quienes_somos.html")


### ¿Cómo comprar? ###

def como_comprar(request):
    return render(request, "footer_links/como_comprar.html")


### Contactanos ###

def contactanos(request):
    return render(request, "footer_links/contactanos.html")


### Legales - Privacidad ###


def legales_privacidad(request):
    return render(request, 'footer_links/legales_privacidad.html')

### Legales - Términos ###

def legales_terminos(request):
    return render(request, 'footer_links/legales_terminos.html')    

### Preguntas frecuentes ###

def preguntas_frecuentes(request):
    return render(request, 'footer_links/preguntas_frecuentes.html')

# Tamanos y cantidades

class StepOneView(FormView):
    form_class = StepOneForm
    template_name = 'shop/medidas-cantidades.html'
    success_url = 'subir-arte'

    def get_initial(self):
        # pre-populate form if someone goes back and forth between forms
        initial = super(StepOneView, self).get_initial()
        initial['size'] = self.request.session.get('size', None)
        initial['quantity'] = self.request.session.get('quantity', None)
        initial['product'] = Product.objects.get(
            category__slug=self.kwargs['c_slug'],
            slug=self.kwargs['product_slug']
        )

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Product.objects.get(
            category__slug=self.kwargs['c_slug'],
            slug=self.kwargs['product_slug']
        )
        return context

    def form_invalid(self, form):
        print('Step one: form is NOT valid')

    def form_valid(self, form):
        cart_id = self.request.COOKIES.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
            except ObjectDoesNotExist:
                # supplied ID doesn't match a Cart from your BD
                cart = Cart.objects.create(cart_id="Random")
        else:
            cart = Cart.objects.create(cart_id="Random")
            cart_id = cart.id
        item = CartItem.objects.create(
            size=form.cleaned_data.get('size'),
            quantity=form.cleaned_data.get('quantity'),
            product=Product.objects.get(
                category__slug=self.kwargs['c_slug'],
                slug=self.kwargs['product_slug']
            ),
            cart=cart
        )

        response = HttpResponseRedirect(self.get_success_url())
        response.set_cookie("cart_id", cart_id)
        response.set_cookie("item_id", item.id)
        return response


# here we are going to use CreateView to save the Third step ModelForm
class StepTwoView(FormView):
    form_class = StepTwoForm
    template_name = 'shop/subir-arte.html'
    success_url = '/carrito-de-compras/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Product.objects.get(
            category__slug=self.kwargs['c_slug'],
            slug=self.kwargs['product_slug']
        )
        return context

    def form_invalid(self, form):
        print('StepTwoForm is not Valid', form.errors)

    def form_valid(self, form):
        item_id = self.request.COOKIES.get("item_id")

        cart_item = CartItem.objects.get(id=item_id)
        cart_item.file_a = form.cleaned_data["file_a"]
        cart_item.file_b = form.cleaned_data["file_b"]
        cart_item.comment = form.cleaned_data["comment"]
        cart_item.step_two_complete = True
        cart_item.save()
        response = HttpResponseRedirect(self.get_success_url())
        response.delete_cookie("item_id")
        return response


### STEPS ONE & TWO FOR SAMPLES


# Tamanos y cantidades

class StepOneView_Sample(FormView):
    form_class = StepOneForm_Sample
    template_name = 'shop/medidas-cantidades.html'
    success_url = 'subir-arte'

    def get_initial(self):
        # pre-populate form if someone goes back and forth between forms
        initial = super(StepOneView_Sample, self).get_initial()
        initial['size'] = self.request.session.get('size', None)
        initial['sample'] = Sample.objects.get(
            # category=self.kwargs['muestras'],
            slug=self.kwargs['sample_slug']
        )

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sample'] = Sample.objects.get(
            # category=self.kwargs['muestras'],
            slug=self.kwargs['sample_slug']
        )
        context['sample_form'] = context.get('form')
        return context

    def form_invalid(self, form):
        print('Step one: form is NOT valid')

    def form_valid(self, form):
        cart_id = self.request.COOKIES.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
            except ObjectDoesNotExist:
                # supplied ID doesn't match a Cart from your BD
                cart = Cart.objects.create(cart_id="Random")
        else:
            cart = Cart.objects.create(cart_id="Random")
            cart_id = cart.id
        item = SampleItem.objects.create(
            size=form.cleaned_data.get('size'),
            quantity=2,
            sample=Sample.objects.get(
                # category=self.kwargs['muestras'],
                slug=self.kwargs['sample_slug']
            ),
            cart=cart
        )

        response = HttpResponseRedirect(self.get_success_url())
        response.set_cookie("cart_id", cart_id)
        response.set_cookie("item_id", item.id)
        return response


# here we are going to use CreateView to save the Third step ModelForm

class StepTwoView_Sample(FormView):
    form_class = StepTwoForm_Sample
    template_name = 'shop/subir-arte.html'
    success_url = '/carrito-de-compras/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Sample.objects.get(
            # category__slug=self.kwargs['c_slug'],
            slug=self.kwargs['sample_slug']
        )
        return context

    def form_invalid(self, form):
        print('StepTwoForm is not Valid', form.errors)

    def form_valid(self, form):
        item_id = self.request.COOKIES.get("item_id")

        sample_item = SampleItem.objects.get(id=item_id)
        sample_item.file_a = form.cleaned_data["file_a"]
        sample_item.file_b = form.cleaned_data["file_b"]
        sample_item.comment = form.cleaned_data["comment"]
        sample_item.step_two_complete = True
        sample_item.save()
        response = HttpResponseRedirect(self.get_success_url())
        response.delete_cookie("item_id")
        return response


###############################
###############################


def signinView(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # username = request.POST['username']
            # password = request.POST['password']
            print(username)
            print(password)
            user = authenticate(username=username,
                                password=password)
            if user is not None:
                login(request, user)
                # cart_id =_cart_id(request)
                # request.session['cart_id'] = cart_id
                return redirect('carrito-de-compras:cart_detail')
            else:
                return redirect('signup')

    else:
        form = AuthenticationForm()
    return render(request, 'accounts/signin.html', {'form': form})


def signoutView(request):
    if request.user.is_superuser:
        request.session.modified = True

        logout(request)

    else:
        # del request.session['cart_id']
        request.session.modified = True
        logout(request)

    response = redirect('signin')
    response.delete_cookie("cart_id")
    response.delete_cookie("cupon")
    return response


### New SignUp Extended

from django.shortcuts import render
from django.contrib.auth.decorators import login_required



### Email Confirmation Needed ###

def email_confirmation_needed(request):
    return render(request, "accounts/email_confirmation_needed.html")



def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        print("############")
        print("Enters if of activate function")
        print("############")
        user.is_active = True
        user.save()
        login(request, user)
        '''send email to admin when a new user has activate his/her account'''
        print("############")
        print(user.id)
        print(type(user.id))
        print("############")
        send_email_new_registered_user(user.id)
        return redirect('shop:home')
    else:
        return HttpResponse('¡Enlace de activación inválido! Intente registrarse nuevamente.')



def send_email_new_registered_user(user_id):
    try:
        print("Enters send_email_new_registed_user try")
        profile = Profile.objects.latest('id')
        if profile:
            print("Se obtuvo profile")
        '''sending the order to the customer'''
        subject = f"Imprenta Gallito Perú - Nuevo usuario registrado #{profile.id}"
        to = [f'{profile.user.email}', 'imprentagallito@gmail.com', 'oma.gonzales@gmail.com']
        from_email = 'imprentagallito@imprentagallito.pe'
        user_information = {
            'user_id': profile.user.id,
            'user_name': profile.user.username,
            'user_full_name': profile.user.get_full_name,
            'user_dni': profile.dni,
            'user_deparment': profile.shipping_deparment,
            'user_province': profile.shipping_province,
            'user_disctrict': profile.shipping_district,
            'user_shipping_address': profile.shipping_address1,
            'user_email': profile.user.email,
            'user_phone': profile.phone_number,
            'user_is_active': profile.user.is_active,
        }
        message = get_template('accounts/new_registered_user.html').render(user_information)
        msg = EmailMessage(subject, message, to=to, from_email=from_email)
        msg.content_subtype = 'html'
        msg.send()
        print("Se envió msj")
    except:
        pass


@transaction.atomic
def signupView(request):
    peru = Peru.objects.all()
    department_list = set()
    province_list = set()
    district_list = set()
    for p in peru:
        department_list.add(p.departamento)
    department_list = list(department_list)
    if len(department_list):
        province_list = set(Peru.objects.filter(departamento=department_list[0]).values_list("provincia", flat=True))
        province_list = list(province_list)
    else:
        province_list = set()
    if len(province_list):
        district_list = set(
            Peru.objects.filter(departamento=department_list[0], provincia=province_list[0]).values_list("distrito",
                                                                                                         flat=True))
    else:
        district_list = set()

    if request.method == 'POST':

        peru = Peru.objects.all()
        department_list = set()
        province_list = set()
        district_list = set()
        for p in peru:
            department_list.add(p.departamento)
        department_list = list(department_list)
        if len(department_list):
            province_list = set(
                Peru.objects.filter(departamento__in=department_list).values_list("provincia", flat=True))

            province_list = list(province_list)
        else:
            province_list = set()
        if len(province_list):
            district_list = set(
                Peru.objects.filter(departamento__in=department_list, provincia__in=province_list).values_list(
                    "distrito",
                    flat=True))
        else:
            district_list = set()

        #####

        user_form = SignUpForm(request.POST)
        profile_form = ProfileForm(district_list, province_list, department_list, request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.is_active = True
            user.save()
            username = user_form.cleaned_data.get('username')
            signup_user = User.objects.get(username=username)
            customer_group = Group.objects.get(name='Clientes')
            customer_group.user_set.add(signup_user)
            raw_password = user_form.cleaned_data.get('password1')
            user.refresh_from_db()  # This will load the Profile created by the Signal

            profile_form = ProfileForm(district_list, province_list, department_list, request.POST, request.FILES,
                                       instance=user.profile)  # Reload the profile form with the profile instance
            profile_form.full_clean()  # Manually clean the form this time. It is implicitly called by "is_valid()" method
            profile_form.save()  # Gracefully save the form
            send_email_new_registered_user(user.id) # send email to admin when a new user registers himself
            login(request, user)

            return redirect('carrito-de-compras:cart_detail')

        else:
            pass


    else:

        user_form = SignUpForm()

        profile_form = ProfileForm(district_list, province_list, department_list)

    return render(request, 'accounts/signup.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


# =============================================================================
# CONSTANTES PARA FILTROS
# =============================================================================
GENDER_CHOICES = [
    ('unisex', 'Unisex'),
    ('hombre', 'Hombre'),
    ('mujer', 'Mujer'),
    ('juvenil', 'Juvenil'),
]

NECK_TYPE_CHOICES = [
    ('cuello_redondo', 'Cuello Redondo'),
    ('cuello_v', 'Cuello V'),
    ('sin_mangas', 'Sin Mangas'),
    ('cuello_polo', 'Cuello Polo'),
    ('espalda_atletica', 'Espalda Atlética'),
    ('crop_top', 'Crop Top'),
]

SLEEVE_TYPE_CHOICES = [
    ('manga_corta', 'Manga Corta'),
    ('manga_larga', 'Manga Larga'),
    ('sin_mangas', 'Sin Mangas'),
]


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================
def parse_features(features_str):
    """
    Parsea el string de features guardado en el producto
    Formato: "genero:unisex,cuello:cuello_redondo,manga:manga_corta"
    Retorna: {'genero': 'unisex', 'cuello': 'cuello_redondo', 'manga': 'manga_corta'}
    """
    result = {}
    if not features_str:
        return result
    
    for item in features_str.split(','):
        if ':' in item:
            key, value = item.split(':', 1)
            result[key.strip()] = value.strip()
    
    return result


def get_product_feature(product, feature_name):
    """Obtiene un feature específico del producto"""
    if hasattr(product, 'features') and product.features:
        features = parse_features(product.features)
        return features.get(feature_name, '')
    return ''


# =============================================================================
# VISTA PRINCIPAL: clothing_category CON FILTROS AVANZADOS
# =============================================================================
def clothing_category(request, category_slug):
    """
    Vista para mostrar productos de una subcategoría de ropa con filtros avanzados.
    
    URL: /ropa-bolsos/polos/
    
    Filtros disponibles:
    - genero: Filtro por género (unisex, hombre, mujer, juvenil)
    - tipo_cuello: Filtro por tipo de cuello
    - tipo_manga: Filtro por tipo de manga
    - color: Filtro por slugs de colores (múltiples)
    - talla: Filtro por nombres de tallas (múltiples)
    - marca: Filtro por marca
    - precio_min/precio_max: Rango de precios
    - q: Búsqueda por texto
    - sort: Ordenamiento
    """
    # Obtener la categoría principal (ropa-bolsos)
    parent_category = get_object_or_404(Category, slug='ropa-bolsos')
    
    # Obtener la subcategoría (polos, gorros, etc.)
    subcategory = get_object_or_404(Subcategory, slug=category_slug, category=parent_category)
    
    # Obtener todas las subcategorías para navegación
    subcategories = Subcategory.objects.filter(
        category=parent_category
    ).order_by('display_order')
    
    # =========================================================================
    # OBTENER PARÁMETROS DE FILTRO
    # =========================================================================
    selected_genders = request.GET.getlist('genero')
    selected_neck_types = request.GET.getlist('tipo_cuello')
    selected_sleeve_types = request.GET.getlist('tipo_manga')
    selected_colors = request.GET.getlist('color')
    selected_sizes = request.GET.getlist('talla')
    selected_brands = request.GET.getlist('marca')
    price_min = request.GET.get('precio_min', '')
    price_max = request.GET.get('precio_max', '')
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'featured')
    
    # =========================================================================
    # CONSTRUIR QUERYSET BASE
    # =========================================================================
    products = Product.objects.filter(
        subcategory=subcategory,
        status='active'
    ).prefetch_related(
        'available_colors',
        'available_sizes',
        'price_tiers',
        Prefetch(
            'images',
            queryset=ProductImage.objects.filter(is_primary=True),
            to_attr='primary_images'
        )
    )
    
    # =========================================================================
    # APLICAR FILTROS
    # =========================================================================
    
    # Filtro por género (usando campo features)
    if selected_genders:
        gender_q = Q()
        for gender in selected_genders:
            gender_q |= Q(features__icontains=f'genero:{gender}')
        products = products.filter(gender_q)
    
    # Filtro por tipo de cuello
    if selected_neck_types:
        neck_q = Q()
        for neck_type in selected_neck_types:
            neck_q |= Q(features__icontains=f'cuello:{neck_type}')
        products = products.filter(neck_q)
    
    # Filtro por tipo de manga
    if selected_sleeve_types:
        sleeve_q = Q()
        for sleeve_type in selected_sleeve_types:
            sleeve_q |= Q(features__icontains=f'manga:{sleeve_type}')
        products = products.filter(sleeve_q)
    
    # Filtro por colores
    if selected_colors:
        products = products.filter(
            available_colors__slug__in=selected_colors
        ).distinct()
    
    # Filtro por tallas
    if selected_sizes:
        products = products.filter(
            available_sizes__name__in=selected_sizes
        ).distinct()
    
    # Filtro por marca (guardada en campo material)
    if selected_brands:
        brand_q = Q()
        for brand in selected_brands:
            brand_q |= Q(material__icontains=brand)
        products = products.filter(brand_q)
    
    # Filtro por precio
    if price_min:
        try:
            products = products.filter(base_price__gte=float(price_min))
        except ValueError:
            pass
    
    if price_max:
        try:
            products = products.filter(base_price__lte=float(price_max))
        except ValueError:
            pass
    
    # Búsqueda por texto
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(sku__icontains=search_query)
        )
    
    # =========================================================================
    # ORDENAMIENTO
    # =========================================================================
    if sort_by == 'price_low':
        products = products.order_by('base_price')
    elif sort_by == 'price_high':
        products = products.order_by('-base_price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:  # featured
        products = products.order_by('display_order', 'name')
    
    # =========================================================================
    # OBTENER OPCIONES DE FILTRO DISPONIBLES
    # =========================================================================
    
    # Colores disponibles en esta subcategoría
    all_colors = ProductColor.objects.filter(
        products__subcategory=subcategory,
        products__status='active',
        is_active=True
    ).distinct().order_by('display_order', 'name')
    
    # Tallas disponibles
    all_sizes = ProductSize.objects.filter(
        size_type='clothing',
        is_active=True
    ).order_by('display_order')
    
    # Marcas disponibles (extraídas del campo material)
    all_brands = Product.objects.filter(
        subcategory=subcategory,
        status='active'
    ).exclude(
        material__isnull=True
    ).exclude(
        material=''
    ).values_list('material', flat=True).distinct()
    all_brands = sorted(set(all_brands))
    
    # =========================================================================
    # PAGINACIÓN
    # =========================================================================
    paginator = Paginator(products, 12)  # 12 productos por página
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # =========================================================================
    # VERIFICAR SI HAY FILTROS ACTIVOS
    # =========================================================================
    has_active_filters = any([
        selected_genders,
        selected_neck_types,
        selected_sleeve_types,
        selected_colors,
        selected_sizes,
        selected_brands,
        price_min,
        price_max,
        search_query,
    ])
    
    # =========================================================================
    # CONTEXTO
    # =========================================================================
    context = {
        # Navegación
        'category': subcategory,  # Para compatibilidad con template existente
        'subcategory': subcategory,
        'parent_category': parent_category,
        'subcategories': subcategories,
        
        # Productos
        'products': page_obj,
        'page_obj': page_obj,
        'product_count': paginator.count,
        
        # Opciones de filtro
        'all_colors': all_colors,
        'all_sizes': all_sizes,
        'all_brands': all_brands,
        'gender_choices': GENDER_CHOICES,
        'neck_type_choices': NECK_TYPE_CHOICES,
        'sleeve_type_choices': SLEEVE_TYPE_CHOICES,
        
        # Filtros seleccionados
        'selected_genders': selected_genders,
        'selected_neck_types': selected_neck_types,
        'selected_sleeve_types': selected_sleeve_types,
        'selected_colors': selected_colors,
        'selected_sizes': selected_sizes,
        'selected_brands': selected_brands,
        'price_min': price_min,
        'price_max': price_max,
        'search_query': search_query,
        'sort_by': sort_by,
        
        # Helper
        'has_active_filters': has_active_filters,
    }
    
    return render(request, 'shop/clothing_category.html', context)


# =============================================================================
# VISTA: clothing_subcategory (alternativa si usas 2 niveles)
# =============================================================================
def clothing_subcategory(request, category_slug, subcategory_slug):
    """
    Vista para subcategorías anidadas (si tu estructura lo requiere)
    URL: /ropa-bolsos/polos/hombre/
    """
    parent_category = get_object_or_404(Category, slug='ropa-bolsos')
    
    # En este caso category_slug sería la subcategoría principal
    # y subcategory_slug sería un filtro adicional
    subcategory = get_object_or_404(Subcategory, slug=category_slug, category=parent_category)
    
    # Redirigir a clothing_category con el filtro de género
    from django.shortcuts import redirect
    from django.urls import reverse
    
    url = reverse('shop:clothing_category', kwargs={'category_slug': category_slug})
    return redirect(f'{url}?genero={subcategory_slug}')


# =============================================================================
# API: Obtener colores disponibles (para filtros dinámicos)
# =============================================================================
def get_available_colors(request):
    """
    API para obtener colores disponibles basados en filtros activos.
    Útil para actualizar los swatches dinámicamente.
    """
    subcategory_slug = request.GET.get('subcategory', '')
    
    if not subcategory_slug:
        return JsonResponse({'colors': []})
    
    try:
        subcategory = Subcategory.objects.get(slug=subcategory_slug)
    except Subcategory.DoesNotExist:
        return JsonResponse({'colors': []})
    
    colors = ProductColor.objects.filter(
        products__subcategory=subcategory,
        products__status='active',
        is_active=True
    ).distinct().values('slug', 'name', 'hex_code').order_by('display_order')
    
    return JsonResponse({'colors': list(colors)})


# =============================================================================
# API: Obtener colores e imágenes de un producto
# =============================================================================
def get_product_colors(request, product_slug):
    """
    API para obtener colores e imágenes de un producto específico.
    Útil para el modal de selección rápida o hover.
    """
    try:
        product = Product.objects.get(slug=product_slug)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    
    colors_data = []
    for color in product.available_colors.all():
        # Buscar imagen para este color
        image = ProductImage.objects.filter(
            product=product,
            color=color
        ).first()
        
        colors_data.append({
            'slug': color.slug,
            'name': color.name,
            'hex_code': color.hex_code,
            'image_url': image.image_url if image else product.base_image_url,
        })
    
    return JsonResponse({
        'product_slug': product_slug,
        'product_name': product.name,
        'colors': colors_data,
    })


# =============================================================================
# VISTA: Detalle de producto de ropa
# =============================================================================
def clothing_product_detail(request, category_slug, product_slug):
    """
    Vista de detalle de producto de ropa con selector de colores y tallas.
    """
    parent_category = get_object_or_404(Category, slug='ropa-bolsos')
    subcategory = get_object_or_404(Subcategory, slug=category_slug, category=parent_category)
    
    product = get_object_or_404(
        Product,
        slug=product_slug,
        subcategory=subcategory,
        status='active'
    )
    
    # Obtener imágenes organizadas por color
    images_by_color = {}
    for image in product.images.all():
        color_slug = image.color.slug if image.color else 'default'
        if color_slug not in images_by_color:
            images_by_color[color_slug] = []
        images_by_color[color_slug].append({
            'image': image.image_url,
            'is_primary': image.is_primary,
        })
    
    # Obtener imágenes por defecto (sin color específico)
    default_images = product.images.filter(color__isnull=True)
    
    # Obtener tiers de precio
    pricing_tiers = product.price_tiers.all().order_by('min_quantity')
    
    # Productos relacionados
    related_products = Product.objects.filter(
        subcategory=subcategory,
        status='active'
    ).exclude(pk=product.pk)[:4]
    
    context = {
        'product': product,
        'category': subcategory,
        'subcategory': subcategory,
        'parent_category': parent_category,
        'images_by_color': json.dumps(images_by_color),
        'default_images': default_images,
        'pricing_tiers': pricing_tiers,
        'related_products': related_products,
    }
    
    return render(request, 'shop/clothing_product_detail.html', context)
