from django.db import models
from django.http import HttpResponse

from shop.models import Product
from shop.sizes_and_quantities import TAMANIOS, CANTIDADES
from decimal import Decimal

# Variables


# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length=100)
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'Cart'
        ordering = ['date_added']

    def __str__(self):
        return str(self.id)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=20, choices=TAMANIOS, blank=True, null=True)
    quantity = models.CharField(max_length=20, choices=CANTIDADES, blank=True, null=True)
    design_file = models.FileField(upload_to='designs/%Y/%m/%d/', blank=True, null=True, max_length=500)
    comment = models.CharField(max_length=100, blank=True, null=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    step_two_complete = models.BooleanField(default=False)

    class Meta:
        db_table = 'CartItem'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.product.name} - {self.quantity or 'N/A'}"

    def sub_total(self):
        """Calculate subtotal based on product price tiers"""
        if not self.product or not self.quantity:
            return 0
        
        quantity = int(''.join(filter(str.isdigit, self.quantity)))
        tier = self.product.price_tiers.filter(
            min_quantity__lte=quantity,
            max_quantity__gte=quantity
        ).first()
        
        if tier:
            return tier.unit_price * quantity
        
        # Fallback to first tier
        first_tier = self.product.price_tiers.order_by('min_quantity').first()
        return first_tier.unit_price * quantity if first_tier else 0

    def get_file_extension(self):
        """Get the file extension in lowercase"""
        if self.design_file:
            import os
            return os.path.splitext(self.design_file.name)[1].lower()
        return None

    def is_image_file(self):
        """Check if the uploaded file is an image"""
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
        return self.get_file_extension() in image_extensions
    
    def is_pdf_file(self):
        """Check if the uploaded file is a PDF"""
        return self.get_file_extension() == '.pdf'

    def get_file_size_mb(self):
        """Get file size in megabytes"""
        if self.design_file:
            try:
                return round(self.design_file.size / (1024 * 1024), 2)
            except:
                return 0
        return 0
    
    def get_file_name(self):
        """Get clean filename without path"""
        if self.design_file:
            import os
            return os.path.basename(self.design_file.name)
        return None
    
    @property
    def total_price(self):
        """Calculate total price for this cart item"""
        return self.sub_total()
