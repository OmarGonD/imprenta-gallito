"""
==============================================================================
DEPRECATED FILE - catalog_models.py
==============================================================================

MIGRATION NOTE (2024):
This file is DEPRECATED and will be removed in a future migration.

The models have been migrated to shop/models.py:
- CatalogCategory -> Category (in models.py)
- CatalogSubcategory -> Subcategory (in models.py)
- CatalogProduct, VariantType, VariantOption, ProductVariantType, PriceTier
  have all been moved to models.py

DO NOT USE THESE MODELS FOR NEW CODE.
Import from shop.models instead:

    from shop.models import (
        Category,
        Subcategory,
        CatalogProduct,
        VariantType,
        VariantOption,
        ProductVariantType,
        PriceTier
    )

The models below are commented out to prevent duplicate model definitions.
Running `makemigrations` after this change will properly handle the migration.

==============================================================================
"""

# =============================================================================
# DEPRECATED MODELS - DO NOT USE
# These have been migrated to shop/models.py
# =============================================================================

# from django.db import models
# from django.urls import reverse
# from decimal import Decimal


# class CatalogCategory(models.Model):
#     """
#     DEPRECATED - Use Category from shop.models instead
#     
#     Categorías principales del catálogo personalizable
#     Separadas del modelo Category existente
#     """
#     slug = models.SlugField(max_length=250, unique=True, primary_key=True, 
#                            help_text="Identificador único de la categoría")
#     name = models.CharField(max_length=250, verbose_name="Nombre")
#     description = models.TextField(blank=True, verbose_name="Descripción")
#     image_url = models.CharField(max_length=500, blank=True, verbose_name="URL de imagen")
#     display_order = models.IntegerField(default=0, verbose_name="Orden de visualización",
#                                        help_text="Menor número aparece primero")
#     status = models.CharField(max_length=20, default='active',
#                              choices=[('active', 'Activo'), ('seasonal', 'Temporal')],
#                              verbose_name="Estado")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'catalog_category'
#         ordering = ['display_order', 'name']
#         verbose_name = 'Categoría del Catálogo'
#         verbose_name_plural = 'Categorías del Catálogo'
#         indexes = [
#             models.Index(fields=['status']),
#             models.Index(fields=['display_order']),
#         ]
#
#     def __str__(self):
#         return self.name
#
#     def get_absolute_url(self):
#         return reverse('catalog:category', args=[self.slug])
#
#     def get_active_products_count(self):
#         """Retorna el número de productos activos en esta categoría"""
#         return self.catalog_products.filter(status='active').count()


# class CatalogSubcategory(models.Model):
#     """
#     DEPRECATED - Use Subcategory from shop.models instead
#     
#     Subcategorías del catálogo personalizable
#     """
#     slug = models.SlugField(max_length=250, unique=True, primary_key=True,
#                            help_text="Identificador único de la subcategoría")
#     name = models.CharField(max_length=250, verbose_name="Nombre")
#     category = models.ForeignKey(CatalogCategory, on_delete=models.CASCADE,
#                                  related_name='subcategories',
#                                  verbose_name="Categoría")
#     description = models.TextField(blank=True, verbose_name="Descripción")
#     image_url = models.CharField(max_length=500, blank=True, verbose_name="URL de imagen")
#     display_order = models.IntegerField(default=0, verbose_name="Orden de visualización")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'catalog_subcategory'
#         ordering = ['display_order', 'name']
#         verbose_name = 'Subcategoría del Catálogo'
#         verbose_name_plural = 'Subcategorías del Catálogo'
#         indexes = [
#             models.Index(fields=['category', 'display_order']),
#         ]
#
#     def __str__(self):
#         return f"{self.category.name} > {self.name}"
#
#     def get_absolute_url(self):
#         return reverse('catalog:subcategory', args=[self.category.slug, self.slug])


