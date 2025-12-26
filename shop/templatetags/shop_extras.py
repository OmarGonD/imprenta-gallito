from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(is_safe=True)
@stringfilter
def endswith(value, suffix):
    return value.endswith(suffix)


@register.filter
def get_image_by_color(product, color_value):
    """
    Find a ProductImage for this product that contains the color slug in its URL.
    Usage: {{ product|get_image_by_color:color.value }}
    """
    if not product or not color_value:
        return ''
    
    # Normalize color for URL matching
    color_slug = color_value.lower().replace(' ', '-').replace('_', '-')
    
    # Search in product images
    for img in product.images.all():
        if img.image_url and color_slug in img.image_url.lower():
            # Return with /static/ prefix for proper URL
            if img.image_url.startswith('/static/'):
                return img.image_url
            return f'/static/{img.image_url}'
    
    return ''
