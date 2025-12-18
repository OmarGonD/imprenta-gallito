"""
Shop Models - SISTEMA UNIFICADO CON OPCIONES GENÉRICAS
=======================================================
Este archivo contiene todos los modelos para la aplicación shop.

ARQUITECTURA:
- Category → Subcategory → Product (para TODO)
- ProductOption → ProductOptionValue → ProductVariant (sistema genérico de opciones)

ELIMINADOS:
- ProductColor (reemplazado por ProductOption key='color')
- ProductSize (reemplazado por ProductOption key='size')
- available_colors y available_sizes de Product

NUEVO SISTEMA DE OPCIONES:
Permite añadir cualquier tipo de opción sin tocar código:
- color, size (ropa)
- material, finish, trim (tarjetas)
- material, cassette, mounting (banners)
"""
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal


# ============================================================================
# CHOICES GLOBALES
# ============================================================================

CATEGORY_TYPES = [
    ('quality_tiers', 'Niveles de Calidad'),
    ('product_types', 'Tipos de Producto'),
    ('formats', 'Formatos de Entrega'),
    ('services', 'Servicios'),
    ('occasions', 'Ocasiones'),
    ('standard', 'Estándar'),
]

DISPLAY_STYLES = [
    ('tab', 'Tabs Horizontales'),
    ('circle', 'Círculos con Imagen'),
    ('card', 'Cards con Imagen'),
    ('vertical_card', 'Cards Verticales'),
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
        return self.products.filter(status='active').count()

    def get_active_subcategories(self):
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
        return self.products.filter(status='active')


# ============================================================================
# SISTEMA GENÉRICO DE OPCIONES DE PRODUCTO
# ============================================================================

class ProductOption(models.Model):
    """
    Define un TIPO de opción de producto (color, talla, material, acabado, etc.)
    
    Ejemplos de keys:
    - 'color' para colores de ropa/accesorios
    - 'size' para tallas
    - 'material' para material de banners (lona, vinil, microperforado)
    - 'finish' para acabados de tarjetas (mate, brillante, soft-touch)
    - 'cassette' para sistema de sujeción de banners
    - 'trim' para tipo de corte
    """
    key = models.SlugField(
        max_length=100,
        unique=True,
        help_text="Identificador único: color, size, material, finish, cassette, etc."
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Nombre visible",
        help_text="Nombre que se muestra al usuario: Color, Talla, Material, etc."
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden de visualización"
    )
    is_required = models.BooleanField(
        default=True,
        verbose_name="Es requerido",
        help_text="Si es True, el usuario debe seleccionar una opción"
    )
    selection_type = models.CharField(
        max_length=10,
        choices=[('single', 'Única'), ('multiple', 'Múltiple')],
        default='single',
        verbose_name="Tipo de selección",
        help_text="Única: solo un valor. Múltiple: varios valores posibles"
    )

    class Meta:
        db_table = 'product_options'
        ordering = ['display_order', 'name']
        verbose_name = 'Opción de Producto'
        verbose_name_plural = 'Opciones de Productos'

    def __str__(self):
        return self.name

    def get_active_values(self):
        """Retorna los valores activos de esta opción"""
        return self.values.filter(is_active=True).order_by('display_order')


class ProductOptionValue(models.Model):
    """
    Valor específico para una opción de producto.
    
    Ejemplos:
    - Para option key='color': Rojo, Azul, Negro (con hex_code en el campo 'extra')
    - Para option key='size': XS, S, M, L, XL
    - Para option key='material': Lona 13oz, Vinil, Microperforado
    - Para option key='cassette': Roll-up, X-Banner, Porta Banner
    """
    option = models.ForeignKey(
        ProductOption,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name="Tipo de Opción"
    )
    value = models.CharField(
        max_length=100,
        verbose_name="Valor interno",
        help_text="Identificador interno: rojo, azul, xs, s, lona-13oz"
    )
    display_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nombre visible",
        help_text="Nombre mostrado al usuario. Si está vacío, usa 'value'"
    )
    image = models.ImageField(
        upload_to='option_images/',
        blank=True,
        null=True,
        verbose_name="Imagen/Muestra",
        help_text="Para colores: muestra del color. Para materiales: textura"
    )
    hex_code = models.CharField(
        max_length=7,
        blank=True,
        verbose_name="Código Hex",
        help_text="Solo para colores: #FF5733"
    )
    additional_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Precio adicional",
        help_text="Costo extra al seleccionar esta opción"
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden de visualización"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )

    class Meta:
        db_table = 'product_option_values'
        ordering = ['option', 'display_order', 'display_name']
        verbose_name = 'Valor de Opción'
        verbose_name_plural = 'Valores de Opciones'
        unique_together = ['option', 'value']

    def __str__(self):
        return f"{self.option.name}: {self.get_display_name()}"

    def get_display_name(self):
        """Retorna display_name si existe, sino value"""
        return self.display_name or self.value

    def has_additional_cost(self):
        return self.additional_price > 0


