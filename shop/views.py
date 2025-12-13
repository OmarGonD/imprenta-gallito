"""
Shop Views - SISTEMA UNIFICADO CON OPCIONES GENÉRICAS
======================================================
Migrado de ProductColor/ProductSize a ProductOption/ProductOptionValue/ProductVariant.
Todas las vistas usan el sistema Category → Subcategory → Product.
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
from django.db.models import Q, Count, Min, Prefetch

# =============================================================================
# IMPORTS DE MODELOS - SISTEMA GENÉRICO DE OPCIONES
# =============================================================================
from shop.models import (
    Profile, Peru, Category, Subcategory, Product,
    ProductOption, ProductOptionValue, ProductVariant,  # ← NUEVO SISTEMA
    ProductImage,
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
    Vista genérica para mostrar una categoría con sus subcategorías y productos.
    Muestra productos agrupados por subcategoría con vista previa (máx 4).
    """
    print(f"🔍 Vista ejecutada: Entra a Category View")
    try:
        category = Category.objects.get(slug=category_slug, status='active')
    except Category.DoesNotExist:
        raise Http404("Categoría no encontrada")
    
    # Prefetch subcategorías con sus productos activos (optimizado)
    subcategories = category.subcategories.filter(
        status='active'
    ).prefetch_related(
        Prefetch(
            'products',
            queryset=Product.objects.filter(status='active').order_by('display_order', 'name'),
            to_attr='active_products_list'
        )
    ).order_by('display_order')
    
    # Productos sin subcategoría (si los hay)
    products_without_subcategory = Product.objects.filter(
        category=category,
        subcategory__isnull=True,
        status='active'
    ).order_by('display_order', 'name')
    
    context = {
        'category': category,
        'subcategories': subcategories,
        'products': products_without_subcategory,  # Para productos sin subcategoría
        'product_count': Product.objects.filter(category=category, status='active').count(),
    }
    
    return render(request, 'shop/category.html', context)


