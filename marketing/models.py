from django.db import models

# Create your models here.

class SignUp(models.Model):
    email = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email




def valid_percentage(val):
    if val.endswith("%"):
        return float(val[:-1])/100
    else:
        return float(val)


class Cupons(models.Model):
    cupon = models.CharField(max_length=100, blank=False)
    percentage = models.CharField(max_length=20, blank=True, null=True, validators=[valid_percentage])
    hard_discount = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField(default=10)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.cupon + " - " + str(self.active)



### Registra que usuario hizo uso del cupon y cual fue su orden ###
### Esto nos servira para evitar que un mismo usuario use el cupon 2 o más veces ###

from order.models import Order
from django.contrib.auth.models import User


class used_cupons(models.Model):
    cupon = models.CharField(max_length=100, blank=False, null=True)
    user = models.CharField(max_length=100, blank=False, null=True)
    order = models.CharField(max_length=100, blank=False, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cupon



