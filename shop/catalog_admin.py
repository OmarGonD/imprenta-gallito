"""
Configuración de Django Admin para el sistema de catálogo personalizable

MIGRATION NOTE (2024):
- Now imports Category, Subcategory, Product from shop.models
- Previously imported from catalog_models.py (deprecated)
- Admin class names updated to match new model names
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count

# Import from models.py (migrated from catalog_models.py)
from .models import (
    Category,
    Subcategory,
    Product,
    VariantType,
    VariantOption,
    ProductVariantType,
    PriceTier
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for Category (formerly CatalogCategory)"""
    list_display = ['name', 'slug', 'status', 'display_order', 'product_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'slug', 'description']
    ordering = ['display_order', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Visualización', {
            'fields': ('image_url', 'display_order', 'status')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def product_count(self, obj):
        count = obj.catalog_products.filter(status='active').count()
        return format_html('<strong>{}</strong> productos', count)
    product_count.short_description = 'Productos'


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    """Admin for Subcategory (formerly CatalogSubcategory)"""
    list_display = ['name', 'category', 'slug', 'display_order', 'product_count', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'slug', 'description', 'category__name']
    ordering = ['category', 'display_order', 'name']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['category']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Visualización', {
            'fields': ('image_url', 'display_order')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def product_count(self, obj):
        count = obj.catalog_products.filter(status='active').count()
        return count
    product_count.short_description = 'Productos'


class PriceTierInline(admin.TabularInline):
    model = PriceTier
    extra = 1
    fields = ['min_quantity', 'max_quantity', 'unit_price', 'discount_percentage']


class ProductVariantTypeInline(admin.TabularInline):
    model = ProductVariantType
    extra = 1
    autocomplete_fields = ['variant_type']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'subcategory', 'status', 'price_range', 'variant_count']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['name', 'slug', 'sku', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at', 'price_range_display']
    autocomplete_fields = ['category', 'subcategory']
    inlines = [ProductVariantTypeInline, PriceTierInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'sku', 'description')
        }),
        ('Categorización', {
            'fields': ('category', 'subcategory')
        }),
        ('Visualización', {
            'fields': ('base_image_url', 'status')
        }),
        ('Información de Precios', {
            'fields': ('price_range_display',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_range(self, obj):
        min_price, max_price = obj.get_price_range()
        if min_price == max_price:
            return f'S/{min_price}'
        return f'S/{min_price} - S/{max_price}'
    price_range.short_description = 'Rango de Precio'
    
    def price_range_display(self, obj):
        tiers = obj.price_tiers.all()
        if not tiers:
            return 'No hay precios configurados'
        
        html = '<table style="width:100%"><tr><th>Cantidad</th><th>Precio</th><th>Descuento</th></tr>'
        for tier in tiers:
            html += f'<tr><td>{tier.get_range_display()}</td><td>S/{tier.unit_price}</td><td>{tier.discount_percentage}%</td></tr>'
        html += '</table>'
        return format_html(html)
    price_range_display.short_description = 'Niveles de Precio'
    
    def variant_count(self, obj):
        count = obj.product_variant_types.count()
        return format_html('<span style="color: #417690; font-weight: bold;">{}</span> variantes', count)
    variant_count.short_description = 'Variantes'


class VariantOptionInline(admin.TabularInline):
    model = VariantOption
    extra = 1
    fields = ['name', 'slug', 'additional_price', 'display_order']


@admin.register(VariantType)
class VariantTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_required', 'allows_multiple', 'display_order', 'option_count']
    list_filter = ['is_required', 'allows_multiple']
    search_fields = ['name', 'slug', 'description']
    ordering = ['display_order', 'name']
    inlines = [VariantOptionInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Configuración', {
            'fields': ('is_required', 'allows_multiple', 'display_order', 'applies_to')
        }),
    )
    
    def option_count(self, obj):
        count = obj.options.count()
        return f'{count} opciones'
    option_count.short_description = 'Opciones'


@admin.register(VariantOption)
class VariantOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'variant_type', 'additional_price', 'display_order', 'has_image']
    list_filter = ['variant_type']
    search_fields = ['name', 'slug', 'description', 'variant_type__name']
    ordering = ['variant_type', 'display_order', 'name']
    autocomplete_fields = ['variant_type']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'variant_type', 'description')
        }),
        ('Precio y Visualización', {
            'fields': ('additional_price', 'image_url', 'display_order')
        }),
    )
    
    def has_image(self, obj):
        if obj.image_url:
            return format_html('✓')
        return format_html('✗')
    has_image.short_description = 'Imagen'


@admin.register(PriceTier)
class PriceTierAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity_range', 'unit_price', 'discount_percentage']
    list_filter = ['product__category', 'discount_percentage']
    search_fields = ['product__name', 'product__sku']
    ordering = ['product', 'min_quantity']
    autocomplete_fields = ['product']
    
    def quantity_range(self, obj):
        return obj.get_range_display()
    quantity_range.short_description = 'Rango de Cantidad'


@admin.register(ProductVariantType)
class ProductVariantTypeAdmin(admin.ModelAdmin):
    list_display = ['product', 'variant_type']
    list_filter = ['variant_type']
    search_fields = ['product__name', 'variant_type__name']
    autocomplete_fields = ['product', 'variant_type']


# Personalización del admin site
admin.site.site_header = "Imprenta Gallito - Administración de Catálogo"
admin.site.site_title = "Admin Catálogo"
admin.site.index_title = "Sistema de Catálogo Personalizable"
