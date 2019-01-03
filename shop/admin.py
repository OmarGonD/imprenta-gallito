from django.contrib import admin
from .models import Category, Product, Profile, Peru

# Register your models here.




admin.site.register(Peru)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'dni']


admin.site.register(Profile, ProfileAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug':('name',)}


admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'available', 'created', 'updated']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug':('name',)}
    list_per_page = 20


admin.site.register(Product, ProductAdmin)
