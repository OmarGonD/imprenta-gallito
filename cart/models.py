from django.db import models
from django.http import HttpResponse

from shop.models import Product, Sample
from shop.sizes_and_quantities import TAMANIOS, CANTIDADES

# Variables


# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length=100)
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'Cart'
        ordering = ['date_added']

    def __str__(self):
        return str(self.id)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=20, choices=TAMANIOS)
    quantity = models.CharField(max_length=20, choices=CANTIDADES)
    file = models.FileField(upload_to='files', blank=True, null=True)
    comment = models.CharField(max_length=100, blank=True, null=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    step_two_complete = models.BooleanField(default=False)

    # def __str__(self):
    #     return str(self.id) + " - " + str(self.size) + " por " + str(self.quantity)

    def sub_total(self):
        if self.size == '5cm x 5cm' and self.quantity == '50':
            return 50
        elif self.size == '5cm x 5cm' and self.quantity == '100':
            return 70
        elif self.size == '5cm x 5cm' and self.quantity == '200':
            return 90
        elif self.size == '5cm x 5cm' and self.quantity == '300':
            return 108
        elif self.size == '5cm x 5cm' and self.quantity == '500':
            return 140
            # 7cm x 7cm
        elif self.size == '7cm x 7cm' and self.quantity == '50':
            return 70
        elif self.size == '7cm x 7cm' and self.quantity == '100':
            return 90
        elif self.size == '7cm x 7cm' and self.quantity == '200':
            return 130
        elif self.size == '7cm x 7cm' and self.quantity == '300':
            return 160
        elif self.size == '7cm x 7cm' and self.quantity == '500':
            return 240
            # Size: 10cm x 10cm
        elif self.size == '10cm x 10cm' and self.quantity == '50':
            return 90
        elif self.size == '10cm x 10cm' and self.quantity == '100':
            return 115
        elif self.size == '10cm x 10cm' and self.quantity == '200':
            return 180
        elif self.size == '10cm x 10cm' and self.quantity == '300':
            return 280
        elif self.size == '10cm x 10cm' and self.quantity == '500':
            return 450

        # 13cm x 13cm
        elif self.size == '13cm x 13cm' and self.quantity == '50':
            return 200
        elif self.size == '13cm x 13cm' and self.quantity == '100':
            return 370
        elif self.size == '13cm x 13cm' and self.quantity == '200':
            return 430
        elif self.size == '13cm x 13cm' and self.quantity == '300':
            return 500
        elif self.size == '13cm x 13cm' and self.quantity == '500':
            return 900

    @property
    def file_name(self):
        if self.file:
            return self.file.url.split('/')[-1]
        else:
            return self.product.image.url.split('/')[-1]


class SampleItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    size = models.CharField(max_length=20, choices=TAMANIOS)
    quantity = models.CharField(max_length=20, choices=CANTIDADES)
    file = models.FileField(upload_to='files', blank=True, null=True)
    comment = models.CharField(max_length=100, blank=True, null=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    step_two_complete = models.BooleanField(default=False)


    def sub_total(self):
        if self.sample.slug == 'sobre-con-muestras':
            return str(3)
        else:
            return str(9)

    @property
    def file_name(self):
        if self.file:
            return self.file.url.split('/')[-1]
        else:
            return self.product.image.url.split('/')[-1]
