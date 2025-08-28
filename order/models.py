from django.db import models
from django.utils.html import mark_safe
import datetime
from decimal import Decimal

# Create your models here.

#

class Order(models.Model):
    ORDER_STATUS = (
        ('recibido_pagado', 'Recibido y pagado'),
        ('recibido_no_pagado', 'Recibido pero no pagado'),
        ('en_proceso', 'En proceso'),
        ('en_camino', 'En camino'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado por no pagar' )
    )
    token = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    stickers_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField(max_length=250, blank = True, verbose_name= 'Correo electrónico')
    last_four = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    shipping_address = models.CharField(max_length=100, blank=True, null=True)
    shipping_address1 = models.CharField(max_length=100, blank=True, null=True)
    reference = models.CharField(max_length=100, blank=True, null=True)
    shipping_department = models.CharField(max_length=100, blank=True, null=True)
    shipping_province = models.CharField(max_length=100, blank=True, null=True)
    shipping_district = models.CharField(max_length=100, blank=True, null=True)
    reason = models.CharField(max_length=400, blank=True, null=True, default='')
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='recibido_pagado')
    comments = models.CharField(max_length=400, blank=True, null=True, default='')
    cupon = models.ForeignKey('marketing.Cupons', blank=True, null=True, default=None, on_delete=models.SET_NULL)


    class Meta:
        db_table = 'Order'
        ordering = ['-created']

    def __str__(self):
        return str(self.id)

    def igv(self):
        igv = int(self.total) * 18/100
        return igv

    def shipping_date(self):
        shipping_date = self.created + datetime.timedelta(days=10)
        return shipping_date

    def deposit_payment_date(self):
        deposit_payment_date = self.created + datetime.timedelta(days=2)
        return deposit_payment_date



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    name = models.CharField(max_length= 200)
    sku = models.CharField(max_length=20)
    quantity = models.CharField(max_length= 200)
    size = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name= 'PEN Price')
    file_a = models.FileField(upload_to='files', blank=True, null=True)
    file_b = models.FileField(upload_to='files', blank=True, null=True)
    comment = models.CharField(max_length=200, blank=True, null=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "OrderItem"

    def file_thumbnail_a(self):
        if self.file_a:
           if str(self.file_a).endswith('.ai'):
               return mark_safe(u'<img src="%s" width="60px" height="50px" />' % ('/static/img/admin/adobe_illustrator_file_logo.png'))
           else:
               return mark_safe(u'<a href="%s" target="_blank"><img src="%s" width="80px" height="80px" /></a>' % (self.file_a.url, self.file_a.url))

        else:
            return mark_safe(u'<p> Sin imagen </p>')

    def file_thumbnail_b(self):
        if self.file_b:
           if str(self.file_b).endswith('.ai'):
               return mark_safe(u'<img src="%s" width="60px" height="50px" />' % ('/static/img/admin/adobe_illustrator_file_logo.png'))
           else:
               return mark_safe(u'<a href="%s" target="_blank"><img src="%s" width="80px" height="80px" /></a>' % (self.file_b.url, self.file_b.url))
        else:
            return mark_safe(u'<p> Sin imagen </p>')        


    def sub_total(self):
        return self.price


    # @property
    # def image_filename(self):
    #     return self.image.url.split('/')[-1]


    #def __str__(self):
    #    return self.product



## ORDERS SUMMARY

class OrderSummary(Order): #Extends funcs of model without creating a table in DB
    class Meta:
        proxy = True #important A proxy model extends the functionality of another model without creating an actual table in the database
        verbose_name = 'Order Summary'
        verbose_name_plural = 'Orders Summary'
