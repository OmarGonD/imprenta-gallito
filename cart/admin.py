from django.contrib import admin

# from .models import Cart, CartItem

from .models import Cart, CartItem

# Register your models here.

class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart_id']
    ordering = ['-id']
    # prepopulated_fields = {'slug':('name',)}

admin.site.register(Cart, CartAdmin)


# admin.site.register(CartItem)
admin.site.register(CartItem)