def subcategory_view(request, category_slug, subcategory_slug):
    """
    Vista para mostrar una subcategoría y sus productos.
    ACTUALIZADO: Usa sistema genérico de opciones.
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
    
    # ACTUALIZADO: Prefetch con nuevo sistema
    products = Product.objects.filter(
        subcategory=subcategory,
        status='active'
    ).select_related(
        'category', 'subcategory'
    ).prefetch_related(
        'price_tiers',
        'variant_options__option',
        'variant_options__available_values'
    )
    
    sibling_subcategories = category.subcategories.filter(status='active').order_by('display_order')
    
    # Filtros - ACTUALIZADO para sistema genérico
    color_filter = request.GET.getlist('color')
    size_filter = request.GET.getlist('size')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    sort_by = request.GET.get('sort', 'featured')
    
    # ACTUALIZADO: Filtrar por colores usando nuevo sistema
    if color_filter:
        products = products.filter(
            variant_options__option__key='color',
            variant_options__available_values__value__in=color_filter
        ).distinct()
    
    # ACTUALIZADO: Filtrar por tallas usando nuevo sistema
    if size_filter:
        products = products.filter(
            variant_options__option__key='size',
            variant_options__available_values__value__in=size_filter
        ).distinct()
    
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
    
    # ACTUALIZADO: Obtener colores y tallas disponibles con nuevo sistema
    all_colors = ProductOptionValue.objects.filter(
        option__key='color',
        product_variants__product__subcategory=subcategory,
        is_active=True
    ).distinct().order_by('display_order')
    
    all_sizes = ProductOptionValue.objects.filter(
        option__key='size',
        product_variants__product__subcategory=subcategory,
        is_active=True
    ).distinct().order_by('display_order')
    
    context = {
        'category': category,
        'subcategory': subcategory,
        'subcategories': sibling_subcategories,
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


def product_detail(request, category_slug, subcategory_slug, product_slug):
    """
    Vista unificada para detalle de producto (Ropa/Imprenta)
    ACTUALIZADO: Usa sistema genérico de opciones.
    """
    
    # -------------------------------------------------------------------------
    # 1. OBTENCIÓN INICIAL
    # -------------------------------------------------------------------------
    
    category = get_object_or_404(Category, slug=category_slug, status='active')

    try:
        product = Product.objects.get(
            category=category,
            subcategory__slug=subcategory_slug,
            slug=product_slug,
            status='active'
        )
    except Product.DoesNotExist:
        raise Http404("Producto no encontrado")
    
    # -------------------------------------------------------------------------
    # 2. PROCESAR PRECIOS DE FORMA SEGURA
    # -------------------------------------------------------------------------
    
    raw_starting_price = product.starting_price
    raw_base_price = product.base_price
    
    if raw_starting_price is not None:
        safe_starting_price = float(raw_starting_price)
    elif raw_base_price is not None:
        safe_starting_price = float(raw_base_price)
    else:
        first_tier = product.price_tiers.order_by('min_quantity').first()
        safe_starting_price = float(first_tier.unit_price) if first_tier and first_tier.unit_price is not None else 0.0
    
    if raw_base_price is not None:
        safe_base_price = float(raw_base_price)
    elif raw_starting_price is not None:
        safe_base_price = float(raw_starting_price)
    else:
        safe_base_price = safe_starting_price 
    
    # -------------------------------------------------------------------------
    # 3. INICIALIZAR CONTEXTO BASE
    # -------------------------------------------------------------------------
    
    context = {
        'category': category,
        'product': product,
        'related_products': None,
        'template_name': 'shop/tarjetas_presentacion_product_detail.html',
        'pricing_tiers': [], 
        'images_by_color': '{}',
        'selected_color_slug': '',
        'base_image_url': product.base_image_url or '',
        'safe_starting_price': safe_starting_price,
        'safe_base_price': safe_base_price,
    }

    # -------------------------------------------------------------------------
    # 4. LÓGICA DE TIERS UNIFICADA
    # -------------------------------------------------------------------------
    
    pricing_tiers_qs = product.price_tiers.all().order_by('min_quantity')
    formatted_tiers = []
    
    for tier in pricing_tiers_qs:
        savings = 0.0
        current_unit_price = float(tier.unit_price) 
        
        if safe_base_price > 0 and safe_base_price > current_unit_price:
            savings = safe_base_price - current_unit_price
        
        formatted_tiers.append({
            'min_quantity': int(tier.min_quantity),
            'max_quantity': int(tier.max_quantity),
            'unit_price': current_unit_price,
            'discount_percent': tier.discount_percentage,
            'savings': savings
        })

    if not formatted_tiers:
        formatted_tiers = [{
            'min_quantity': 1,
            'max_quantity': 999999,
            'unit_price': safe_base_price,
            'discount_percent': 0,
            'savings': 0.0,
        }]

    context['pricing_tiers'] = formatted_tiers
    context['pricing_tiers_json'] = json.dumps(formatted_tiers)

    # -------------------------------------------------------------------------
    # 5. LÓGICA ESPECÍFICA (Ropa vs. Imprenta) - ACTUALIZADO
    # -------------------------------------------------------------------------

    if category_slug == 'ropa-bolsos':
        
        subcategory = product.subcategory

        # ACTUALIZADO: Obtener opciones usando nuevo sistema
        variant_options = product.get_variant_options()
        
        # Obtener colores y tallas del nuevo sistema
        available_colors = product.get_colors()  # Método de retrocompatibilidad
        available_sizes = product.get_sizes()    # Método de retrocompatibilidad
        
        context.update({
            'variant_options': variant_options,  # Nuevo: todas las opciones
            'available_sizes': available_sizes,
            'available_colors': available_colors,
            'pricing_tiers_qs': pricing_tiers_qs, 
            'subcategory': subcategory,
            'category_slug': subcategory.slug,
        })
        
        # MANEJO DE COLORES E IMÁGENES - ACTUALIZADO
        selected_color_slug = request.GET.get('color', '')
        
        selected_color = None
        if selected_color_slug and available_colors:
            for color in available_colors:
                if color.value == selected_color_slug:
                    selected_color = color
                    break
        
        if not selected_color and available_colors:
            selected_color = available_colors[0]
            selected_color_slug = selected_color.value
            
        context.update({
            'selected_color': selected_color,
            'selected_color_slug': selected_color_slug or '',
        })

        # ACTUALIZADO: Construir images_by_color con nuevo sistema
        images_by_color = {}
        base_image_url = product.base_image_url or ''
        
        # Obtener imágenes relacionadas con option_value
        all_images = product.images.select_related('option_value').order_by(
            'option_value__value', '-is_primary', 'display_order'
        )
        
        for img in all_images:
            color_key = img.option_value.value if img.option_value else 'default'
            if color_key not in images_by_color:
                images_by_color[color_key] = []
            
            images_by_color[color_key].append({
                'image': img.image_url or '',
                'is_primary': img.is_primary,
                'alt_text': img.alt_text or product.name
            })
        
        if selected_color:
            primary_image = product.images.filter(
                option_value=selected_color, 
                is_primary=True
            ).first()
            
            if primary_image:
                base_image_url = primary_image.image_url or base_image_url
            else:
                first_image = product.images.filter(option_value=selected_color).first()
                if first_image:
                    base_image_url = first_image.image_url or base_image_url

        context.update({
            'base_image_url': base_image_url,
            'images_by_color': json.dumps(images_by_color),
        })

        context['template_name'] = 'shop/clothing_product_detail.html'
        
    else:
        # -------------------------------------------------------------------------
        # 5.1. LÓGICA PARA IMPRENTA Y OTROS
        # -------------------------------------------------------------------------
        
        #context['variant_types'] = product.get_available_variant_types()
        
        context['related_products'] = Product.objects.filter(
            category=category,
            status='active'
        ).exclude(pk=product.pk)[:4]
        
        context.update({
            'product_images': product.images.all().order_by('display_order'),
            'has_colors': product.has_colors(),
            'has_sizes': product.has_sizes(),
        })

    # -------------------------------------------------------------------------
    # 6. DEBUGGING
    # -------------------------------------------------------------------------
    
    print("\n" + "="*70)
    print(f"🔍 DEBUGGING: {product.name} (Template: {context['template_name']})")
    print("="*70)
    print(f"  Tiers cargados: {len(context['pricing_tiers'])} tiers")
    print(f"  Precio Base Seguro (float): {context['safe_base_price']}")
    
    if context['pricing_tiers']:
        print(f"\n  📊 Tiers procesados:")
        for i, tier in enumerate(context['pricing_tiers'][:3]):
            print(f"    Tier {i}: min={tier['min_quantity']}, "
                  f"max={tier['max_quantity']}, "
                  f"price={tier['unit_price']} (savings={tier['savings']})")
    
    print("="*70 + "\n")
    
    # -------------------------------------------------------------------------
    # 7. RENDERIZADO FINAL
    # -------------------------------------------------------------------------
    
    return render(request, context['template_name'], context)



# =============================================================================
# API: Agregar producto de ropa al carrito (con HTMX)
# =============================================================================
@csrf_exempt
def add_clothing_to_cart(request):
    """
    API para agregar productos de ropa al carrito.
    ACTUALIZADO: Usa sistema genérico de opciones.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        cart_id = request.COOKIES.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(pk=cart_id)
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id="Random")
        else:
            cart = Cart.objects.create(cart_id="Random")
            cart_id = cart.pk
        
        product_slug = request.POST.get('product_slug')
        color_value = request.POST.get('color') or request.POST.get('color_slug')
        size_value = request.POST.get('size') or request.POST.get('size_slug')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            product = Product.objects.get(slug=product_slug, status='active')
            
            # ACTUALIZADO: Obtener color y talla del nuevo sistema
            color_obj = None
            size_obj = None
            
            if color_value:
                color_obj = ProductOptionValue.objects.filter(
                    option__key='color',
                    value=color_value
                ).first()
            
            if size_value:
                size_obj = ProductOptionValue.objects.filter(
                    option__key='size',
                    value=size_value
                ).first()
            
            # Guardar datos de personalización en comment como JSON
            custom_data = json.dumps({
                'type': 'clothing',
                'color': color_obj.get_display_name() if color_obj else '',
                'color_value': color_obj.value if color_obj else '',
                'color_hex': color_obj.hex_code if color_obj else '',
                'size': size_obj.get_display_name() if size_obj else '',
                'size_value': size_obj.value if size_obj else '',
            })
            
            # Obtener imagen del color
            color_image_url = product.base_image_url
            if color_obj:
                img = product.images.filter(option_value=color_obj).first()
                if img:
                    color_image_url = img.image_url
            
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=str(quantity),
                comment=custom_data,
                step_two_complete=True,
                color=color_obj.get_display_name() if color_obj else '',
                size=size_obj.get_display_name() if size_obj else '',
                color_image_url=color_image_url,
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
    
    except Exception as e:
        return JsonResponse({
            'error': f'Error al agregar al carrito: {str(e)}'
        }, status=500)


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
                cart = Cart.objects.get(pk=cart_id)
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id="Random")
        else:
            cart = Cart.objects.create(cart_id="Random")
            cart_id = cart.pk
        
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
                cart_item = CartItem.objects.get(pk=edit_item_id)
                
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
                    'item_id': cart_item.pk
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
                'item_id': cart_item.pk
            })
            response.set_cookie("cart_id", cart_id)
            response.set_cookie("item_id", cart_item.pk)
            return response
            
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Producto no encontrado'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# ============================================================================
# VISTA: GALERÍA DE PLANTILLAS - VERSIÓN 100% FUNCIONAL
# ============================================================================

