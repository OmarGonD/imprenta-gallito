from django.db import models
from django.utils.html import mark_safe
import datetime

# Create your models here.

#

class Order(models.Model):
    ORDER_STATUS = (
        ('recibido_pagado', 'Recibido y pagado'),
        ('recibido_no_pagado', 'Recibido pero no pagado'),
        ('en_proceso', 'En proceso'),
        ('en_camino', 'En camino'),
        ('entregado', 'Entregado'),
    )
    token = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField(max_length=250, blank = True, verbose_name= 'Correo electrónico')
    last_four = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    shipping_address = models.CharField(max_length=100, blank=True, null=True)
    shipping_address1 = models.CharField(max_length=100, blank=True, null=True)
    shipping_address2 = models.CharField(max_length=100, blank=True, null=True)
    shipping_department = models.CharField(max_length=100, blank=True, null=True)
    shipping_province = models.CharField(max_length=100, blank=True, null=True)
    shipping_district = models.CharField(max_length=100, blank=True, null=True)
    reason = models.CharField(max_length=400, blank=True, null=True, default='')
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='recibido_pagado')


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
        deposit_payment_date = self.created + datetime.timedelta(days=1)
        return deposit_payment_date




class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.CharField(max_length= 200)
    quantity = models.CharField(max_length= 200)
    size = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name= 'PEN Price')
    file = models.FileField(upload_to='files', blank=True, null=True)
    comment = models.CharField(max_length=200, blank=True, null=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)



    class Meta:
        db_table = "OrderItem"

    def file_thumbnail(self):
        if self.file:
           if str(self.file).endswith('.ai'):
               return mark_safe(u'<img src="%s" width="60px" height="50px" />' % ('/static/img/admin/adobe_illustrator_file_logo.png'))
           else:
               return mark_safe(u'<img src="%s" width="200px" height="140px" />' % (self.file.url))

        else:
            return mark_safe(u'<p> Sin imagen </p>')


    file_thumbnail.short_description = 'File Thumbnail'


    def sub_total(self):
        return self.price


    # @property
    # def image_filename(self):
    #     return self.image.url.split('/')[-1]


    def __str__(self):
        return self.product




###############################



# class Order(models.Model):
#     token = models.CharField(max_length=250, blank = True)
#     total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name= 'PEN Order Total')
#     emailAddress = models.EmailField(max_length=250, blank = True, verbose_name= 'Email Address')
#     created = models.DateTimeField(auto_now_add=True)
#     billingName = models.CharField(max_length=250, blank=True)
#     billingAddress1 = models.CharField(max_length=250, blank=True)
#     billingCity = models.CharField(max_length=250, blank=True)
#     billingPostCode = models.CharField(max_length=10, blank=True)
#     billingCountry = models.CharField(max_length=200, blank=True)
#     shippingName = models.CharField(max_length=250, blank=True)
#     shippingAddress1 = models.CharField(max_length=250, blank=True)
#     shippingCity = models.CharField(max_length=250, blank=True)
#     shippingPostcode = models.CharField(max_length=10, blank=True)
#     shippingCountry = models.CharField(max_length=10, blank=True)
#
#     class Meta:
#         db_table = 'Order'
#         ordering = ['-created']
#
#     def __str__(self):
#         return str(self.id)
