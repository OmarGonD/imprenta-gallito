"""
Shop Models - SISTEMA UNIFICADO
================================
Este archivo contiene todos los modelos para la aplicación shop.

ARQUITECTURA UNIFICADA:
- Category → Subcategory → Product (para TODO, incluyendo ropa)
- ProductColor y ProductSize como modelos auxiliares
- Los modelos Clothing* han sido eliminados (redundantes)

El CSV subcategories_complete.csv ahora funciona directamente.
"""
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from .sizes_and_quantities import TAMANIOS, CANTIDADES


# ============================================================================
# CHOICES GLOBALES
# ============================================================================

CATEGORY_TYPES = [
    ('quality_tiers', 'Niveles de Calidad'),      # Tarjetas: Deluxe > Premium > Estándar
    ('product_types', 'Tipos de Producto'),        # Ropa: Polos, Gorros, Bolsos
    ('formats', 'Formatos de Entrega'),            # Stickers: Individual, Plancha, Rollo
    ('services', 'Servicios'),                     # Diseño: Logo, Web, Redes
    ('occasions', 'Ocasiones'),                    # Invitaciones: Boda, Cumpleaños
    ('standard', 'Estándar'),                      # Default
]

DISPLAY_STYLES = [
    ('tab', 'Tabs Horizontales'),          # Para quality_tiers
    ('circle', 'Círculos con Imagen'),     # Para product_types (ropa, promocionales)
    ('card', 'Cards con Imagen'),          # Para formats
    ('vertical_card', 'Cards Verticales'), # Para services
]

SIZE_TYPES = [
    ('clothing', 'Ropa'),
    ('hat', 'Gorras'),
    ('bag', 'Bolsas'),
    ('universal', 'Universal'),
]


# ============================================================================
# SISTEMA DE CATÁLOGO UNIFICADO
# ============================================================================

class Category(models.Model):
    """
    Categorías principales del catálogo.
    Ejemplos: Tarjetas de Presentación, Ropa y Bolsos, Stickers, etc.
    """
    slug = models.SlugField(max_length=250, unique=True, primary_key=True, 
                           help_text="Identificador único de la categoría")
    name = models.CharField(max_length=250, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    image_url = models.CharField(max_length=500, blank=True, verbose_name="URL de imagen")
    icon = models.CharField(max_length=50, blank=True, 
                           help_text="Clase de Font Awesome, ej: fa-tshirt")
    display_order = models.IntegerField(default=0, verbose_name="Orden de visualización",
                                       help_text="Menor número aparece primero")
    status = models.CharField(max_length=20, default='active',
                             choices=[('active', 'Activo'), ('inactive', 'Inactivo'), ('seasonal', 'Temporal')],
                             verbose_name="Estado")
    category_type = models.CharField(
        max_length=20, 
        choices=CATEGORY_TYPES, 
        default='standard',
        verbose_name="Tipo de Categoría",
        help_text="Define cómo se renderiza esta categoría en el frontend"
    )
    # Campos para template personalizado
    custom_template = models.CharField(
        max_length=100, blank=True,
        verbose_name="Template personalizado",
        help_text="Nombre del template a usar, ej: shop/ropa_bolsos.html"
    )
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
    
    def get_active_subcategories(self):
        """Retorna subcategorías activas ordenadas"""
        return self.subcategories.filter(status='active').order_by('display_order')


class Subcategory(models.Model):
    """
    Subcategorías del catálogo.
    Ejemplos: Polos, Camisas, Gorros (para Ropa y Bolsos)
              Deluxe, Premium, Estándar (para Tarjetas)
    """
    slug = models.SlugField(max_length=250, unique=True, primary_key=True,
                           help_text="Identificador único de la subcategoría")
    name = models.CharField(max_length=250, verbose_name="Nombre")
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='subcategories',
                                 verbose_name="Categoría")
    description = models.TextField(blank=True, verbose_name="Descripción")
    image_url = models.CharField(max_length=500, blank=True, verbose_name="URL de imagen")
    icon = models.CharField(max_length=50, blank=True, 
                           help_text="Clase de Font Awesome, ej: fa-tshirt")
    display_order = models.IntegerField(default=0, verbose_name="Orden de visualización")
    display_style = models.CharField(
        max_length=20,
        choices=DISPLAY_STYLES,
        default='card',
        verbose_name="Estilo de Visualización",
        help_text="Cómo se muestra esta subcategoría en el frontend"
    )
    status = models.CharField(max_length=20, default='active',
                             choices=[('active', 'Activo'), ('inactive', 'Inactivo')],
                             verbose_name="Estado")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subcategories'
        ordering = ['display_order', 'name']
        verbose_name = 'Subcategoría'
        verbose_name_plural = 'Subcategorías'
        indexes = [
            models.Index(fields=['category', 'display_order']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.category.name} > {self.name}"

    def get_absolute_url(self):
        return reverse('shop:subcategory', args=[self.category.slug, self.slug])

    @property
    def get_url(self):
        return self.get_absolute_url()
    
    def get_active_products(self):
        """Retorna productos activos de esta subcategoría"""
        return self.products.filter(status='active')


# ============================================================================
# COLORES Y TALLAS (Aplicables a cualquier producto)
# ============================================================================

class ProductColor(models.Model):
    """Colores disponibles para productos (ropa, accesorios, etc.)"""
    name = models.CharField(max_length=50, verbose_name="Nombre")
    slug = models.SlugField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=7, help_text="Código hex, ej: #FF5733")
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'product_colors'
        ordering = ['display_order', 'name']
        verbose_name = 'Color de Producto'
        verbose_name_plural = 'Colores de Productos'
    
    def __str__(self):
        return self.name


