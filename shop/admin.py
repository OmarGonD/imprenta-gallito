from django.contrib import admin
from .models import (
    Product, Profile, Peru,
    ClothingCategory, ClothingSubCategory, ClothingColor, ClothingSize,
    ClothingProduct, ClothingProductImage, ClothingProductPricing
)

# Import catalog admin configuration (handles Category, Subcategory, CatalogProduct, etc.)
from . import catalog_admin

# Register your models here.




admin.site.register(Peru)






class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'dni']



admin.site.register(Profile, ProfileAdmin)





# ===========================
# CLOTHING & BAGS ADMIN
# ===========================

class ClothingSubCategoryInline(admin.TabularInline):
    model = ClothingSubCategory
    extra = 1
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ClothingCategory)
class ClothingCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'available']
    list_editable = ['order', 'available']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ClothingSubCategoryInline]
    search_fields = ['name']
    list_filter = ['available']


@admin.register(ClothingSubCategory)
class ClothingSubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'order', 'available']
    list_editable = ['order', 'available']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['category', 'available']
    search_fields = ['name', 'category__name']


@admin.register(ClothingColor)
class ClothingColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'hex_code', 'order', 'color_preview']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def color_preview(self, obj):
        return f'<div style="background-color: {obj.hex_code}; width: 30px; height: 30px; border-radius: 50%; border: 1px solid #ccc;"></div>'
    color_preview.allow_tags = True
    color_preview.short_description = 'Color'


@admin.register(ClothingSize)
class ClothingSizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'size_type', 'order']
    list_editable = ['order']
    list_filter = ['size_type']
    search_fields = ['name', 'display_name']


class ClothingProductImageInline(admin.TabularInline):
    model = ClothingProductImage
    extra = 3
    fields = ['image', 'color', 'alt_text', 'is_primary', 'order']


class ClothingProductPricingInline(admin.TabularInline):
    model = ClothingProductPricing
    extra = 3
    fields = ['min_quantity', 'max_quantity', 'price_per_unit']


@admin.register(ClothingProduct)
class ClothingProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'base_price', 'sale_price', 'is_featured', 'is_bestseller', 'available']
    list_editable = ['base_price', 'sale_price', 'is_featured', 'is_bestseller', 'available']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['category', 'subcategory', 'is_featured', 'is_bestseller', 'is_new', 'available']
    search_fields = ['name', 'sku', 'description']
    filter_horizontal = ['available_colors', 'available_sizes']
    inlines = [ClothingProductImageInline, ClothingProductPricingInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'sku', 'description', 'short_description')
        }),
        ('Categorización', {
            'fields': ('category', 'subcategory')
        }),
        ('Precios', {
            'fields': ('base_price', 'sale_price', 'min_quantity')
        }),
        ('Opciones', {
            'fields': ('available_colors', 'available_sizes')
        }),
        ('Imágenes', {
            'fields': ('main_image', 'hover_image')
        }),
        ('Características', {
            'fields': ('material', 'weight', 'features')
        }),
        ('Estado', {
            'fields': ('is_featured', 'is_new', 'is_bestseller', 'available')
        }),
    )


@admin.register(ClothingProductImage)
class ClothingProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'color', 'is_primary', 'order']
    list_filter = ['product__category', 'color', 'is_primary']
    search_fields = ['product__name', 'alt_text']


@admin.register(ClothingProductPricing)
class ClothingProductPricingAdmin(admin.ModelAdmin):
    list_display = ['product', 'min_quantity', 'max_quantity', 'price_per_unit']
    list_filter = ['product__category']
    search_fields = ['product__name']
