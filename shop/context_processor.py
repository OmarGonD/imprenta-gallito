"""
Context processors for the shop application.

MIGRATION NOTE (2024):
- Removed import from catalog_models.py (deprecated)
- For catalog system, use Category from shop.models
"""
import re
from django.db.models import Prefetch


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


def nav_categories(request):
    """Provide categories with subcategories for navigation"""
    cats = []
    try:
        from django.db import connection
        table_names = connection.introspection.table_names()
        if 'categories' not in table_names and 'shop_category' not in table_names:
            return {'categories': []}
        
        from .models import Category, Subcategory
        cats = list(Category.objects.filter(
            status='active'
        ).prefetch_related(
            Prefetch(
                'subcategories',
                queryset=Subcategory.objects.filter(status='active').order_by('display_order', 'name')
            )
        ).order_by('display_order', 'name')[:20])
    except Exception as e:
        print(f"❌ Error en nav_categories: {e}")  # Para debug
    
    return {'categories': cats}