def template_gallery_view(request, category_slug, product_slug):
    """
    Muestra la galería de plantillas para un producto específico.
    URL: /<category_slug>/producto/<product_slug>/elegir-diseno/
    """
    try:
        category = Category.objects.get(slug=category_slug, status='active')
        product = Product.objects.get(
            slug=product_slug,
            category=category,
            status='active'
        )
    except (Category.DoesNotExist, Product.DoesNotExist):
        raise Http404("Producto o categoría no encontrada")

    # OBTENER PLANTILLAS DE LA CATEGORÍA (prioridad: subcategoría si existe)
    templates = DesignTemplate.objects.filter(
        category=category
    )

    # Si el producto tiene subcategoría, filtrar por ella también (opcional pero recomendado)
    if product.subcategory:
        templates = templates.filter(
            Q(subcategory=product.subcategory) | Q(subcategory__isnull=True)
        )

    templates = templates.order_by('-is_popular', '-is_new', 'display_order', 'name').distinct()

    context = {
        'product': product,
        'category': category,
        'templates': templates,
        'total_templates': templates.count(),
        # Para los filtros por industria (si usas el campo industry_slug)
        # 'categories': DesignTemplate.objects.filter(category=category).values('industry_slug').distinct(),
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
            
            cart_item = CartItem.objects.get(pk=item_id)
            
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


# ============================================================================
# FOOTER LINKS
# ============================================================================

def quienes_somos(request):
    return render(request, "footer_links/quienes_somos.html")

def como_comprar(request):
    return render(request, "footer_links/como_comprar.html")

def contactanos(request):
    return render(request, "footer_links/contactanos.html")

def legales_privacidad(request):
    return render(request, 'footer_links/legales_privacidad.html')

def legales_terminos(request):
    return render(request, 'footer_links/legales_terminos.html')    

def preguntas_frecuentes(request):
    return render(request, 'footer_links/preguntas_frecuentes.html')


# ============================================================================
# STEP VIEWS (Legacy)
# ============================================================================

class StepOneView(FormView):
    form_class = StepOneForm
    template_name = 'shop/medidas-cantidades.html'
    success_url = 'subir-arte'

    def get_initial(self):
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
                cart = Cart.objects.get(pk=cart_id)
            except ObjectDoesNotExist:
                cart = Cart.objects.create(cart_id="Random")
        else:
            cart = Cart.objects.create(cart_id="Random")
            cart_id = cart.pk
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
        response.set_cookie("item_id", item.pk)
        return response


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
        cart_item = CartItem.objects.get(pk=item_id)
        cart_item.file_a = form.cleaned_data["file_a"]
        cart_item.file_b = form.cleaned_data["file_b"]
        cart_item.comment = form.cleaned_data["comment"]
        cart_item.step_two_complete = True
        cart_item.save()
        response = HttpResponseRedirect(self.get_success_url())
        response.delete_cookie("item_id")
        return response


class StepOneView_Sample(FormView):
    form_class = StepOneForm_Sample
    template_name = 'shop/medidas-cantidades.html'
    success_url = 'subir-arte'

    def get_initial(self):
        initial = super(StepOneView_Sample, self).get_initial()
        initial['size'] = self.request.session.get('size', None)
        initial['sample'] = Sample.objects.get(
            slug=self.kwargs['sample_slug']
        )
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sample'] = Sample.objects.get(
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
                cart = Cart.objects.get(pk=cart_id)
            except ObjectDoesNotExist:
                cart = Cart.objects.create(cart_id="Random")
        else:
            cart = Cart.objects.create(cart_id="Random")
            cart_id = cart.pk
        item = SampleItem.objects.create(
            size=form.cleaned_data.get('size'),
            quantity=2,
            sample=Sample.objects.get(
                slug=self.kwargs['sample_slug']
            ),
            cart=cart
        )

        response = HttpResponseRedirect(self.get_success_url())
        response.set_cookie("cart_id", cart_id)
        response.set_cookie("item_id", item.pk)
        return response


class StepTwoView_Sample(FormView):
    form_class = StepTwoForm_Sample
    template_name = 'shop/subir-arte.html'
    success_url = '/carrito-de-compras/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Sample.objects.get(
            slug=self.kwargs['sample_slug']
        )
        return context

    def form_invalid(self, form):
        print('StepTwoForm is not Valid', form.errors)

    def form_valid(self, form):
        item_id = self.request.COOKIES.get("item_id")
        sample_item = SampleItem.objects.get(pk=item_id)
        sample_item.file_a = form.cleaned_data["file_a"]
        sample_item.file_b = form.cleaned_data["file_b"]
        sample_item.comment = form.cleaned_data["comment"]
        sample_item.step_two_complete = True
        sample_item.save()
        response = HttpResponseRedirect(self.get_success_url())
        response.delete_cookie("item_id")
        return response


