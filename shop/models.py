from django.db import models
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

#Variables
from embed_video.fields import EmbedVideoField

TAMANIOS = (('variante_50', '50 mm x 50 mm',), ('variante_75', '75 mm x 75 mm',),
            ('variante_100', '100 mm x 100 mm',), ('variante_125', '125 mm x 125 mm',))

CANTIDADES = (('cantidad_50', '50',), ('cantidad_100', '100',),
              ('cantidad_200', '200',), ('cantidad_300', '300',),
              ('cantidad_500', '500',), ('cantidad_1000', '1000',),
              ('cantidad_2000', '2000',), ('cantidad_3000', '3000',),
              ('cantidad_4000', '4000',), ('cantidad_5000', '5000',),
              ('cantidad_1000', '1000',))


# Create your models here.
# EmbedVideoField Optional


class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category', blank=True)
    video = EmbedVideoField(null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('shop:allCat', args=[self.slug])

    def __str__(self):
        return '{}'.format(self.name)


class Product(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product', blank=True)
    stock = models.IntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def get_url(self):
            return reverse('shop:ProdDetail', args=[self.category.slug, self.slug])

    def __str__(self):
        return '{}'.format(self.name)



### Sample Packs ###

class Sample(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    image = models.ImageField(upload_to='product', blank=True)
    stock = models.IntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'sample'
        verbose_name_plural = 'samples'

    def get_url(self):
        return reverse('shop:SampleCatDetail', args=[self.category.slug, self.slug])
        # return reverse('shop:SampleDetail', args=[self.slug])

    def __str__(self):
        return '{}'.format(self.name)




### Reviews ###


class Reviews(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    review = models.CharField(max_length=250, unique=True)
    order_again = models.BooleanField(default=True)
    stars = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)



### User Profile ###


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthdate = models.DateField(null=True, blank=True)
    dni = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    shipping_address1 = models.CharField(max_length=100, blank=False)
    shipping_address2 = models.CharField(max_length=100, blank=False)
    shipping_department = models.CharField(max_length=100, blank=False)
    shipping_province = models.CharField(max_length=100, blank=False)
    shipping_district = models.CharField(max_length=100, blank=False)

    def __str__(self):
        return str(self.user.first_name) + "'s profile"




@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Peru(models.Model):
    departamento = models.CharField(max_length=100, blank=False)
    provincia = models.CharField(max_length=100, blank=False)
    distrito = models.CharField(max_length=100, blank=False)

    def __str__(self):
        return self.departamento + " - " + self.provincia + " - " + self.distrito