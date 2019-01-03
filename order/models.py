from django.db import models

# Create your models here.

#

class Order(models.Model):
    token = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField(max_length=250, blank = True, verbose_name= 'Correo electrónico')
    last_four = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    shipping_address1 = models.CharField(max_length=100, blank=True, null=True)
    shipping_address2 = models.CharField(max_length=100, blank=True, null=True)
    shipping_department = models.CharField(max_length=100, blank=True, null=True)
    shipping_province = models.CharField(max_length=100, blank=True, null=True)
    shipping_district = models.CharField(max_length=100, blank=True, null=True)
    reason = models.CharField(max_length=400, blank=True, null=True, default='')


    class Meta:
        db_table = 'Order'
        ordering = ['-created']

    def __str__(self):
        return str(self.id)




class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.CharField(max_length= 200)
    quantity = models.CharField(max_length= 200)
    size = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name= 'PEN Price')
    image = models.ImageField(upload_to='images', blank=True, null=True)
    comment = models.CharField(max_length=200, blank=True, null=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)



    class Meta:
        db_table = "OrderItem"

    def sub_total(self):
        return self.quantity * self.price


    @property
    def image_filename(self):
        return self.image.url.split('/')[-1]


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