# ============================================================================
# AUTH VIEWS
# ============================================================================

def signinView(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
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
        request.session.modified = True
        logout(request)

    response = redirect('signin')
    response.delete_cookie("cart_id")
    response.delete_cookie("cupon")
    return response


def email_confirmation_needed(request):
    return render(request, "accounts/email_confirmation_needed.html")


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        send_email_new_registered_user(user.pk)
        return redirect('shop:home')
    else:
        return HttpResponse('¡Enlace de activación inválido! Intente registrarse nuevamente.')


def send_email_new_registered_user(user_id):
    try:
        profile = Profile.objects.latest('id')
        subject = f"Imprenta Gallito Perú - Nuevo usuario registrado #{profile.pk}"
        to = [f'{profile.user.email}', 'imprentagallito@gmail.com', 'oma.gonzales@gmail.com']
        from_email = 'imprentagallito@imprentagallito.pe'
        user_information = {
            'user_id': profile.user.pk,
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
            Peru.objects.filter(departamento=department_list[0], provincia=province_list[0]).values_list("distrito", flat=True))
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
                    "distrito", flat=True))
        else:
            district_list = set()

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
            user.refresh_from_db()

            profile_form = ProfileForm(district_list, province_list, department_list, request.POST, request.FILES,
                                       instance=user.profile)
            profile_form.full_clean()
            profile_form.save()
            send_email_new_registered_user(user.pk)
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
# API: Obtener colores disponibles (para filtros dinámicos)
# ACTUALIZADO: Usa sistema genérico de opciones
# =============================================================================
def get_available_colors(request):
    """
    API para obtener colores disponibles basados en filtros activos.
    ACTUALIZADO: Usa ProductOptionValue en lugar de ProductColor.
    """
    subcategory_slug = request.GET.get('subcategory', '')
    
    if not subcategory_slug:
        return JsonResponse({'colors': []})
    
    try:
        subcategory = Subcategory.objects.get(slug=subcategory_slug)
    except Subcategory.DoesNotExist:
        return JsonResponse({'colors': []})
    
    # ACTUALIZADO: Query con nuevo sistema
    colors = ProductOptionValue.objects.filter(
        option__key='color',
        product_variants__product__subcategory=subcategory,
        variants__product__status='active',
        is_active=True
    ).distinct().values(
        'value', 'display_name', 'hex_code'
    ).order_by('display_order')
    
    # Formatear para compatibilidad
    colors_list = []
    for c in colors:
        colors_list.append({
            'slug': c['value'],  # Mantener 'slug' para retrocompatibilidad
            'value': c['value'],
            'name': c['display_name'] or c['value'],
            'display_name': c['display_name'] or c['value'],
            'hex_code': c['hex_code'],
        })
    
    return JsonResponse({'colors': colors_list})


