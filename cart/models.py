from django.db import models
from shop.models import Product


TAMANIOS = (
    ('A3', 'A3'),
    ('A4', 'A4'),
    ('A5', 'A5'),
    ('A6', 'A6'),
    ('A7', 'A7'),
    ('medio-oficio', 'Medio oficio'),
    ('oficio', 'Oficio'),
    ('carta', 'Carta'),
    ('4x8', '4 x 8'),
    ('5x10', '5 x 10'),
    ('5x14', '5 x 14'),
    ('5x17', '5 x 17'),
    ('3x5', '3 x 5'),
    ('10x14', '10 x 14'),
    ('10x17', '10 x 17'),
    ('10x21', '10 x 21'),
    ('14x21', '14 x 21'),
)

CANTIDADES = (
    ('100', '100'),
    ('200', '200'),
    ('250', '250'),
    ('500', '500'),
    ('1000', '1000'),
    ('1500', '1500'),
    ('2000', '2000'),
    ('2500', '2500'),
    ('3000', '3000'),
    ('4000', '4000'),
    ('5000', '5000'),
    ('10000', '10000'),
    ('15000', '15000'),
    ('20000', '20000'),
    ('30000', '30000'),
    ('50000', '50000'),
)


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'Cart'
        ordering = ['date_added']

    def __str__(self):
        return self.cart_id
    


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=20, choices=TAMANIOS, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    design_file = models.FileField(upload_to='designs/%Y/%m/%d/', blank=True, null=True, max_length=500)
    comment = models.CharField(max_length=100, blank=True, null=True, default='')
    color = models.CharField(max_length=100, blank=True, null=True, verbose_name="Color")
    color_image_url = models.URLField(max_length=500, blank=True, null=True, 
                                       verbose_name="URL de imagen del color")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    step_two_complete = models.BooleanField(default=False)
    
    # ===== NUEVOS CAMPOS PARA TARJETAS DE PRESENTACIÓN =====
    # Logo de empresa (opcional)
    logo_file = models.FileField(
        upload_to='logos/%Y/%m/%d/', 
        blank=True, 
        null=True, 
        max_length=500,
        verbose_name='Logo de empresa'
    )
    
    # Datos de contacto para la tarjeta
    contact_name = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='Nombre completo'
    )
    contact_phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name='Celular'
    )
    contact_address = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name='Dirección física'
    )
    contact_social = models.URLField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name='Red social / Web'
    )
    contact_email = models.EmailField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Correo electrónico'
    )
    contact_job_title = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Cargo / Profesión'
    )
    contact_company = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Empresa'
    )
    
    # Nuevo campo para información extra dinámica (Bodas, etc.)
    additional_info = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Información Adicional"
    )
    # =========================================================

    class Meta:
        db_table = 'CartItem'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
    @property
    def sub_total(self):
        """Calcula el subtotal basándose en la cantidad y precio del tier"""
        quantity = self.get_quantity_int()
        unit_price = self.get_unit_price()
        return quantity * unit_price
    
    # ===== MÉTODOS PARA ARCHIVOS =====
    
    def get_file_name(self):
        """Retorna solo el nombre del archivo sin la ruta"""
        if self.design_file:
            import os
            return os.path.basename(self.design_file.name)
        return ''
    
    def get_file_extension(self):
        """Retorna la extensión del archivo"""
        if self.design_file:
            import os
            _, ext = os.path.splitext(self.design_file.name)
            return ext.lower().replace('.', '')
        return ''
    
    def get_file_size_mb(self):
        """Retorna el tamaño del archivo en MB"""
        if self.design_file:
            try:
                size_bytes = self.design_file.size
                return round(size_bytes / (1024 * 1024), 2)
            except:
                pass
        return 0
    
    @property
    def is_image_file(self):
        """Verifica si el archivo es una imagen"""
        ext = self.get_file_extension()
        return ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff']
    
    @property
    def is_pdf_file(self):
        """Verifica si el archivo es PDF"""
        return self.get_file_extension() == 'pdf'
    
    # ===== MÉTODOS PARA LOGO =====
    
    def get_logo_name(self):
        """Retorna el nombre del archivo de logo"""
        if self.logo_file:
            import os
            return os.path.basename(self.logo_file.name)
        return ''
    
    def get_logo_extension(self):
        """Retorna la extensión del logo"""
        if self.logo_file:
            import os
            _, ext = os.path.splitext(self.logo_file.name)
            return ext.lower().replace('.', '')
        return ''
    
    @property
    def has_logo(self):
        """Verifica si tiene logo subido"""
        return bool(self.logo_file)
    
    # ===== MÉTODOS PARA TEMPLATES =====
    
    def get_design_type(self):
        """Retorna 'template' o 'custom'"""
        if self.comment and self.comment.startswith('template:'):
            return 'template'
        return 'custom'
    
    def get_template_slug(self):
        """Retorna el slug del template (ej: 'tp-01rnz') o None"""
        if self.comment and self.comment.startswith('template:'):
            return self.comment.replace('template:', '').strip()
        return None
    
    def get_template_info(self):
        """Retorna un diccionario con info del template"""
        template_slug = self.get_template_slug()
        if not template_slug:
            return None
        
        # 1. Intentar buscar en base de datos (DesignTemplate)
        try:
            from shop.models import DesignTemplate
            template = DesignTemplate.objects.get(slug=template_slug)
            return {
                'slug': template.slug,
                'name': template.name,
                'thumbnail_url': template.thumbnail_url or template.preview_url
            }
        except Exception:
            pass
        
        # 2. Intentar cargar desde TemplateLoader (Legacy)
        try:
            from shop.template_loader import TemplateLoader
            return TemplateLoader.get_by_slug(template_slug)
        except (ImportError, Exception):
            pass
        
        # 3. Fallback: construir info básica (Asume tarjetas de presentación por defecto)
        return {
            'slug': template_slug,
            'name': f'Diseño {template_slug.upper()}',
            'thumbnail_url': f'/static/media/template_images/templates_tarjetas_presentacion/{template_slug.upper()}.jpg'
        }
    
    def get_template_thumbnail_url(self):
        """Retorna la URL del thumbnail del template"""
        template_info = self.get_template_info()
        if template_info:
            return template_info.get('thumbnail_url', '')
        return ''
    
    def get_design_display(self):
        """Retorna texto amigable para mostrar: 'Plantilla TP-01RNZ' o 'Diseño personalizado'"""
        if self.get_design_type() == 'template':
            slug = self.get_template_slug()
            return f"Plantilla {slug.upper() if slug else ''}"
        return "Diseño personalizado"
    
    # ===== MÉTODOS PARA CANTIDAD Y PRECIO =====
    
    def get_quantity_int(self):
        """Retorna la cantidad como entero"""
        if self.quantity:
            try:
                # Limpiar cualquier caracter no numérico
                clean_qty = ''.join(filter(str.isdigit, str(self.quantity)))
                return int(clean_qty) if clean_qty else 0
            except (ValueError, TypeError):
                pass
        return 0
    
    def get_unit_price(self):
        """Retorna el precio unitario según el tier de cantidad"""
        quantity = self.get_quantity_int()
        if not quantity or not self.product:
            return 0
        
        # Buscar el tier que corresponde a esta cantidad
        tier = self.product.price_tiers.filter(
            min_quantity__lte=quantity,
            max_quantity__gte=quantity
        ).first()
        
        if tier:
            return tier.unit_price
        
        # Fallback: usar el primer tier disponible
        first_tier = self.product.price_tiers.order_by('min_quantity').first()
        return first_tier.unit_price if first_tier else 0
    
    # ===== MÉTODOS PARA DATOS DE CONTACTO =====
    
    def has_contact_info(self):
        """Verifica si tiene datos de contacto ingresados"""
        return bool(self.contact_name or self.contact_phone)
    
    def get_contact_summary(self):
        """Retorna un resumen de los datos de contacto"""
        parts = []
        if self.contact_name:
            parts.append(self.contact_name)
        if self.contact_job_title:
            parts.append(self.contact_job_title)
        if self.contact_company:
            parts.append(self.contact_company)
        return ' - '.join(parts) if parts else 'Sin datos de contacto'
    
    def is_ready_for_print(self):
        """Verifica si el item tiene toda la info necesaria para imprimir"""
        # Debe tener: diseño (template o archivo) + datos de contacto básicos
        has_design = bool(self.get_template_slug() or self.design_file)
        has_contact = bool(self.contact_name and self.contact_phone)
        return has_design and has_contact
