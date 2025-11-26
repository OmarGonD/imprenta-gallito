from django.db import models
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .sizes_and_quantities import TAMANIOS, CANTIDADES

#Variables



# Create your models here.
# EmbedVideoField Optional


class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category', blank=True, null=True)
    #video = EmbedVideoField(null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        # Use the correct named URL for category detail
        return reverse('shop:ProdCatDetail', args=[self.slug])

    def __str__(self):
        return '{}'.format(self.name)


class Product(models.Model):
    name = models.CharField(max_length=250, unique=False)
    slug = models.SlugField(max_length=250, unique=False)
    sku = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images', blank=True, null=True)
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



##############################
### COSTO DE LOS PRODUCTOS ###
##############################


class ProductsPricing(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=20, choices=TAMANIOS)
    quantity = models.CharField(max_length=20, choices=CANTIDADES)
    price = models.IntegerField(default=30)


####################################
#### Packs de productos varios #####
####################################

''' Every pack should contain it's own price '''

class Pack(models.Model):
    name = models.CharField(max_length=250, unique=False)
    slug = models.SlugField(max_length=250, unique=False)
    sku = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.CharField(max_length=20, blank=True, null=True)
    size = models.CharField(max_length=20, blank=True, null=True)
    quantity = models.CharField(max_length=20, blank=True, null=True)
    price = models.IntegerField(default=10)
    image = models.ImageField(upload_to='pack_images', blank=True, null=True)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'pack'
        verbose_name_plural = 'packs'

    def __str__(self):
        return '{}'.format(self.name)



########################
### Unitary Products ###
########################

class UnitaryProduct(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory1 = models.CharField(max_length=20, blank=True, null=True)
    subcategory2 = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=250, unique=False)
    slug = models.SlugField(max_length=250, unique=False)
    sku = models.CharField(max_length=14, unique=True)
    description = models.TextField(blank=True)
    size = models.CharField(max_length=20, blank=True, null=True)
    quantity = models.CharField(default=1, max_length=20, blank=True, null=True)
    price = models.DecimalField(default=2, decimal_places=2, max_digits=4)
    image = models.ImageField(upload_to='unitaryproducts', blank=True, null=True)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'unitary product'
        verbose_name_plural = 'unitary products'

    def __str__(self):
        return '{}'.format(self.name)


### Sample Packs ###

class Sample(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    sku = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='sample_images', blank=True)
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


##############################
### COSTO DE LAS MUESTRAS ###
##############################


class SamplesPricing(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    size = models.CharField(max_length=20, choices=TAMANIOS)
    quantity = models.CharField(max_length=20, choices=CANTIDADES)
    price = models.IntegerField(default=30)

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
    reference = models.CharField(max_length=100, blank=False)
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



#####################################################################
# Model con informacion sobre el costo de los despachos a provincia #
#####################################################################


class Peru(models.Model):
    departamento = models.CharField(max_length=100, blank=False)
    provincia = models.CharField(max_length=100, blank=False)
    distrito = models.CharField(max_length=100, blank=False)
    costo_despacho_con_recojo = models.IntegerField(default=15)
    costo_despacho_sin_recojo = models.IntegerField(default=15)
    dias_despacho = models.IntegerField(default=4)

    def __str__(self):
        return self.departamento + " - " + self.provincia + " - " + self.distrito + '-' + str(self.dias_despacho)


class TarjetaPresentacion(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='tarjetas_presentacion', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Folleto(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='folletos', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Poster(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='posters', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Etiqueta(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='etiquetas', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Empaque(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='empaques', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


#######################################
### CLOTHING & BAGS - VistaPrint Clone
#######################################

class ClothingCategory(models.Model):
    """Main categories: Camisetas, Polos, Gorras, Bolsas, etc."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='clothing/categories/', blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    order = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Clothing Category'
        verbose_name_plural = 'Clothing Categories'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:clothing_category', args=[self.slug])


class ClothingSubCategory(models.Model):
    """Sub-categories: Viseras, Gorras de Camionero, etc."""
    category = models.ForeignKey(ClothingCategory, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='clothing/subcategories/', blank=True, null=True)
    order = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Clothing SubCategory'
        verbose_name_plural = 'Clothing SubCategories'
        unique_together = ['category', 'slug']
    
    def __str__(self):
        return f"{self.category.name} > {self.name}"
    
    def get_absolute_url(self):
        return reverse('shop:clothing_subcategory', args=[self.category.slug, self.slug])


class ClothingColor(models.Model):
    """Available colors for clothing products"""
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=7, help_text="Color hex code, e.g., #FF5733")
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class ClothingSize(models.Model):
    """Available sizes for clothing products"""
    SIZE_TYPES = [
        ('clothing', 'Ropa'),
        ('hat', 'Gorras'),
        ('bag', 'Bolsas'),
    ]
    name = models.CharField(max_length=20)  # XS, S, M, L, XL, etc.
    display_name = models.CharField(max_length=50)  # Extra Small, Small, etc.
    size_type = models.CharField(max_length=20, choices=SIZE_TYPES, default='clothing')
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['size_type', 'order']
    
    def __str__(self):
        return f"{self.name} ({self.get_size_type_display()})"


class ClothingProduct(models.Model):
    """Main clothing product model"""
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)
    sku = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=200, blank=True)
    
    category = models.ForeignKey(ClothingCategory, on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey(ClothingSubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_quantity = models.IntegerField(default=1)
    
    # Available options
    available_colors = models.ManyToManyField(ClothingColor, blank=True, related_name='products')
    available_sizes = models.ManyToManyField(ClothingSize, blank=True, related_name='products')
    
    # Images
    main_image = models.ImageField(upload_to='clothing/products/', blank=True, null=True)
    hover_image = models.ImageField(upload_to='clothing/products/', blank=True, null=True)
    
    # Features
    material = models.CharField(max_length=100, blank=True)
    weight = models.CharField(max_length=50, blank=True)
    features = models.TextField(blank=True, help_text="Comma-separated features")
    
    # Flags
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    available = models.BooleanField(default=True)
    
    # Metadata
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-is_bestseller', 'name']
        verbose_name = 'Clothing Product'
        verbose_name_plural = 'Clothing Products'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:clothing_product_detail', args=[self.category.slug, self.slug])
    
    @property
    def current_price(self):
        return self.sale_price if self.sale_price else self.base_price
    
    @property
    def discount_percentage(self):
        if self.sale_price and self.base_price > self.sale_price:
            return int(((self.base_price - self.sale_price) / self.base_price) * 100)
        return 0
    
    @property
    def features_list(self):
        if self.features:
            return [f.strip() for f in self.features.split(',')]
        return []


class ClothingProductImage(models.Model):
    """Additional product images, can be per color"""
    product = models.ForeignKey(ClothingProduct, on_delete=models.CASCADE, related_name='images')
    color = models.ForeignKey(ClothingColor, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='clothing/products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        color_name = self.color.name if self.color else "Default"
        return f"{self.product.name} - {color_name}"


class ClothingProductPricing(models.Model):
    """Quantity-based pricing tiers"""
    product = models.ForeignKey(ClothingProduct, on_delete=models.CASCADE, related_name='pricing_tiers')
    min_quantity = models.IntegerField()
    max_quantity = models.IntegerField(null=True, blank=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['min_quantity']
    
    def __str__(self):
        max_qty = self.max_quantity if self.max_quantity else "+"
        return f"{self.product.name}: {self.min_quantity}-{max_qty} @ S/{self.price_per_unit}"