# class CatalogProduct(models.Model):
#     """
#     DEPRECATED - Use CatalogProduct from shop.models instead
#     
#     Producto personalizable del catálogo
#     """
#     slug = models.SlugField(max_length=250, primary_key=True,
#                            help_text="Identificador único del producto")
#     name = models.CharField(max_length=250, verbose_name="Nombre del Producto")
#     category = models.ForeignKey(CatalogCategory, on_delete=models.CASCADE,
#                                  related_name='catalog_products',
#                                  verbose_name="Categoría")
#     subcategory = models.ForeignKey(CatalogSubcategory, on_delete=models.SET_NULL,
#                                     null=True, blank=True,
#                                     related_name='catalog_products',
#                                     verbose_name="Subcategoría")
#     sku = models.CharField(max_length=50, unique=True, verbose_name="SKU",
#                           help_text="Código único del producto")
#     description = models.TextField(blank=True, verbose_name="Descripción")
#     base_image_url = models.CharField(max_length=500, blank=True,
#                                       verbose_name="URL de imagen base")
#     status = models.CharField(max_length=20, default='active',
#                              choices=[('active', 'Activo'), ('seasonal', 'Temporal')],
#                              verbose_name="Estado")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'catalog_product'
#         ordering = ['name']
#         verbose_name = 'Producto del Catálogo'
#         verbose_name_plural = 'Productos del Catálogo'
#         indexes = [
#             models.Index(fields=['category', 'status']),
#             models.Index(fields=['subcategory', 'status']),
#             models.Index(fields=['sku']),
#         ]
#
#     def __str__(self):
#         return self.name
#
#     def get_absolute_url(self):
#         return reverse('shop:catalog_product_detail', 
#                       args=[self.category.slug, self.slug])
#
#     def get_base_price(self, quantity=1):
#         tier = self.price_tiers.filter(
#             min_quantity__lte=quantity,
#             max_quantity__gte=quantity
#         ).first()
#         
#         if tier:
#             return tier.unit_price
#         
#         first_tier = self.price_tiers.order_by('min_quantity').first()
#         return first_tier.unit_price if first_tier else Decimal('0.00')
#
#     def get_price_range(self):
#         tiers = self.price_tiers.all()
#         if not tiers:
#             return (Decimal('0.00'), Decimal('0.00'))
#         
#         prices = [tier.unit_price for tier in tiers]
#         return (min(prices), max(prices))
#
#     def get_available_variant_types(self):
#         return VariantType.objects.filter(
#             product_variant_types__product=self
#         ).order_by('display_order')


# class VariantType(models.Model):
#     """
#     DEPRECATED - Use VariantType from shop.models instead
#     """
#     slug = models.SlugField(max_length=250, unique=True, primary_key=True,
#                            help_text="Identificador único del tipo de variante")
#     name = models.CharField(max_length=250, verbose_name="Nombre")
#     description = models.TextField(blank=True, verbose_name="Descripción")
#     is_required = models.BooleanField(default=False, verbose_name="Es requerido",
#                                       help_text="Si es true, el usuario debe seleccionar una opción")
#     allows_multiple = models.BooleanField(default=False, verbose_name="Permite múltiples",
#                                          help_text="Si permite seleccionar múltiples opciones")
#     display_order = models.IntegerField(default=0, verbose_name="Orden de visualización")
#     applies_to = models.CharField(max_length=100, blank=True, null=True,
#                                   verbose_name="Aplica a",
#                                   help_text="Categorías o tipos de productos a los que aplica")
#
#     class Meta:
#         db_table = 'variant_type'
#         ordering = ['display_order', 'name']
#         verbose_name = 'Tipo de Variante'
#         verbose_name_plural = 'Tipos de Variantes'
#         indexes = [
#             models.Index(fields=['display_order']),
#         ]
#
#     def __str__(self):
#         return self.name
#
#     def get_options_count(self):
#         return self.options.count()


