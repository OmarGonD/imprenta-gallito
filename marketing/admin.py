from django.contrib import admin
from .models import SignUp, Cupons

# Register your models here.

# class CuponsAdmin(admin.ModelAdmin):
#     list_display = ['id', 'cupon', 'active']
#     ordering = ['-id']
#
#
# admin.site.register(Cupons, Cupons)

admin.site.register(Cupons)
admin.site.register(SignUp)

