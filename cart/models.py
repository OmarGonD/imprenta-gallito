from django.db import models
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
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'Cart'
        ordering = ['date_added']

    def __str__(self):
        return self.cart_id

#
# class CartItem(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
#     quantity = models.IntegerField()
#     active = models.BooleanField(default=True)
#     class Meta:
#         db_table = 'CartItem'
#
#     def sub_total(self):
#         return self.product.price * self.quantity
#
#     def __str__(self):
#         return str(self.product)





# class CartItem(models.Model):
#     sizequantity = models.ForeignKey(SizeQuantity, on_delete=models.CASCADE)
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
#     # size = models.CharField(max_length=10, choices=TAMANIOS)
#     # quantity = models.CharField(max_length=10, choices=CANTIDADES)
#     # uploaded_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         db_table = 'CartItem'
#
#     def sub_total(self):
#         return self.sizequantity.product.price * self.sizequantity.quantity
#
#     def __str__(self):
#         return str(self.sizequantity.product)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=20, choices=TAMANIOS)
    quantity = models.CharField(max_length=20, choices=CANTIDADES)
    image = models.ImageField(upload_to='images', blank=True, null=True)
    comment = models.CharField(max_length=100, blank=True, null=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id) + " - " + str(self.size) + " por " + str(self.quantity)

    def sub_total(self):
        return str(self.product.price * int(self.quantity))


    @property
    def image_filename(self):
        return self.image.url.split('/')[-1]