# =============================================================================
# API: Obtener colores e imágenes de un producto
# ACTUALIZADO: Usa sistema genérico de opciones
# =============================================================================
def get_product_colors(request, product_slug):
    """
    API para obtener colores e imágenes de un producto específico.
    ACTUALIZADO: Usa ProductOptionValue en lugar de ProductColor.
    """
    try:
        product = Product.objects.get(slug=product_slug)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    
    # Si se pide un color específico
    color_value = request.GET.get('color')
    if color_value:
        # Buscar la imagen para este color (option_value)
        image = ProductImage.objects.filter(
            product=product,
            option_value__value=color_value
        ).first()
        
        if image:
            return JsonResponse({'image': image.image_url})
        else:
            return JsonResponse({'image': product.base_image_url or ''})
    
    # Si no se pide color específico, retornar todos
    colors_data = []
    available_colors = product.get_colors()  # Usa método de retrocompatibilidad
    
    for color_val in available_colors:
        # Buscar imagen para este color
        image = ProductImage.objects.filter(
            product=product,
            option_value=color_val
        ).first()
        
        colors_data.append({
            'slug': color_val.value,  # Retrocompatibilidad
            'value': color_val.value,
            'name': color_val.get_display_name(),
            'display_name': color_val.get_display_name(),
            'hex_code': color_val.hex_code,
            'image_url': image.image_url if image else product.base_image_url,
        })
    
    return JsonResponse({
        'product_slug': product_slug,
        'product_name': product.name,
        'colors': colors_data,
    })


