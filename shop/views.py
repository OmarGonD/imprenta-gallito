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
    print(f"🔍 Vista ejecutada: Entra a Category View")
    try:
        category = Category.objects.get(slug=category_slug, status='active')
    except Category.DoesNotExist:
        raise Http404("Categoría no encontrada")
    
    
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


def product_detail(request, category_slug, subcategory_slug, product_slug):
    """
    Vista unificada para detalle de producto (Ropa/Imprenta) - VERSIÓN FINAL CORREGIDA
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
    # 2. PROCESAR PRECIOS DE FORMA SEGURA (CRÍTICO)
    # -------------------------------------------------------------------------
    
    # Obtener starting_price y base_price, asegurando que nunca sean None
    raw_starting_price = product.starting_price  # Puede ser None
    raw_base_price = product.base_price  # Puede ser None
    
    # Estrategia de fallback para precios
    if raw_starting_price is not None:
        safe_starting_price = float(raw_starting_price)
    elif raw_base_price is not None:
        safe_starting_price = float(raw_base_price)
    else:
        # Último recurso: buscar en el primer tier
        first_tier = product.price_tiers.order_by('min_quantity').first()
        safe_starting_price = float(first_tier.unit_price) if first_tier else 0.0
    
    # Base price con el mismo fallback
    if raw_base_price is not None:
        safe_base_price = float(raw_base_price)
    elif raw_starting_price is not None:
        safe_base_price = float(raw_starting_price)
    else:
        safe_base_price = safe_starting_price
    
    # -------------------------------------------------------------------------
    # 3. INICIALIZAR CONTEXTO BASE CON VALORES SEGUROS
    # -------------------------------------------------------------------------
    
    context = {
        'category': category,
        'product': product,
        'tiers': [],
        'related_products': None,
        'template_name': 'shop/product_detail.html',
        # Valores seguros para JavaScript (siempre float, nunca None)
        'pricing_tiers': [],
        'images_by_color': '{}',
        'selected_color_slug': '',
        'base_image_url': product.base_image_url or '',
        # Precios seguros como float para evitar problemas de localización
        'safe_starting_price': safe_starting_price,
        'safe_base_price': safe_base_price,
    }

    # -------------------------------------------------------------------------
    # 4. LÓGICA PARA ROPA-BOLSOS
    # -------------------------------------------------------------------------

    if category_slug == 'ropa-bolsos':
        
        subcategory = product.subcategory

        # TALLAS Y PRECIOS
        available_sizes = product.available_sizes.filter(is_active=True).order_by('display_order')
        pricing_tiers_qs = product.price_tiers.all().order_by('min_quantity')
        
        # ✅ CONVERTIR PRICING TIERS A DICCIONARIOS CON VALORES FLOAT
        pricing_tiers_list = []
        for tier in pricing_tiers_qs:
            pricing_tiers_list.append({
                'min_quantity': int(tier.min_quantity),
                'max_quantity': int(tier.max_quantity),
                'unit_price': float(tier.unit_price),  # Convertir a float
                'discount_percentage': tier.discount_percentage,
            })
        
        # Si no hay tiers, crear uno por defecto
        if not pricing_tiers_list:
            pricing_tiers_list = [{
                'min_quantity': 1,
                'max_quantity': 999999,
                'unit_price': safe_starting_price,
                'discount_percentage': 0,
            }]
        
        context.update({
            'available_sizes': available_sizes,
            'pricing_tiers': pricing_tiers_list,  # Lista de diccionarios
            'pricing_tiers_json': json.dumps(pricing_tiers_list),  # ✅ JSON string para JavaScript
            'pricing_tiers_qs': pricing_tiers_qs,  # Queryset original para el template HTML
            'subcategory': subcategory,
            'category_slug': subcategory.slug,
        })
        
        # PRODUCTOS RELACIONADOS
        context['related_products'] = Product.objects.filter(
            subcategory=subcategory,
            status='active'
        ).exclude(pk=product.pk)[:4]
        
        # MANEJO DE COLORES E IMÁGENES
        selected_color_slug = request.GET.get('color', '')
        available_colors = product.available_colors.filter(is_active=True).order_by('display_order')
        
        # Determinar selected_color
        selected_color = None
        if selected_color_slug:
            selected_color = available_colors.filter(slug=selected_color_slug).first()
        if not selected_color and available_colors.exists():
            selected_color = available_colors.first()
            selected_color_slug = selected_color.slug
            
        context.update({
            'available_colors': available_colors,
            'selected_color': selected_color,
            'selected_color_slug': selected_color_slug or '',
        })

        # OBTENER Y ORGANIZAR IMÁGENES POR COLOR
        images_by_color = {}
        base_image_url = product.base_image_url or ''
        
        all_images = product.images.select_related('color').order_by(
            'color__slug', '-is_primary', 'display_order'
        )
        
        for img in all_images:
            color_key = img.color.slug if img.color else 'default'
            if color_key not in images_by_color:
                images_by_color[color_key] = []
            
            images_by_color[color_key].append({
                'image': img.image_url or '',
                'is_primary': img.is_primary,
                'alt_text': img.alt_text or product.name
            })
        
        # Determinar imagen principal
        if selected_color:
            primary_image = product.images.filter(
                color=selected_color, 
                is_primary=True
            ).first()
            
            if primary_image:
                base_image_url = primary_image.image_url or base_image_url
            else:
                first_image = product.images.filter(color=selected_color).first()
                if first_image:
                    base_image_url = first_image.image_url or base_image_url

        context.update({
            'base_image_url': base_image_url,
            'images_by_color': json.dumps(images_by_color),
        })

        context['template_name'] = 'shop/clothing_product_detail.html'
        
    else:
        # -------------------------------------------------------------------------
        # 5. LÓGICA PARA IMPRENTA Y OTROS
        # -------------------------------------------------------------------------
        
        pricing_service = PricingService()
        all_tiers = pricing_service.price_tiers.get(product.slug, [])
        
        if all_tiers:
            base_price = all_tiers[0]['unit_price']
            for tier in all_tiers:
                tier['savings'] = base_price - tier['unit_price']
        
        context['tiers'] = all_tiers
        context['variant_types'] = product.get_available_variant_types()
        
        # PRODUCTOS RELACIONADOS
        context['related_products'] = Product.objects.filter(
            category=category,
            status='active'
        ).exclude(pk=product.pk)[:4]
        
        # Datos adicionales
        context.update({
            'product_images': product.images.all().order_by('display_order'),
            'has_colors': product.has_colors(),
            'has_sizes': product.has_sizes(),
        })
    
    # -------------------------------------------------------------------------
    # 6. DEBUGGING (TEMPORAL - REMOVER EN PRODUCCIÓN)
    # -------------------------------------------------------------------------
    
    print("\n" + "="*70)
    print(f"🔍 DEBUGGING: {product.name}")
    print("="*70)
    print(f"  Base Price (raw): {raw_base_price} (type: {type(raw_base_price)})")
    print(f"  Starting Price (raw): {raw_starting_price} (type: {type(raw_starting_price)})")
    print(f"  Base Price (safe): {safe_base_price} (type: {type(safe_base_price)})")
    print(f"  Starting Price (safe): {safe_starting_price} (type: {type(safe_starting_price)})")
    print(f"  Selected Color: '{context.get('selected_color_slug', 'N/A')}'")
    print(f"  Images by Color: {len(json.loads(context['images_by_color']))} colores")
    print(f"  Pricing Tiers: {len(context['pricing_tiers'])} tiers")
    
    if context['pricing_tiers']:
        print(f"\n  📊 Tiers procesados:")
        for i, tier in enumerate(context['pricing_tiers'][:3]):
            print(f"    Tier {i}: min={tier['min_quantity']}, "
                  f"max={tier['max_quantity']}, "
                  f"price={tier['unit_price']} (type: {type(tier['unit_price'])})")
    
    print("="*70 + "\n")
    
    # -------------------------------------------------------------------------
    # 7. RENDERIZADO FINAL
    # -------------------------------------------------------------------------
    
    return render(request, context['template_name'], context)


# ============================================================================
# ROPA Y BOLSOS - VISTAS REFACTORIZADAS (Usando sistema unificado)
# ============================================================================

# =============================================================================
# VISTAS ESPECÍFICAS PARA ROPA/BOLSOS (MODIFICADAS POR EL USUARIO)
# =============================================================================

def clothing_category(request):
    """
    Vista de categoría para 'ropa-bolsos/' (Nivel 1).
    Renderiza clothing_category.html.
    
    Esta vista no recibe argumentos de slug porque la URL está fijada en 'ropa-bolsos/'.
    """
    # Busca la categoría 'ropa-bolsos'
    try:
        category = Category.objects.get(slug='ropa-bolsos')
    except Category.DoesNotExist:
        # En caso de que el slug 'ropa-bolsos' no exista en la base de datos
        raise Http404("La categoría 'Ropa y Bolsos' no fue encontrada.")
        
    # Obtener subcategorías relevantes (polos, camisas, etc.)
    subcategories = Subcategory.objects.filter(category=category)
    
    context = {
        'category': category,
        'subcategories': subcategories,
    }
    return render(request, 'shop/clothing_category.html', context)

    return render(request, 'shop/clothing_category.html', context)
    
from django.shortcuts import render, get_object_or_404
from .models import Subcategory, Product # Asume que también tienes un modelo Product

def clothing_subcategory(request, category_slug, subcategory_slug):
    """
    Muestra los productos que pertenecen a una subcategoría específica,
    validando que la subcategoría pertenezca a la categoría dada en la URL.
    """
    print(f"🔍 Vista ejecutada: {category_slug}/{subcategory_slug}")
    # 1. Recuperar la Subcategoría o lanzar 404 (No Subcategory matches the given query)
    #    Aquí es donde la combinación de slugs debe ser correcta.
    #    'category__slug' filtra a través de la relación de clave foránea.
    try:
        subcategory = get_object_or_404(
            Subcategory, 
            slug=subcategory_slug,           # Ej: 'polos'
            category__slug=category_slug     # Ej: 'ropa-bolsos'
        )
    except Exception as e:
        # Aunque get_object_or_404 debería manejarlo, este bloque es para depuración
        print(f"Error al buscar subcategoría: {e}")
        # Lanza el 404 si no se encuentra
        raise
        
    # 2. Obtener los Productos relacionados
    #    Asumiendo que tu modelo Product tiene una ForeignKey a Subcategory
    #    llamada 'subcategory' o que usas el related_name
    products = Product.objects.filter(subcategory=subcategory,status='active')

    # 3. Preparar el Contexto y Renderizar
    context = {
        'category': subcategory.category,
        'subcategory': subcategory,
        'products': products,
        # Puedes añadir los slugs al contexto por si los necesitas en la plantilla
        'current_category_slug': category_slug, 
        'current_subcategory_slug': subcategory_slug,
    }

    return render(request, 'shop/clothing_subcategory.html', context)


    



# =============================================================================
# API: Agregar producto de ropa al carrito (con HTMX)
# =============================================================================
@csrf_exempt
def add_clothing_to_cart(request):
    """
    API para agregar productos de ropa al carrito.
    Acepta: product_slug, color_slug, size_slug, quantity
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        # Obtener datos del POST
        product_slug = request.POST.get('product_slug')
        color_slug = request.POST.get('color_slug')
        size_slug = request.POST.get('size_slug')
        quantity = int(request.POST.get('quantity', 1))
        
        # Validar datos requeridos
        if not all([product_slug, color_slug, size_slug]):
            return JsonResponse({
                'error': 'Faltan datos requeridos (producto, color, talla)'
            }, status=400)
        
        # Obtener el producto
        product = get_object_or_404(Product, slug=product_slug)
        
        # Obtener color y talla
        color = get_object_or_404(ProductColor, slug=color_slug)
        size = get_object_or_404(ProductSize, slug=size_slug)
        
        # Verificar que el color y talla estén disponibles para este producto
        if color not in product.available_colors.all():
            return JsonResponse({'error': 'Color no disponible'}, status=400)
        
        if size not in product.available_sizes.all():
            return JsonResponse({'error': 'Talla no disponible'}, status=400)
        
        # Calcular precio basado en cantidad (usando PriceTiers)
        unit_price = product.base_price  # Default
        
        # Buscar el tier correspondiente
        price_tier = product.price_tiers.filter(
            min_quantity__lte=quantity,
            max_quantity__gte=quantity
        ).first()
        
        if price_tier:
            unit_price = price_tier.unit_price
        
        # Obtener o crear el carrito
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(
                user=request.user,
                status='active'
            )
        else:
            # Para usuarios anónimos, usar sesión
            cart_id = request.session.get('cart_id')
            if cart_id:
                cart = Cart.objects.filter(id=cart_id, status='active').first()
                if not cart:
                    cart = Cart.objects.create(status='active')
                    request.session['cart_id'] = cart.pk
            else:
                cart = Cart.objects.create(status='active')
                request.session['cart_id'] = cart.pk
        
        # Buscar si ya existe un item con el mismo producto, color y talla
        cart_item = CartItem.objects.filter(
            cart=cart,
            product=product,
            color=color,
            size=size
        ).first()
        
        if cart_item:
            # Actualizar cantidad
            cart_item.quantity += quantity
            cart_item.unit_price = unit_price
            cart_item.save()
        else:
            # Crear nuevo item
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                color=color,
                size=size,
                quantity=quantity,
                unit_price=unit_price
            )
        
        # Calcular totales del carrito
        cart_items = cart.items.all()
        cart_total = sum(item.get_total() for item in cart_items)
        cart_count = sum(item.quantity for item in cart_items)
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} agregado al carrito',
            'cart_count': cart_count,
            'cart_total': float(cart_total),
            'item': {
                'product_name': product.name,
                'color': color.name,
                'size': size.name,
                'quantity': cart_item.quantity,
                'unit_price': float(unit_price),
                'total': float(cart_item.get_total()),
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error al agregar al carrito: {str(e)}'
        }, status=500)


