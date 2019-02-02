from django.db import models
from django.http import HttpResponse

from shop.models import Product



TAMANIOS = (('50mm x 50mm', '50 mm x 50 mm',), ('75mm x 75mm', '75 mm x 75 mm',),
            ('100mm x 100mm', '100 mm x 100 mm',), ('125mm x 125mm', '125 mm x 125 mm',))

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
        return self.id





class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=20, choices=TAMANIOS)
    quantity = models.CharField(max_length=20, choices=CANTIDADES)
    file = models.FileField(upload_to='files', blank=True, null=True)
    comment = models.CharField(max_length=100, blank=True, null=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    step_two_complete = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id) + " - " + str(self.size) + " por " + str(self.quantity)

    def sub_total(self):
        return str(self.product.price * int(self.quantity))


    @property
    def file_name(self):
        if self.file:
            return self.file.url.split('/')[-1]
        else:
            return self.product.image.url.split('/')[-1]







