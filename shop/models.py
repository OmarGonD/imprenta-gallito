from django.db import models
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .sizes_and_quantities import TAMANIOS, CANTIDADES

#Variables
from embed_video.fields import EmbedVideoField


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


class Product_Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    review = models.CharField(max_length=250, unique=True)
    stars = models.DecimalField(max_digits=4, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.username) + ": " + str(self.product.name) + " | Estrellas: " + str(self.stars)




class Sample_Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    review = models.CharField(max_length=250, unique=True)
    stars = models.DecimalField(max_digits=4, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.username) + ": " + str(self.sample.name) + " | Estrellas: " + str(self.stars)







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
    photo = models.ImageField(upload_to='profile_pics', default='profile_pics/default_profile_pic_white.png')

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