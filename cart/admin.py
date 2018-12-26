from django.contrib import admin

# from .models import Cart, CartItem

from .models import Cart, SizeQuantity, Transactions

# Register your models here.
admin.site.register(Cart)
# admin.site.register(CartItem)
admin.site.register(SizeQuantity)



class TransactionsAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'last_four', 'email', 'amount', 'reason', 'creation_date']
    list_editable = ['reason',]

    readonly_fields = ('transaction_id',)
    class Meta:
        ordering = ('transaction_id',)
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'


admin.site.register(Transactions, TransactionsAdmin)

