"""
Shop Models
============
This file contains all models for the shop application.

MIGRATION NOTE (2024):
- CatalogCategory has been renamed to Category
- CatalogSubcategory has been renamed to Subcategory
- The old models in catalog_models.py are deprecated and will be removed
- The legacy Category model (for Product, Pack, Sample) has been renamed to LegacyCategory
"""
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from .sizes_and_quantities import TAMANIOS, CANTIDADES


# ============================================================================
# CATALOG SYSTEM MODELS (Migrated from catalog_models.py)
# These are the primary models for the new catalog/product system
# ============================================================================

from django.db import models
from django.urls import reverse
from decimal import Decimal


class Category(models.Model):
    """
    Categorías principales del catálogo personalizable
    """
    slug = models.SlugField(max_length=250, unique=True, primary_key=True, 
                           help_text="Identificador único de la categoría")
    name = models.CharField(max_length=250, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    image_url = models.CharField(max_length=500, blank=True, verbose_name="URL de imagen")
    display_order = models.IntegerField(default=0, verbose_name="Orden de visualización",
                                       help_text="Menor número aparece primero")
    status = models.CharField(max_length=20, default='active',
                             choices=[('active', 'Activo'), ('seasonal', 'Temporal')],
                             verbose_name="Estado")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        ordering = ['display_order', 'name']
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['display_order']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:category', args=[self.slug])

    @property
    def get_url(self):
        return self.get_absolute_url()

    def get_active_products_count(self):
        """Retorna el número de productos activos en esta categoría"""
        return self.products.filter(status='active').count()


class Subcategory(models.Model):
    """
    Subcategorías del catálogo personalizable
    """
    slug = models.SlugField(max_length=250, unique=True, primary_key=True,
                           help_text="Identificador único de la subcategoría")
    name = models.CharField(max_length=250, verbose_name="Nombre")
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='subcategories',
                                 verbose_name="Categoría")
    description = models.TextField(blank=True, verbose_name="Descripción")
    image_url = models.CharField(max_length=500, blank=True, verbose_name="URL de imagen")
    display_order = models.IntegerField(default=0, verbose_name="Orden de visualización")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subcategories'
        ordering = ['display_order', 'name']
        verbose_name = 'Subcategoría'
        verbose_name_plural = 'Subcategorías'
        indexes = [
            models.Index(fields=['category', 'display_order']),
        ]

    def __str__(self):
        return f"{self.category.name} > {self.name}"

    def get_absolute_url(self):
        return reverse('shop:subcategory', args=[self.category.slug, self.slug])

    @property
    def get_url(self):
        return self.get_absolute_url()


class Product(models.Model):
    """Producto personalizable"""
    slug = models.SlugField(max_length=250, primary_key=True,
                           help_text="Identificador único del producto")
    name = models.CharField(max_length=250, verbose_name="Nombre del Producto")
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products',
                                 verbose_name="Categoría")
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL,
                                    null=True, blank=True,
                                    related_name='products',
                                    verbose_name="Subcategoría")
    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU",
                          help_text="Código único del producto")
    description = models.TextField(blank=True, verbose_name="Descripción")
    base_image_url = models.CharField(max_length=500, blank=True,
                                      verbose_name="URL de imagen base")
    status = models.CharField(max_length=20, default='active',
                             choices=[('active', 'Activo'), ('seasonal', 'Temporal')],
                             verbose_name="Estado")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['name']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['subcategory', 'status']),
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', 
                      args=[self.category.slug, self.slug])

    def get_base_price(self, quantity=1):
        """
        Retorna el precio base para una cantidad específica
        
        Args:
            quantity: Cantidad de unidades
            
        Returns:
            Decimal: Precio unitario base según tier de cantidad
        """
        tier = self.price_tiers.filter(
            min_quantity__lte=quantity,
            max_quantity__gte=quantity
        ).first()
        
        if tier:
            return tier.unit_price
        
        # Si no hay tier, buscar el primer tier disponible
        first_tier = self.price_tiers.order_by('min_quantity').first()
        return first_tier.unit_price if first_tier else Decimal('0.00')

    def get_price_range(self):
        """Retorna el rango de precios (min, max)"""
        tiers = self.price_tiers.all()
        if not tiers:
            return (Decimal('0.00'), Decimal('0.00'))
        
        prices = [tier.unit_price for tier in tiers]
        return (min(prices), max(prices))

    def get_available_variant_types(self):
        """Retorna los tipos de variantes disponibles para este producto"""
        return VariantType.objects.filter(
            product_variant_types__product=self
        ).order_by('display_order')


