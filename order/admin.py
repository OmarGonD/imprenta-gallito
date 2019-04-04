from django.contrib import admin

from .models import Order, OrderItem





# Register your models here.



class OrderItemAdmin(admin.TabularInline):
    model = OrderItem
    fieldsets = [
        # ('Customer', {'fields': ['first_name', 'last_name'], }),
        ('Product', {'fields': ['product'],}),
        ('Size', {'fields': ['size'], }),
        ('Quantity', {'fields': ['quantity'],}),
        ('Price', {'fields': ['price'], }),
        ('File', {'fields': ['file'], }),
        ('File_Thumbnail', {'fields': ['file_thumbnail'], }),
    ]
    readonly_fields = ['product', 'size', 'quantity', 'price', 'file', 'file_thumbnail']
    can_delete = False
    max_num = 0
    template = 'admin/order/tabular.html'




### Order Display ###

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = ['id', 'status', 'first_name', 'last_name', 'phone_number', 'email', 'last_four', 'total', 'reason', 'created']
    list_editable = ['reason', 'status']
    list_display_links = ('id', 'email')
    search_fields = ['token', 'shipping_department', 'email']
    readonly_fields = ['id','created', 'total']

    fieldsets = [
        ('ORDER INFORMATION', {'fields': ['id','status', 'total', 'created']}),
        # ('BILLING INFORMATION', {'fields': ['billingName', 'billingAddress1', 'billingCity', 'billingPostCode',
        #                                     'billingCountry', 'emailAddress']}),
        ('SHIPPING INFORMATION', {'fields': ['first_name', 'last_name', 'phone_number', 'email', 'last_four', 'shipping_address', 'shipping_department', 'shipping_province',
                                             'shipping_district', 'shipping_address1', 'shipping_address2']}),
    ]

    inlines = [
        OrderItemAdmin,
    ]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False





#####################


# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['id', 'email', 'total', 'reason', 'created']
#     list_editable = ['reason',]
#
#     readonly_fields = ('id',)
#     class Meta:
#         ordering = ('id',)
#         verbose_name = 'Order'
#         verbose_name_plural = 'Orders'
#
#
# admin.site.register(Order, OrderAdmin)