# =============================================================================
# API: Obtener todas las opciones de un producto
# NUEVO: Para el sistema genérico de opciones
# =============================================================================
def get_product_options(request, product_slug):
    """
    API para obtener todas las opciones disponibles de un producto.
    Retorna estructura completa para cualquier tipo de opción.
    """
    try:
        product = Product.objects.get(slug=product_slug)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    
    # Obtener todas las opciones usando el método del modelo
    variant_options = product.get_variant_options()
    
    # Formatear para JSON
    options_data = {}
    for key, data in variant_options.items():
        options_data[key] = {
            'option_name': data['option'].name,
            'option_key': data['option'].key,
            'values': []
        }
        for val in data['values']:
            val_data = {
                'value': val.value,
                'display_name': val.get_display_name(),
                'additional_price': float(val.additional_price) if val.additional_price else 0,
            }
            # Agregar campos opcionales si existen
            if val.hex_code:
                val_data['hex_code'] = val.hex_code
            if val.image:
                val_data['image'] = val.image.url
            
            options_data[key]['values'].append(val_data)
    
    return JsonResponse({
        'product_slug': product_slug,
        'product_name': product.name,
        'options': options_data,
    })


# =============================================================================
# API: Agregar producto al carrito (genérico para todos los tipos)
# ACTUALIZADO: Usa sistema genérico de opciones
# =============================================================================