class VariantType(models.Model):
    """
    Tipo de variante (forma, material, talla, color, etc.)
    Define las características personalizables de los productos
    """
    slug = models.SlugField(max_length=250, unique=True, primary_key=True,
                           help_text="Identificador único del tipo de variante")
    name = models.CharField(max_length=250, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_required = models.BooleanField(default=False, verbose_name="Es requerido",
                                      help_text="Si es true, el usuario debe seleccionar una opción")
    allows_multiple = models.BooleanField(default=False, verbose_name="Permite múltiples",
                                         help_text="Si permite seleccionar múltiples opciones")
    display_order = models.IntegerField(default=0, verbose_name="Orden de visualización")
    applies_to = models.CharField(max_length=100, blank=True, null=True,
                                  verbose_name="Aplica a",
                                  help_text="Categorías o tipos de productos a los que aplica")

    class Meta:
        db_table = 'variant_types'
        ordering = ['display_order', 'name']
        verbose_name = 'Tipo de Variante'
        verbose_name_plural = 'Tipos de Variantes'
        indexes = [
            models.Index(fields=['display_order']),
        ]

    def __str__(self):
        return self.name

    def get_options_count(self):
        """Retorna el número de opciones disponibles"""
        return self.options.count()


class VariantOption(models.Model):
    """
    Opción específica de una variante
    Ejemplo: Para el tipo 'color', opciones serían 'rojo', 'azul', etc.
    """
    slug = models.SlugField(max_length=250, primary_key=True,
                           help_text="Identificador único de la opción")
    variant_type = models.ForeignKey(VariantType, on_delete=models.CASCADE,
                                     related_name='options',
                                     verbose_name="Tipo de Variante")
    name = models.CharField(max_length=250, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    additional_price = models.DecimalField(max_digits=10, decimal_places=2,
                                          default=Decimal('0.00'),
                                          verbose_name="Precio adicional",
                                          help_text="Costo extra por seleccionar esta opción")
    image_url = models.CharField(max_length=500, blank=True, null=True,
                                verbose_name="URL de imagen")
    display_order = models.IntegerField(default=0, verbose_name="Orden de visualización")

    class Meta:
        db_table = 'variant_options'
        ordering = ['variant_type', 'display_order', 'name']
        verbose_name = 'Opción de Variante'
        verbose_name_plural = 'Opciones de Variantes'
        indexes = [
            models.Index(fields=['variant_type', 'display_order']),
        ]

    def __str__(self):
        return f"{self.variant_type.name}: {self.name}"

    def has_additional_cost(self):
        """Verifica si esta opción tiene costo adicional"""
        return self.additional_price > 0


class ProductVariantType(models.Model):
    """
    Tabla intermedia que relaciona productos con tipos de variantes
    Define qué variantes están disponibles para cada producto
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='product_variant_types',
                                verbose_name="Producto")
    variant_type = models.ForeignKey(VariantType, on_delete=models.CASCADE,
                                     related_name='product_variant_types',
                                     verbose_name="Tipo de Variante")

    class Meta:
        db_table = 'product_variant_types'
        unique_together = ['product', 'variant_type']
        verbose_name = 'Variante de Producto'
        verbose_name_plural = 'Variantes de Productos'
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['variant_type']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.variant_type.name}"


class PriceTier(models.Model):
    """
    Tier de precios por volumen
    Define precios diferentes según la cantidad comprada
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='price_tiers',
                                verbose_name="Producto")
    min_quantity = models.IntegerField(verbose_name="Cantidad mínima",
                                       help_text="Cantidad mínima para este precio")
    max_quantity = models.IntegerField(verbose_name="Cantidad máxima",
                                       help_text="Cantidad máxima para este precio")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2,
                                     verbose_name="Precio unitario",
                                     help_text="Precio por unidad en este rango")
    discount_percentage = models.IntegerField(default=0,
                                             verbose_name="Porcentaje de descuento",
                                             help_text="Descuento aplicado respecto al precio base")

    class Meta:
        db_table = 'price_tiers'
        ordering = ['product', 'min_quantity']
        unique_together = ['product', 'min_quantity']
        verbose_name = 'Nivel de Precio'
        verbose_name_plural = 'Niveles de Precios'
        indexes = [
            models.Index(fields=['product', 'min_quantity']),
        ]

    def __str__(self):
        return f"{self.product.name}: {self.min_quantity}-{self.max_quantity} @ S/{self.unit_price}"

    def get_range_display(self):
        """Retorna un string amigable del rango de cantidades"""
        if self.max_quantity >= 999999:
            return f"{self.min_quantity}+"
        return f"{self.min_quantity}-{self.max_quantity}"

    def get_total_for_quantity(self, quantity):
        """Calcula el total para una cantidad específica"""
        if self.min_quantity <= quantity <= self.max_quantity:
            return self.unit_price * quantity
        return None

    def is_quantity_in_range(self, quantity):
        """Verifica si una cantidad está dentro del rango de este tier"""
        return self.min_quantity <= quantity <= self.max_quantity



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
    type = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('premium', 'Premium'), ('deluxe', 'Deluxe')],
        default='standard',
        verbose_name="Tipo"
    )
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
    category = models.ForeignKey(ClothingCategory, on_delete=models.CASCADE, related_name='clothing_subcategories')
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