class ProductVariant(models.Model):
    """
    Relaciona un Producto con los tipos de opciones que tiene disponibles.
    
    Ejemplo: El polo "polo-algodon-180g" tiene:
    - ProductVariant(product=polo, option=color)
    - ProductVariant(product=polo, option=size)
    
    Para banners "banner-roll-up" tendría:
    - ProductVariant(product=banner, option=material)
    - ProductVariant(product=banner, option=cassette)
    """
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='variant_options',
        verbose_name="Producto"
    )
    option = models.ForeignKey(
        ProductOption,
        on_delete=models.CASCADE,
        related_name='product_variants',
        verbose_name="Tipo de Opción"
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden de visualización",
        help_text="Orden en que aparece esta opción en el producto"
    )
    # Valores específicos disponibles para este producto (subset de ProductOptionValue)
    available_values = models.ManyToManyField(
        ProductOptionValue,
        blank=True,
        related_name='product_variants',
        verbose_name="Valores disponibles",
        help_text="Si está vacío, todos los valores activos de la opción están disponibles"
    )

    class Meta:
        db_table = 'product_variants'
        ordering = ['product', 'display_order']
        verbose_name = 'Variante de Producto'
        verbose_name_plural = 'Variantes de Productos'
        unique_together = ['product', 'option']

    def __str__(self):
        return f"{self.product.name} - {self.option.name}"

    def get_available_values(self):
        """
        Retorna los valores disponibles para este producto.
        Si available_values está vacío, retorna todos los valores activos de la opción.
        """
        if self.available_values.exists():
            return self.available_values.filter(is_active=True).order_by('display_order')
        return self.option.values.filter(is_active=True).order_by('display_order')


# ============================================================================
# PRODUCTO UNIFICADO
# ============================================================================

