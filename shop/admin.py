from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Product, Profile, Peru, Category, Subcategory,
    VariantType, VariantOption, ProductVariantType, PriceTier,
    DesignTemplate  # NUEVO
)


# ===========================
# CATALOG SYSTEM ADMIN
# ===========================

class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1
    prepopulated_fields = {'slug': ('name',)}
    fields = ['slug', 'name', 'description', 'display_style', 'display_order']  # AGREGADO display_style


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['slug', 'name', 'category_type_badge', 'display_order', 'status', 'products_count', 'created_at']
    list_editable = ['display_order', 'status']
    list_filter = ['status', 'category_type', 'created_at']  # AGREGADO category_type
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug', 'description']
    inlines = [SubcategoryInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('slug', 'name', 'description')
        }),
        ('Imagen', {
            'fields': ('image_url',)
        }),
        ('Tipo y Visualización', {  # NUEVA SECCIÓN
            'fields': ('category_type',),
            'description': 'Define cómo se renderiza esta categoría en el frontend'
        }),
        ('Configuración', {
            'fields': ('display_order', 'status')
        }),
    )
    
    def category_type_badge(self, obj):
        """Muestra el tipo de categoría con un badge colorido"""
        colors = {
            'quality_tiers': '#8b5cf6',  # Violeta
            'product_types': '#0ea5e9',  # Azul
            'formats': '#10b981',        # Verde
            'services': '#f59e0b',       # Naranja
            'occasions': '#ec4899',      # Rosa
            'standard': '#6b7280',       # Gris
        }
        color = colors.get(obj.category_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_category_type_display()
        )
    category_type_badge.short_description = 'Tipo'
    category_type_badge.admin_order_field = 'category_type'
    
    def products_count(self, obj):
        """Cuenta productos activos en esta categoría"""
        count = obj.products.filter(status='active').count()
        return format_html(
            '<span style="background-color: #e5e7eb; padding: 2px 8px; '
            'border-radius: 10px; font-size: 12px;">{}</span>',
            count
        )
    products_count.short_description = 'Productos'


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['slug', 'name', 'category', 'display_style_badge', 'display_order', 'created_at']
    list_editable = ['display_order']
    list_filter = ['category', 'display_style', 'created_at']  # AGREGADO display_style
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug', 'description']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('slug', 'name', 'category', 'description')
        }),
        ('Imagen', {
            'fields': ('image_url',)
        }),
        ('Visualización', {  # NUEVA SECCIÓN
            'fields': ('display_style',),
            'description': 'Cómo se muestra esta subcategoría en el frontend'
        }),
        ('Configuración', {
            'fields': ('display_order',)
        }),
    )
    
    def display_style_badge(self, obj):
        """Muestra el estilo de visualización con un badge"""
        icons = {
            'tab': '📑',
            'circle': '⭕',
            'card': '🃏',
            'vertical_card': '📋',
        }
        icon = icons.get(obj.display_style, '📄')
        return format_html(
            '<span title="{}">{} {}</span>',
            obj.get_display_style_display(),
            icon,
            obj.get_display_style_display()
        )
    display_style_badge.short_description = 'Estilo'
    display_style_badge.admin_order_field = 'display_style'


# ===========================
# DESIGN TEMPLATES ADMIN (NUEVO)
# ===========================

@admin.register(DesignTemplate)
class DesignTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'slug', 'name', 'category', 'subcategory', 
        'thumbnail_preview', 'is_popular', 'is_new', 'display_order'
    ]
    list_editable = ['is_popular', 'is_new', 'display_order']
    list_filter = ['category', 'subcategory', 'is_popular', 'is_new']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ['category', 'subcategory']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('slug', 'name', 'description')
        }),
        ('Categorización', {
            'fields': ('category', 'subcategory'),
            'description': 'Asocia este template a una categoría y subcategoría'
        }),
        ('Imágenes', {
            'fields': ('thumbnail_url', 'preview_url'),
            'description': 'URLs de las imágenes del template'
        }),
        ('Estado y Orden', {
            'fields': ('is_popular', 'is_new', 'display_order')
        }),
    )
    
    def thumbnail_preview(self, obj):
        """Muestra una preview del thumbnail"""
        if obj.thumbnail_url:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; '
                'border-radius: 4px; border: 1px solid #ddd;" />',
                obj.thumbnail_url
            )
        return format_html(
            '<span style="color: #999; font-size: 11px;">Sin imagen</span>'
        )
    thumbnail_preview.short_description = 'Preview'
    
    def get_queryset(self, request):
        """Optimiza las queries"""
        return super().get_queryset(request).select_related('category', 'subcategory')


# ===========================
# PRODUCT ADMIN
# ===========================

class PriceTierInline(admin.TabularInline):
    model = PriceTier
    extra = 3
    fields = ['min_quantity', 'max_quantity', 'unit_price', 'discount_percentage']


class ProductVariantTypeInline(admin.TabularInline):
    model = ProductVariantType
    extra = 1
    fields = ['variant_type']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['slug', 'name', 'category', 'subcategory', 'sku', 'status', 'created_at']
    list_editable = ['status']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug', 'sku', 'description']
    list_filter = ['category', 'subcategory', 'status', 'created_at']
    inlines = [PriceTierInline, ProductVariantTypeInline]
    autocomplete_fields = ['category', 'subcategory']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('slug', 'name', 'sku', 'description')
        }),
        ('Categorización', {
            'fields': ('category', 'subcategory')
        }),
        ('Imagen', {
            'fields': ('base_image_url',)
        }),
        ('Estado', {
            'fields': ('status',)
        }),
    )


@admin.register(VariantType)
class VariantTypeAdmin(admin.ModelAdmin):
    list_display = ['slug', 'name', 'is_required', 'allows_multiple', 'display_order']
    list_editable = ['is_required', 'allows_multiple', 'display_order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    list_filter = ['is_required', 'allows_multiple']


@admin.register(VariantOption)
class VariantOptionAdmin(admin.ModelAdmin):
    list_display = ['slug', 'name', 'variant_type', 'additional_price', 'display_order']
    list_editable = ['additional_price', 'display_order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    list_filter = ['variant_type']


@admin.register(PriceTier)
class PriceTierAdmin(admin.ModelAdmin):
    list_display = ['product', 'min_quantity', 'max_quantity', 'unit_price', 'discount_percentage']
    list_filter = ['product__category']
    search_fields = ['product__name']


# ===========================
# PROFILE & PERU
# ===========================

admin.site.register(Peru)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'dni']


admin.site.register(Profile, ProfileAdmin)


# ===========================
# CLOTHING & BAGS ADMIN
# ===========================




# ===========================
# ADMIN SITE CUSTOMIZATION
# ===========================

admin.site.site_header = "Imprenta Gallito - Administración"
admin.site.site_title = "Gallito Admin"
admin.site.index_title = "Panel de Administración"
