from django.contrib import admin
from .models import SignUp, Cupons, used_cupons

# Register your models here.


class UsedCuponsAdmin(admin.ModelAdmin):
    model = used_cupons

    list_display = ['cupon', 'user', 'created', 'order_id', 'order_total_to_pay', 'stickers_price',
                    'order_shipping_cost', 'order_discount',
                    'order_total_without_shipping', 
                    'cupon_discount_percentage' ]                    

    def order_id(self, obj):
        return obj.order.id

    def order_total_to_pay(self, obj):
        return obj.order.total

    def stickers_price(self, obj):
        return obj.order.stickers_price    

    def order_total_without_shipping(self, obj):
        return obj.order.total - obj.order.shipping_cost  

    def order_discount(self, obj):
        return obj.order.discount
    
    def order_shipping_cost(self, obj):
        return obj.order.shipping_cost

    def cupon_discount_percentage(self, obj):
        return obj.cupon.percentage

    def hard_discount(self, obj):
        return obj.cupon.hard_discount         


    
    
 
admin.site.register(used_cupons, UsedCuponsAdmin)



admin.site.register(Cupons)
admin.site.register(SignUp)
