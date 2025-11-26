"""
Context processors for the shop application.

MIGRATION NOTE (2024):
- Removed import from catalog_models.py (deprecated)
- For catalog system, use Category from shop.models
"""
import re


def menu_links(request):
    """Provide menu links using Category - returns empty if DB not ready"""
    links = []
    try:
        from django.db import connection
        # Check if table exists first
        table_names = connection.introspection.table_names()
        if 'categories' not in table_names and 'shop_category' not in table_names:
            return dict(links=[])
        
        from .models import Category
        links = list(Category.objects.all()[:20])
    except:
        pass
    return dict(links=links)


def navbar_categories(request):
    """Provide categories for VistaPrint-style navbar - returns empty if DB not ready"""
    categories = []
    try:
        from django.db import connection
        # Check if table exists first
        table_names = connection.introspection.table_names()
        if 'categories' not in table_names and 'shop_category' not in table_names:
            return dict(categories=[])
        
        from .models import Category
        categories = list(Category.objects.filter(
            status='active'
        ).prefetch_related(
            'subcategories'
        ).order_by('display_order', 'name')[:20])
    except:
        pass
    return dict(categories=categories)


def categories(request):
    """Provide catalog categories for the new catalog system - returns empty if DB not ready"""
    cats = []
    try:
        from django.db import connection
        # Check if table exists first
        table_names = connection.introspection.table_names()
        if 'categories' not in table_names and 'shop_category' not in table_names:
            return dict(categories=[])
        
        from .models import Category
        cats = list(Category.objects.filter(
            status='active'
        ).prefetch_related(
            'subcategories'
        ).order_by('display_order', 'name')[:20])
    except:
        pass
    return dict(categories=cats)