@csrf_exempt
def add_clothing_to_cart(request):
    """AJAX endpoint para agregar producto de ropa al carrito."""
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
# TARJETAS DE PRESENTACIÓN
# ============================================================================


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
            cart_item = CartItem.objects.get(pk=edit_item_id)
            edit_item_data = json.dumps({
                'id': cart_item.pk,
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
                cart = Cart.objects.get(pk=cart_id)
            except ObjectDoesNotExist:
                # supplied ID doesn't match a Cart from your BD
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

        cart_item = CartItem.objects.get(pk=item_id)
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
                cart = Cart.objects.get(pk=cart_id)
            except ObjectDoesNotExist:
                # supplied ID doesn't match a Cart from your BD
                cart = Cart.objects.create(cart_id="Random")
        else:
            cart = Cart.objects.create(cart_id="Random")
            cart_id = cart.pk
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
        response.set_cookie("item_id", item.pk)
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

        sample_item = SampleItem.objects.get(pk=item_id)
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
        print(user.pk)
        print(type(user.pk))
        print("############")
        send_email_new_registered_user(user.pk)
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
            send_email_new_registered_user(user.pk) # send email to admin when a new user registers himself
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
    
    Si se pasa ?color=slug, retorna solo la imagen de ese color:
        { "image": "url_de_la_imagen" }
    
    Si no se pasa color, retorna todos los colores:
        { "product_slug": "...", "colors": [...] }
    """
    try:
        product = Product.objects.get(slug=product_slug)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    
    # Si se pide un color específico, retornar solo la imagen
    color_slug = request.GET.get('color')
    if color_slug:
        # Buscar la imagen para este color
        image = ProductImage.objects.filter(
            product=product,
            color__slug=color_slug
        ).first()
        
        if image:
            return JsonResponse({'image': image.image_url})
        else:
            # Si no hay imagen específica para el color, retornar la base
            return JsonResponse({'image': product.base_image_url or ''})
    
    # Si no se pide color específico, retornar todos
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
# API: Agregar producto al carrito (genérico para todos los tipos)
# =============================================================================
@csrf_exempt
def add_to_cart_api(request):
    """
    API genérica para agregar productos al carrito.
    Detecta automáticamente si es producto de ropa o de impresión.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        product_slug = request.POST.get('product_slug')
        quantity = int(request.POST.get('quantity', 1))
        
        if not product_slug:
            return JsonResponse({'error': 'Falta el producto'}, status=400)
        
        product = get_object_or_404(Product, slug=product_slug)
        
        # Detectar tipo de producto
        is_clothing = product.available_colors.exists() or product.available_sizes.exists()
        
        if is_clothing:
            # Producto de ropa - requiere color y talla
            color_slug = request.POST.get('color_slug')
            size_slug = request.POST.get('size_slug')
            
            if not all([color_slug, size_slug]):
                return JsonResponse({
                    'error': 'Productos de ropa requieren color y talla'
                }, status=400)
            
            color = get_object_or_404(ProductColor, slug=color_slug)
            size = get_object_or_404(ProductSize, slug=size_slug)
            
            if color not in product.available_colors.all():
                return JsonResponse({'error': 'Color no disponible'}, status=400)
            
            if size not in product.available_sizes.all():
                return JsonResponse({'error': 'Talla no disponible'}, status=400)
            
            # Obtener o crear carrito
            cart_id = request.COOKIES.get('cart_id')
            
            if cart_id:
                try:
                    cart = Cart.objects.get(pk=cart_id)
                except Cart.DoesNotExist:
                    cart = Cart.objects.create()
            else:
                cart = Cart.objects.create()
            
            # Buscar o crear CartItem
            cart_item = CartItem.objects.filter(
                cart=cart,
                product=product,
                clothing_color=color,
                clothing_size=size
            ).first()
            
            if cart_item:
                cart_item.clothing_quantity = (cart_item.clothing_quantity or 0) + quantity
                cart_item.save()
            else:
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    clothing_color=color,
                    clothing_size=size,
                    clothing_quantity=quantity
                )
            
            item_info = {
                'product_name': product.name,
                'color': color.name,
                'size': size.name,
                'quantity': cart_item.clothing_quantity,
            }
            
        else:
            # Producto de impresión - manejo diferente
            # (implementar según tus necesidades)
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
        return JsonResponse({
            'error': f'Error al agregar al carrito: {str(e)}'
        }, status=500)


# =============================================================================
# COMPATIBILIDAD: Mantener las vistas específicas de ropa
# =============================================================================



def add_clothing_to_cart(request):
    """Vista específica para ropa - redirige a API genérica"""
    return add_to_cart_api(request)