# class VariantOption(models.Model):
#     """
#     DEPRECATED - Use VariantOption from shop.models instead
#     """
#     slug = models.SlugField(max_length=250, primary_key=True,
#                            help_text="Identificador único de la opción")
#     variant_type = models.ForeignKey(VariantType, on_delete=models.CASCADE,
#                                      related_name='options',
#                                      verbose_name="Tipo de Variante")
#     name = models.CharField(max_length=250, verbose_name="Nombre")
#     description = models.TextField(blank=True, verbose_name="Descripción")
#     additional_price = models.DecimalField(max_digits=10, decimal_places=2,
#                                           default=Decimal('0.00'),
#                                           verbose_name="Precio adicional",
#                                           help_text="Costo extra por seleccionar esta opción")
#     image_url = models.CharField(max_length=500, blank=True, null=True,
#                                 verbose_name="URL de imagen")
#     display_order = models.IntegerField(default=0, verbose_name="Orden de visualización")
#
#     class Meta:
#         db_table = 'variant_option'
#         ordering = ['variant_type', 'display_order', 'name']
#         verbose_name = 'Opción de Variante'
#         verbose_name_plural = 'Opciones de Variantes'
#         indexes = [
#             models.Index(fields=['variant_type', 'display_order']),
#         ]
#
#     def __str__(self):
#         return f"{self.variant_type.name}: {self.name}"
#
#     def has_additional_cost(self):
#         return self.additional_price > 0


# class ProductVariantType(models.Model):
#     """
#     DEPRECATED - Use ProductVariantType from shop.models instead
#     """
#     product = models.ForeignKey(CatalogProduct, on_delete=models.CASCADE,
#                                 related_name='product_variant_types',
#                                 verbose_name="Producto")
#     variant_type = models.ForeignKey(VariantType, on_delete=models.CASCADE,
#                                      related_name='product_variant_types',
#                                      verbose_name="Tipo de Variante")
#
#     class Meta:
#         db_table = 'product_variant_type'
#         unique_together = ['product', 'variant_type']
#         verbose_name = 'Variante de Producto'
#         verbose_name_plural = 'Variantes de Productos'
#         indexes = [
#             models.Index(fields=['product']),
#             models.Index(fields=['variant_type']),
#         ]
#
#     def __str__(self):
#         return f"{self.product.name} - {self.variant_type.name}"


# class PriceTier(models.Model):
#     """
#     DEPRECATED - Use PriceTier from shop.models instead
#     """
#     product = models.ForeignKey(CatalogProduct, on_delete=models.CASCADE,
#                                 related_name='price_tiers',
#                                 verbose_name="Producto")
#     min_quantity = models.IntegerField(verbose_name="Cantidad mínima",
#                                        help_text="Cantidad mínima para este precio")
#     max_quantity = models.IntegerField(verbose_name="Cantidad máxima",
#                                        help_text="Cantidad máxima para este precio")
#     unit_price = models.DecimalField(max_digits=10, decimal_places=2,
#                                      verbose_name="Precio unitario",
#                                      help_text="Precio por unidad en este rango")
#     discount_percentage = models.IntegerField(default=0,
#                                              verbose_name="Porcentaje de descuento",
#                                              help_text="Descuento aplicado respecto al precio base")
#
#     class Meta:
#         db_table = 'price_tier'
#         ordering = ['product', 'min_quantity']
#         unique_together = ['product', 'min_quantity']
#         verbose_name = 'Nivel de Precio'
#         verbose_name_plural = 'Niveles de Precios'
#         indexes = [
#             models.Index(fields=['product', 'min_quantity']),
#         ]
#
#     def __str__(self):
#         return f"{self.product.name}: {self.min_quantity}-{self.max_quantity} @ S/{self.unit_price}"
#
#     def get_range_display(self):
#         if self.max_quantity >= 999999:
#             return f"{self.min_quantity}+"
#         return f"{self.min_quantity}-{self.max_quantity}"
#
#     def get_total_for_quantity(self, quantity):
#         if self.min_quantity <= quantity <= self.max_quantity:
#             return self.unit_price * quantity
#         return None
#
#     def is_quantity_in_range(self, quantity):
#         return self.min_quantity <= quantity <= self.max_quantity
