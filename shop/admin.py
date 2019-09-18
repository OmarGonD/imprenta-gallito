from django.contrib import admin
from .models import *

# Register your models here.



admin.site.register(Product_Review)
admin.site.register(Sample_Review)

admin.site.register(Peru)


class PackAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug':('name',)}


admin.site.register(Pack, PackAdmin)


class SampleAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug':('name',)}


admin.site.register(Sample, SampleAdmin)

class SamplesPricingAdmin(admin.ModelAdmin):
    list_display = ['category', 'sample', 'size', 'quantity', 'price']
    list_editable = ['quantity', 'price']
    list_per_page = 20


admin.site.register(SamplesPricing, SamplesPricingAdmin)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'dni']



admin.site.register(Profile, ProfileAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug':('name',)}


admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'available', 'created', 'updated']
    list_editable = ['available']
    prepopulated_fields = {'slug':('name',)}
    list_per_page = 20


admin.site.register(Product, ProductAdmin)


class ProductsPricingAdmin(admin.ModelAdmin):
    list_display = ['size', 'quantity', 'category', 'product', 'price']
    list_editable = ['category', 'product', 'price']
    list_per_page = 20


admin.site.register(ProductsPricing, ProductsPricingAdmin)


