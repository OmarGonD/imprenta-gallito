from django.contrib import admin

from .models import Order, OrderItem, OrderSummary
from django.db.models import Sum, Count, F






# Register your models here.



class OrderItemAdmin(admin.TabularInline):
    model = OrderItem
    fieldsets = [
        # ('Customer', {'fields': ['first_name', 'last_name'], }),
        ('Name', {'fields': ['name'],}),
        ('Size', {'fields': ['size'], }),
        ('Quantity', {'fields': ['quantity'],}),
        ('Price', {'fields': ['price'], }),
        ('File_Thumbnail_A', {'fields': ['file_thumbnail_a'], }),
        ('File_Thumbnail_B', {'fields': ['file_thumbnail_b'], }),
        ('Comment', {'fields': ['comment'], })
    ]
    readonly_fields = ['name', 'size', 'quantity', 'price', 'file_thumbnail_a', 'file_thumbnail_b', 'comment']
    can_delete = False
    max_num = 0
    template = 'admin/order/tabular.html'




### Order Display ###

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = ['id', 'status', 'first_name', 'last_name', 'phone_number', 'email', 'total', 'discount', 'created', 'shipping_cost', 'comments']
    list_editable = ['status']
    list_display_links = ('id', 'email')
    list_filter = ('status', )
    search_fields = ['token', 'shipping_department', 'email']
    readonly_fields = ['id','created', 'total', 'stickers_price', 'discount', 'shipping_cost', 'comments']
    date_hierarchy = 'created'

    fieldsets = [
        ('ORDER INFORMATION', {'fields': ['id','status', 'total', 'stickers_price', 'shipping_cost', 'discount', 'comments', 'created']}),
        # ('BILLING INFORMATION', {'fields': ['billingName', 'billingAddress1', 'billingCity', 'billingPostCode',
        #                                     'billingCountry', 'emailAddress']}),
        ('SHIPPING INFORMATION', {'fields': ['first_name', 'last_name', 'phone_number', 'email', 'last_four', 'shipping_address', 'shipping_department', 'shipping_province',
                                             'shipping_district', 'shipping_address1', 'reference']}),
    ]

    inlines = [
        OrderItemAdmin,
    ]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

      





#####################
from django.db.models import Func

class Round(Func):
  function = 'ROUND'
  arity = 2

@admin.register(OrderSummary)
class OrderSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/order_summary_change_list.html'
    date_hierarchy = 'created'

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        
        metrics = {
            'num': Count('id'),
            'total_sales': Round(Sum('total'),2),
            'total_shipping_cost': Round(Sum('shipping_cost'), 2),
            'total_no_shipping_cost': Round(Sum(F('total') - F('shipping_cost')),2),
        }

        response.context_data['summary'] = list(
            qs
            .values('id','total', 'shipping_cost')
            .annotate(**metrics)
            .order_by('-created')
        )

        response.context_data['summary_total'] = dict(
            qs.aggregate(**metrics)
        )
       
        return response

       
