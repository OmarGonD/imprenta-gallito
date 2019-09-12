from django.db import models
from django.http import HttpResponse

from shop.models import Product, Sample, SamplesPricing, ProductsPricing
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
    file_a = models.FileField(upload_to='files', blank=True, null=True)
    file_b = models.FileField(upload_to='files', blank=True, null=True)
    comment = models.CharField(max_length=100, blank=True, null=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    step_two_complete = models.BooleanField(default=False)

    # def __str__(self):
    #     return str(self.id) + " - " + str(self.size) + " por " + str(self.quantity)

    def sub_total(self):
        print("### PRODUCTITEM SUBTOTAL ###")
        print(type(self.product))
        print(self.product)
        print(type(self.size))
        print(self.size)
        print(type(self.quantity))
        print(self.quantity)
        print("############################")
        product_price = ProductsPricing.objects.filter(product=self.product, size=self.size, quantity=self.quantity).values_list("price", flat=True)[0]
        return int(product_price)


    @property
    def file_name_a(self):
        if self.file_a:
            return self.file_a.url.split('/')[-1]
        else:
            return self.product.image.url.split('/')[-1]

    @property
    def file_name_b(self):
        if self.file_b:
            return self.file_b.url.split('/')[-1]
        else:
            pass        


class SampleItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    size = models.CharField(max_length=20, choices=TAMANIOS)
    quantity = models.CharField(max_length=20, choices=CANTIDADES)
    file_a = models.FileField(upload_to='files', blank=True, null=True)
    file_b = models.FileField(upload_to='files', blank=True, null=True)
    comment = models.CharField(max_length=100, blank=True, null=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    step_two_complete = models.BooleanField(default=False)

    def sub_total(self):

        #sample_price = SamplesPricing.objects.filter(sample=self.sample, size=self.size, quantity=self.quantity).values_list("price", flat=True)[0]
        #return int(sample_price)
        print("#######SUB TOTAL - SAMPLEITEM #############")
        print(type(self.sample))
        print(self.sample)
        print(type(self.size))
        print(self.size)
        print(type(self.quantity))
        print(self.quantity)
        print("####################")
        return int(5)

    @property
    def file_name_a(self):
        if self.file_a:
            return self.file_a.url.split('/')[-1]
        else:
            return self.product.image.url.split('/')[-1]

    @property
    def file_name_b(self):
        if self.file_b:
            return self.file_b.url.split('/')[-1]
        else:
            return self.product.image.url.split('/')[-1]        

          
