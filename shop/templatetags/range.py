from django import template

register = template.Library()

@register.filter()
def range(upto=5):
    return range(upto)