class ProductSize(models.Model):
    """Tallas disponibles para productos"""
    name = models.CharField(max_length=20)  # XS, S, M, L, XL, etc.
    display_name = models.CharField(max_length=50)  # Extra Small, Small, etc.
    size_type = models.CharField(max_length=20, choices=SIZE_TYPES, default='clothing')
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'product_sizes'
        ordering = ['size_type', 'display_order']
        verbose_name = 'Talla de Producto'
        verbose_name_plural = 'Tallas de Productos'
    
    def __str__(self):
        return f"{self.name} ({self.get_size_type_display()})"


# ============================================================================
# PRODUCTO UNIFICADO
# ============================================================================

class Product(models.Model):
    """
    Producto unificado que soporta tanto productos de imprenta como ropa.
    Los campos opcionales se usan según el tipo de producto.
    """
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
    short_description = models.CharField(max_length=200, blank=True,
                                        verbose_name="Descripción corta")
    
    # Imágenes
    base_image_url = models.CharField(max_length=500, blank=True,
                                      verbose_name="URL de imagen principal")
    hover_image_url = models.CharField(max_length=500, blank=True,
                                       verbose_name="URL de imagen hover")
    
    # Precios (para productos simples sin tiers)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, 
                                     null=True, blank=True,
                                     verbose_name="Precio base")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, 
                                     null=True, blank=True,
                                     verbose_name="Precio oferta")
    min_quantity = models.IntegerField(default=1, verbose_name="Cantidad mínima")
    
    # Opciones de personalización (para ropa, accesorios)
    available_colors = models.ManyToManyField(ProductColor, blank=True, 
                                              related_name='products',
                                              verbose_name="Colores disponibles")
    available_sizes = models.ManyToManyField(ProductSize, blank=True, 
                                             related_name='products',
                                             verbose_name="Tallas disponibles")
    
    # Características del producto
    material = models.CharField(max_length=100, blank=True, 
                               verbose_name="Material/Marca",
                               help_text="Material del producto o marca para ropa")
    weight = models.CharField(max_length=50, blank=True, verbose_name="Peso")
    features = models.TextField(blank=True, 
                               help_text="Para ropa: genero:unisex,cuello:cuello_redondo,manga:manga_corta",
                               verbose_name="Características")
    
    # Flags
    is_featured = models.BooleanField(default=False, verbose_name="Destacado")
    is_new = models.BooleanField(default=False, verbose_name="Nuevo")
    is_bestseller = models.BooleanField(default=False, verbose_name="Más vendido")
    
    # Estado y orden
    status = models.CharField(max_length=20, default='active',
                             choices=[('active', 'Activo'), ('inactive', 'Inactivo'), ('seasonal', 'Temporal')],
                             verbose_name="Estado")
    display_order = models.IntegerField(default=0, verbose_name="Orden de visualización")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['-is_featured', '-is_bestseller', 'display_order', 'name']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['subcategory', 'status']),
            models.Index(fields=['sku']),
            models.Index(fields=['is_featured', 'is_bestseller']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # Ropa y bolsos
        if hasattr(self.category, 'parent') and self.category.parent and self.category.parent.slug == "ropa-bolsos":
            return reverse('shop:clothing_product_detail', 
                        kwargs={
                            'category_slug': self.category.slug,
                            'subcategory_slug': self.subcategory.slug,
                            'product_slug': self.slug
                        })
        
        # Catálogos especiales sin subcategoría real
        special_categories = [
            'tarjetas-presentacion', 'empaques', 'folletos', 'posters',
            'invitaciones-regalos', 'bodas', 'productos-promocionales'
        ]
        if self.category and self.category.slug in special_categories:
            return reverse('shop:product_detail', 
                        kwargs={
                            'category_slug': self.category.slug,
                            'subcategory_slug': self.subcategory.slug,
                            'product_slug': self.slug
                        })
                        
        # Productos con subcategoría real
        if hasattr(self, 'subcategory') and self.subcategory:
            return reverse('shop:product_detail', 
                        kwargs={
                            'category_slug': self.category.slug,
                            'subcategory_slug': self.subcategory.slug,
                            'product_slug': self.slug
                        })
        
        # Fallback → siempre 3 niveles
        return reverse('shop:product_detail', 
                    kwargs={
                        'category_slug': self.category.slug,
                        'subcategory_slug': self.subcategory.slug if self.subcategory else 'default',
                        'product_slug': self.slug
                    })

    @property
    def current_price(self):
        """Retorna el precio actual (oferta o base)"""
        if self.sale_price:
            return self.sale_price
        if self.base_price:
            return self.base_price
        first_tier = self.price_tiers.order_by('min_quantity').first()
        return first_tier.unit_price if first_tier else Decimal('0.00')
    
    @property
    def starting_price(self):
        """Retorna el precio inicial más bajo (para mostrar 'Desde S/ X')"""
        # Si tiene precio base directo, úsalo
        if self.base_price:
            return self.base_price
        
        # Si no, obtén el precio del tier con cantidad mínima más baja
        first_tier = self.price_tiers.order_by('min_quantity').first()
        return first_tier.unit_price if first_tier else None
    
    @property
    def discount_percentage(self):
        """Calcula el porcentaje de descuento"""
        if self.sale_price and self.base_price and self.base_price > self.sale_price:
            return int(((self.base_price - self.sale_price) / self.base_price) * 100)
        return 0
    
    @property
    def features_list(self):
        """Retorna las características como lista"""
        if self.features:
            return [f.strip() for f in self.features.split(',')]
        return []
    
    @property
    def features_dict(self):
        """Retorna las características como diccionario (para filtros de ropa)"""
        result = {}
        if self.features:
            for item in self.features.split(','):
                if ':' in item:
                    key, value = item.split(':', 1)
                    result[key.strip()] = value.strip()
        return result

    def get_base_price(self, quantity=1):
        """Retorna el precio base para una cantidad específica (usando tiers)"""
        tier = self.price_tiers.filter(
            min_quantity__lte=quantity,
            max_quantity__gte=quantity
        ).first()
        
        if tier:
            return tier.unit_price
        
        if self.base_price:
            return self.base_price
        first_tier = self.price_tiers.order_by('min_quantity').first()
        return first_tier.unit_price if first_tier else Decimal('0.00')

    def get_price_range(self):
        """Retorna el rango de precios (min, max)"""
        tiers = self.price_tiers.all()
        if not tiers:
            price = self.base_price or Decimal('0.00')
            return (price, price)
        
        prices = [tier.unit_price for tier in tiers]
        return (min(prices), max(prices))

    def get_available_variant_types(self):
        """Retorna los tipos de variantes disponibles para este producto"""
        return VariantType.objects.filter(
            product_variant_types__product=self
        ).order_by('display_order')
    
    def has_colors(self):
        """Verifica si el producto tiene colores disponibles"""
        return self.available_colors.exists()
    
    def has_sizes(self):
        """Verifica si el producto tiene tallas disponibles"""
        return self.available_sizes.exists()


class ProductImage(models.Model):
    """Imágenes adicionales del producto, opcionalmente por color"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    color = models.ForeignKey(ProductColor, on_delete=models.SET_NULL, 
                             null=True, blank=True, related_name='product_images')
    image_url = models.CharField(max_length=500, verbose_name="URL de imagen")
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'product_images'
        ordering = ['display_order']
        verbose_name = 'Imagen de Producto'
        verbose_name_plural = 'Imágenes de Productos'
    
    def __str__(self):
        color_name = self.color.name if self.color else "Default"
        return f"{self.product.name} - {color_name}"


# ============================================================================
# VARIANTES Y PRECIOS
# ============================================================================

class VariantType(models.Model):
    """Tipo de variante (forma, material, acabado, etc.)"""
    slug = models.SlugField(max_length=250, unique=True, primary_key=True,
                           help_text="Identificador único del tipo de variante")
    name = models.CharField(max_length=250, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_required = models.BooleanField(default=False, verbose_name="Es requerido")
    allows_multiple = models.BooleanField(default=False, verbose_name="Permite múltiples")
    display_order = models.IntegerField(default=0, verbose_name="Orden de visualización")
    applies_to = models.CharField(max_length=100, blank=True, null=True,
                                  verbose_name="Aplica a",
                                  help_text="Categorías o tipos de productos")

    class Meta:
        db_table = 'variant_types'
        ordering = ['display_order', 'name']
        verbose_name = 'Tipo de Variante'
        verbose_name_plural = 'Tipos de Variantes'

    def __str__(self):
        return self.name

    def get_options_count(self):
        return self.options.count()


class VariantOption(models.Model):
    """Opción específica de una variante"""
    slug = models.SlugField(max_length=250, primary_key=True)
    variant_type = models.ForeignKey(VariantType, on_delete=models.CASCADE,
                                     related_name='options')
    name = models.CharField(max_length=250, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    additional_price = models.DecimalField(max_digits=10, decimal_places=2,
                                          default=Decimal('0.00'),
                                          verbose_name="Precio adicional")
    image_url = models.CharField(max_length=500, blank=True, null=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'variant_options'
        ordering = ['variant_type', 'display_order', 'name']
        verbose_name = 'Opción de Variante'
        verbose_name_plural = 'Opciones de Variantes'

    def __str__(self):
        return f"{self.variant_type.name}: {self.name}"

    def has_additional_cost(self):
        return self.additional_price > 0


class ProductVariantType(models.Model):
    """Relación producto-variante"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='product_variant_types')
    variant_type = models.ForeignKey(VariantType, on_delete=models.CASCADE,
                                     related_name='product_variant_types')

    class Meta:
        db_table = 'product_variant_types'
        unique_together = ['product', 'variant_type']
        verbose_name = 'Variante de Producto'
        verbose_name_plural = 'Variantes de Productos'

    def __str__(self):
        return f"{self.product.name} - {self.variant_type.name}"


class PriceTier(models.Model):
    """Tier de precios por volumen"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='price_tiers')
    min_quantity = models.IntegerField(verbose_name="Cantidad mínima")
    max_quantity = models.IntegerField(verbose_name="Cantidad máxima")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2,
                                     verbose_name="Precio unitario")
    discount_percentage = models.IntegerField(default=0,
                                             verbose_name="Porcentaje de descuento")

    class Meta:
        db_table = 'price_tiers'
        ordering = ['product', 'min_quantity']
        unique_together = ['product', 'min_quantity']
        verbose_name = 'Nivel de Precio'
        verbose_name_plural = 'Niveles de Precios'

    def __str__(self):
        return f"{self.product.name}: {self.min_quantity}-{self.max_quantity} @ S/{self.unit_price}"

    def get_range_display(self):
        if self.max_quantity >= 999999:
            return f"{self.min_quantity}+"
        return f"{self.min_quantity}-{self.max_quantity}"


# ============================================================================
# USER PROFILE
# ============================================================================

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


# ============================================================================
# PERU (Despachos)
# ============================================================================

class Peru(models.Model):
    departamento = models.CharField(max_length=100, blank=False)
    provincia = models.CharField(max_length=100, blank=False)
    distrito = models.CharField(max_length=100, blank=False)
    costo_despacho_con_recojo = models.IntegerField(default=15)
    costo_despacho_sin_recojo = models.IntegerField(default=15)
    dias_despacho = models.IntegerField(default=4)

    def __str__(self):
        return f"{self.departamento} - {self.provincia} - {self.distrito} - {self.dias_despacho}"


# ============================================================================
# MODELOS LEGACY (Para compatibilidad - considerar migrar o eliminar)
# ============================================================================

class TarjetaPresentacion(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='tarjetas_presentacion', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    type = models.CharField(max_length=20,
        choices=[('standard', 'Standard'), ('premium', 'Premium'), ('deluxe', 'Deluxe')],
        default='standard')
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


# ============================================================================
# DESIGN TEMPLATES
# ============================================================================

class DesignTemplate(models.Model):
    """Templates de diseño predefinidos"""
    slug = models.SlugField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=200, verbose_name="Nombre del Template")
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                related_name='design_templates')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL,
                                   null=True, blank=True,
                                   related_name='design_templates')
    description = models.TextField(blank=True)
    thumbnail_url = models.CharField(max_length=500, verbose_name="URL Miniatura")
    preview_url = models.CharField(max_length=500, blank=True, verbose_name="URL Preview")
    is_popular = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'design_templates'
        ordering = ['-is_popular', 'display_order', 'name']
        verbose_name = 'Template de Diseño'
        verbose_name_plural = 'Templates de Diseño'

    def __str__(self):
        return f"{self.name} ({self.category.name})"


# ============================================================================
# NOTA: Los siguientes modelos han sido ELIMINADOS por ser redundantes:
# - ClothingCategory (usar Category con category_type='product_types')
# - ClothingSubCategory (usar Subcategory con display_style='circle')
# - ClothingProduct (usar Product con available_colors y available_sizes)
# - ClothingProductImage (usar ProductImage)
# - ClothingColor (usar ProductColor)
# - ClothingSize (usar ProductSize)
# - ClothingProductPricing (usar PriceTier)
# ============================================================================