class Product(models.Model):
    """
    Producto unificado que soporta tanto productos de imprenta como ropa.
    Las opciones (color, talla, material, etc.) se manejan via ProductVariant.
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

    # Características del producto
    material = models.CharField(max_length=100, blank=True,
                                verbose_name="Material/Marca",
                                help_text="Material del producto o marca para ropa")
    weight = models.CharField(max_length=50, blank=True, verbose_name="Peso")
    features = models.TextField(blank=True,
                                help_text="Para ropa: genero:unisex,cuello:cuello_redondo",
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

    # =========================================================================
    # MÉTODOS DE PRECIOS
    # =========================================================================

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
        if self.base_price:
            return self.base_price
        first_tier = self.price_tiers.order_by('min_quantity').first()
        return first_tier.unit_price if first_tier else None

    @property
    def discount_percentage(self):
        """Calcula el porcentaje de descuento"""
        if self.sale_price and self.base_price and self.base_price > self.sale_price:
            return int(((self.base_price - self.sale_price) / self.base_price) * 100)
        return 0

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

    # =========================================================================
    # MÉTODOS DE CARACTERÍSTICAS
    # =========================================================================

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

    # =========================================================================
    # MÉTODOS DE OPCIONES/VARIANTES (NUEVO SISTEMA)
    # =========================================================================

    def get_variant_options(self):
        """
        Retorna lista de diccionarios con las opciones disponibles para este producto.
        Optimizado para usar directamente en templates.
        
        Retorna:
        [
            {
                'key': 'color',
                'name': 'Color',
                'is_required': True,
                'selection_type': 'single',
                'values': [
                    {'value': 'rojo', 'display_name': 'Rojo', 'hex_code': '#FF0000', 
                     'image': '/media/option_images/rojo.jpg', 'additional_price': Decimal('0.00')},
                    {'value': 'azul', 'display_name': 'Azul', 'hex_code': '#0000FF', ...},
                ]
            },
            {
                'key': 'size',
                'name': 'Talla',
                'is_required': True,
                'values': [...]
            },
        ]
        """
        result = []
        
        variants = self.variant_options.select_related('option').prefetch_related(
            'available_values',
            'option__values'
        ).order_by('display_order')
        
        for variant in variants:
            option = variant.option
            values = variant.get_available_values()
            
            option_data = {
                'key': option.key,
                'name': option.name,
                'is_required': option.is_required,
                'selection_type': option.selection_type,
                'values': []
            }
            
            for val in values:
                option_data['values'].append({
                    'value': val.value,
                    'display_name': val.get_display_name(),
                    'hex_code': val.hex_code,
                    'image': val.image.url if val.image else None,
                    'additional_price': val.additional_price,
                    'has_additional_cost': val.has_additional_cost(),
                })
            
            result.append(option_data)
        
        return result

    def get_option_by_key(self, key):
        """
        Retorna los valores de una opción específica por su key.
        Útil para obtener solo colores o solo tallas.
        
        Uso: product.get_option_by_key('color')
        """
        try:
            variant = self.variant_options.select_related('option').prefetch_related(
                'available_values', 'option__values'
            ).get(option__key=key)
            return variant.get_available_values()
        except ProductVariant.DoesNotExist:
            return ProductOptionValue.objects.none()

    def has_option(self, key):
        """Verifica si el producto tiene una opción específica"""
        return self.variant_options.filter(option__key=key).exists()

    def has_colors(self):
        """Verifica si el producto tiene colores disponibles (retrocompatibilidad)"""
        return self.has_option('color')

    def has_sizes(self):
        """Verifica si el producto tiene tallas disponibles (retrocompatibilidad)"""
        return self.has_option('size')

    def get_colors(self):
        """Retorna los colores disponibles (retrocompatibilidad)"""
        return self.get_option_by_key('color')

    def get_sizes(self):
        """Retorna las tallas disponibles (retrocompatibilidad)"""
        return self.get_option_by_key('size')

    def is_clothing_product(self):
        """Determina si es un producto de ropa (tiene color o talla)"""
        return self.has_option('color') or self.has_option('size')


# ============================================================================
# IMÁGENES DE PRODUCTO
# ============================================================================

class ProductImage(models.Model):
    """
    Imágenes adicionales del producto, opcionalmente asociadas a un valor de opción.
    Por ejemplo: imagen del polo en color rojo.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    option_value = models.ForeignKey(
        ProductOptionValue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='product_images',
        verbose_name="Valor de opción",
        help_text="Opcional: asociar esta imagen a un color/material específico"
    )
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
        option_name = self.option_value.get_display_name() if self.option_value else "Default"
        return f"{self.product.name} - {option_name}"

    def get_option_info(self):
        """Retorna información del valor de opción asociado"""
        if self.option_value:
            return {
                'option_key': self.option_value.option.key,
                'value': self.option_value.value,
                'display_name': self.option_value.get_display_name(),
            }
        return None


# ============================================================================
# PRECIOS POR VOLUMEN
# ============================================================================

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

    @property
    def is_complete(self):
        required_fields = [
            self.dni, 
            self.phone_number, 
            self.shipping_address1, 
            self.shipping_department, 
            self.shipping_province, 
            self.shipping_district,
        ]
        return all(field and str(field).strip() for field in required_fields)

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

