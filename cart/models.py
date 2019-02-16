from django.db import models
from django.http import HttpResponse

from shop.models import Product, Sample

# Variables


TAMANIOS = (('5cm x 5cm', '5 cm x 5 cm',), ('7cm x 7cm', '7 cm x 7 cm',),
            ('10cm x 10cm', '10 cm x 10 cm',), ('13cm x 13cm', '13 cm x 13 cm',))

CANTIDADES = (('50', '50',), ('100', '100',),
              ('200', '200',), ('300', '300',),
              ('500', '500',), ('1000', '1000',),
              ('2000', '2000',), ('3000', '3000',),
              ('4000', '4000',), ('5000', '5000',),
              ('10000', '10000',))



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
        if self.product.slug == 'paquete-de-muestra':
            return str(10)
        else:
            if self.size == '5cm x 5cm' and self.quantity == '50':
                return (str(50))
            elif self.size == '5cm x 5cm' and self.quantity == '100':
                return (str(70))
            elif self.size == '5cm x 5cm' and self.quantity == '200':
                return (str(90))
            elif self.size == '5cm x 5cm' and self.quantity == '300':
                return (str(108))
            elif self.size == '5cm x 5cm' and self.quantity == '500':
                return (str(140))
                # 7cm x 7cm
            elif self.size == '7cm x 7cm' and self.quantity == '50':
                return (str(70))
            elif self.size == '7cm x 7cm' and self.quantity == '100':
                return (str(90))
            elif self.size == '7cm x 7cm' and self.quantity == '200':
                return (str(130))
            elif self.size == '7cm x 7cm' and self.quantity == '300':
                return (str(160))
            elif self.size == '7cm x 7cm' and self.quantity == '500':
                return (str(240))
                #Size: 10cm x 10cm
            elif self.size == '10cm x 10cm' and self.quantity == '50':
                return (str(90))
            elif self.size == '10cm x 10cm' and self.quantity == '100':
                return (str(115))
            elif self.size == '10cm x 10cm' and self.quantity == '200':
                return (str(180))
            elif self.size == '10cm x 10cm' and self.quantity == '300':
                return (str(280))
            elif self.size == '10cm x 10cm' and self.quantity == '500':
                return (str(450))

            #13cm x 13cm
            elif self.size == '13cm x 13cm' and self.quantity == '50':
                return (str(200))
            elif self.size == '13cm x 13cm' and self.quantity == '100':
                return (str(370))
            elif self.size == '13cm x 13cm' and self.quantity == '200':
                return (str(430))
            elif self.size == '13cm x 13cm' and self.quantity == '300':
                return (str(500))
            elif self.size == '13cm x 13cm' and self.quantity == '500':
                return (str(900))



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

    # def __str__(self):
    #     return str(self.id) + " - " + str(self.size) + " por " + str(self.quantity)

    def sub_total(self):
        if self.sample.slug == 'paquete-de-muestra':
            return str(1)
        else:
            return str(9)


    @property
    def file_name(self):
        if self.file:
            return self.file.url.split('/')[-1]
        else:
            return self.product.image.url.split('/')[-1]