@csrf_exempt
def add_to_cart_api(request):
    """
    API genérica para agregar productos al carrito.
    ACTUALIZADO: Detecta tipo de producto usando is_clothing_product().
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        product_slug = request.POST.get('product_slug')
        quantity = int(request.POST.get('quantity', 1))
        
        if not product_slug:
            return JsonResponse({'error': 'Falta el producto'}, status=400)
        
        product = get_object_or_404(Product, slug=product_slug)
        
        # ACTUALIZADO: Detectar tipo usando método de retrocompatibilidad
        is_clothing = product.is_clothing_product()
        
        if is_clothing:
            # Producto de ropa - requiere color y talla
            color_value = request.POST.get('color_slug') or request.POST.get('color')
            size_value = request.POST.get('size_slug') or request.POST.get('size')
            
            if not all([color_value, size_value]):
                return JsonResponse({
                    'error': 'Productos de ropa requieren color y talla'
                }, status=400)
            
            # ACTUALIZADO: Obtener valores usando nuevo sistema
            color_obj = ProductOptionValue.objects.filter(
                option__key='color',
                value=color_value
            ).first()
            
            size_obj = ProductOptionValue.objects.filter(
                option__key='size',
                value=size_value
            ).first()
            
            if not color_obj:
                return JsonResponse({'error': 'Color no encontrado'}, status=400)
            
            if not size_obj:
                return JsonResponse({'error': 'Talla no encontrada'}, status=400)
            
            # Verificar disponibilidad en el producto
            product_colors = product.get_colors()
            product_sizes = product.get_sizes()
            
            if color_obj not in product_colors:
                return JsonResponse({'error': 'Color no disponible para este producto'}, status=400)
            
            if size_obj not in product_sizes:
                return JsonResponse({'error': 'Talla no disponible para este producto'}, status=400)
            
            # Obtener la imagen del color
            product_image = ProductImage.objects.filter(
                product=product,
                option_value=color_obj
            ).first()
            
            color_image_url = product_image.image_url if product_image else product.base_image_url
            
            # Obtener archivo de diseño si existe
            design_file = request.FILES.get('design_file')
            
            # Obtener o crear carrito
            cart_id = request.COOKIES.get('cart_id')
            
            if cart_id:
                try:
                    cart = Cart.objects.get(pk=cart_id)
                except Cart.DoesNotExist:
                    cart = Cart.objects.create()
            else:
                cart = Cart.objects.create()
            
            # Buscar CartItem existente con mismo producto, color y talla
            cart_item = CartItem.objects.filter(
                cart=cart,
                product=product,
                color=color_obj.get_display_name(),
                size=size_obj.get_display_name()
            ).first()
            
            if cart_item:
                # Actualizar cantidad del item existente
                cart_item.quantity = cart_item.quantity + quantity
                cart_item.color_image_url = color_image_url
                
                if design_file:
                    if cart_item.design_file:
                        cart_item.design_file.delete(save=False)
                    cart_item.design_file = design_file
                
                cart_item.save()
            else:
                # Crear nuevo CartItem
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    color=color_obj.get_display_name(),
                    size=size_obj.get_display_name(),
                    quantity=quantity,
                    color_image_url=color_image_url,
                    design_file=design_file
                )
            
            item_info = {
                'product_name': product.name,
                'color': color_obj.get_display_name(),
                'color_value': color_obj.value,
                'size': size_obj.get_display_name(),
                'size_value': size_obj.value,
                'quantity': cart_item.quantity,
                'color_image_url': color_image_url,
                'has_design_file': bool(cart_item.design_file)
            }
            
        else:
            # Producto de impresión - manejo diferente
            return JsonResponse({
                'error': 'Productos de impresión usan un flujo diferente'
            }, status=400)
        
        # Calcular totales
        cart_items = CartItem.objects.filter(cart=cart)
        cart_total = sum(item.sub_total for item in cart_items)
        cart_count = sum(item.get_quantity_int() for item in cart_items)
        
        response_data = {
            'success': True,
            'message': f'{product.name} agregado al carrito',
            'cart_count': cart_count,
            'cart_total': float(cart_total),
            'item': item_info
        }
        
        response = JsonResponse(response_data)
        response.set_cookie('cart_id', cart.pk, max_age=30*24*60*60)
        return response
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': f'Error al agregar al carrito: {str(e)}'
        }, status=500)
