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
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.cupon + " - " + str(self.active)

