from django import template

register = template.Library()

@register.filter(name = 'percentof')
def percent_of_total(row_sale, total_sale):
    return round(row_sale * 100 / total_sale, ndigits = 0)
