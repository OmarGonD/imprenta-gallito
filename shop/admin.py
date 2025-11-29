from django.contrib import admin
from .models import (
    Product, Profile, Peru, Category, Subcategory,
    VariantType, VariantOption, ProductVariantType, PriceTier,
    ClothingCategory, ClothingSubCategory, ClothingColor, ClothingSize,
    ClothingProduct, ClothingProductImage, ClothingProductPricing
)



# Register your models here.

# ===========================
# CATALOG SYSTEM ADMIN
# ===========================

class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1
    prepopulated_fields = {'slug': ('name',)}
    fields = ['slug', 'name', 'description', 'display_order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['slug', 'name', 'display_order', 'status', 'created_at']
    list_editable = ['display_order', 'status']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug', 'description']
    list_filter = ['status', 'created_at']
    inlines = [SubcategoryInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('slug', 'name', 'description')
        }),
        ('Imagen', {
            'fields': ('image_url',)
        }),
        ('Configuración', {
            'fields': ('display_order', 'status')
        }),
    )


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['slug', 'name', 'category', 'display_order', 'created_at']
    list_editable = ['display_order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug', 'description']
    list_filter = ['category', 'created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('slug', 'name', 'category', 'description')
        }),
        ('Imagen', {
            'fields': ('image_url',)
        }),
        ('Configuración', {
            'fields': ('display_order',)
        }),
    )


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
