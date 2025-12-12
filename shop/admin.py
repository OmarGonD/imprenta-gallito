from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Subcategory, Product,
    ProductOption, ProductOptionValue, ProductVariant,
    ProductImage, PriceTier,
    DesignTemplate, Profile, Peru
)

# ============================================================
# CATEGORY / SUBCATEGORY
# ============================================================

class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1
    prepopulated_fields = {'slug': ('name',)}
    fields = ['slug', 'name', 'description', 'display_style', 'display_order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['slug', 'name', 'category_type', 'display_order', 'status', 'products_count']
    list_editable = ['display_order', 'status']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug']
    list_filter = ['status', 'category_type']
    inlines = [SubcategoryInline]

    def products_count(self, obj):
        return obj.products.filter(status='active').count()
    products_count.short_description = "Productos activos"


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['slug', 'name', 'category', 'display_style', 'display_order']
    list_editable = ['display_order']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['category', 'display_style']
    search_fields = ['name', 'slug']


# ============================================================
# PRODUCT OPTION SYSTEM
# ============================================================

@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ['key', 'name', 'selection_type', 'is_required', 'display_order']
    list_editable = ['is_required', 'display_order']
    search_fields = ['key', 'name']


@admin.register(ProductOptionValue)
class ProductOptionValueAdmin(admin.ModelAdmin):
    list_display = [
        'option', 'value', 'display_name',
        'hex_code', 'additional_price', 'display_order', 'is_active'
    ]
    list_editable = ['additional_price', 'display_order', 'is_active']
    search_fields = ['value', 'display_name', 'option__name']
    list_filter = ['option']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    autocomplete_fields = ['option', 'available_values']
    filter_horizontal = ['available_values']


# ============================================================
# PRODUCT
# ============================================================

class PriceTierInline(admin.TabularInline):
    model = PriceTier
    extra = 2
    fields = ['min_quantity', 'max_quantity', 'unit_price', 'discount_percentage']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image_url', 'option_value', 'is_primary', 'display_order']
    autocomplete_fields = ['option_value']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['slug', 'name', 'category', 'subcategory', 'sku', 'status', 'created_at']
    list_editable = ['status']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['category', 'subcategory', 'status']
    search_fields = ['name', 'slug', 'sku']
    autocomplete_fields = ['category', 'subcategory']
    inlines = [PriceTierInline, ProductVariantInline, ProductImageInline]


# ============================================================
# PRODUCT IMAGE ADMIN
# ============================================================

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'option_value', 'is_primary', 'display_order']
    list_editable = ['is_primary', 'display_order']
    search_fields = ['product__name', 'alt_text']
    list_filter = ['product__category', 'product__subcategory', 'option_value']


# ============================================================
# PRICE TIERS
# ============================================================

@admin.register(PriceTier)
class PriceTierAdmin(admin.ModelAdmin):
    list_display = ['product', 'min_quantity', 'max_quantity', 'unit_price', 'discount_percentage']
    list_filter = ['product__category']
    search_fields = ['product__name']


# ============================================================
# DESIGN TEMPLATES
# ============================================================

@admin.register(DesignTemplate)
class DesignTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'slug', 'name', 'category', 'subcategory',
        'is_popular', 'is_new', 'display_order', 'thumbnail_preview'
    ]
    list_editable = ['is_popular', 'is_new', 'display_order']
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ['category', 'subcategory']
    list_filter = ['category', 'subcategory', 'is_popular', 'is_new']
    search_fields = ['name', 'slug']

    def thumbnail_preview(self, obj):
        if obj.thumbnail_url:
            return format_html(
                '<img src="{}" style="width:70px;height:50px;object-fit:cover;border-radius:4px;" />',
                obj.thumbnail_url
            )
        return "Sin imagen"
    thumbnail_preview.short_description = "Preview"


# ============================================================
# PROFILE / PERU
# ============================================================

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'dni']


admin.site.register(Peru)


# ============================================================
# ADMIN BRANDING
# ============================================================

admin.site.site_header = "Imprenta Gallito - Administración"
admin.site.site_title = "Gallito Admin"
admin.site.index_title = "Panel de Administración"
