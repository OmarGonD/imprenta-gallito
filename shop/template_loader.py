"""
Template Loader para Diseños de Tarjetas de Presentación
=========================================================

Compatible con la configuración de Imprenta Gallito:
- WhiteNoise para archivos estáticos
- Heroku en producción
- SQLite en desarrollo

Uso:
    from shop.template_loader import TemplateLoader
    
    templates = TemplateLoader.get_all()
    data = TemplateLoader.get_paginated(page=1, filter_type='popular')
"""

import os
import json
import csv
from django.conf import settings
from django.core.cache import cache
from typing import List, Dict, Optional, Any


class TemplateLoader:
    """
    Cargador de templates de diseño con caché automático.
    
    Detecta automáticamente:
    - Desarrollo local → usa /static/images/templates/tp/
    - Heroku (producción) → usa CDN configurado o static
    """
    
    # === CONFIGURACIÓN ===
    CACHE_KEY = 'design_templates_v1'
    CACHE_TIMEOUT = 3600  # 1 hora
    
    # Categoría por defecto
    DEFAULT_CATEGORY = 'tarjetas-presentacion'
    
    # Cuántos templates marcar como populares/nuevos
    POPULAR_COUNT = 20
    NEW_COUNT = 20
    
    # === URL BASE (se configura automáticamente) ===
    
    @classmethod
    def get_base_url(cls) -> str:
        """
        Retorna la URL base para las imágenes de templates.
        
        Prioridad:
        1. Variable de entorno TEMPLATES_CDN_URL (para CDN externo)
        2. /static/media/template_images/templates_tarjetas_presentacion/ (archivos locales)
        """
        # Si hay CDN configurado, usarlo
        cdn_url = os.environ.get('TEMPLATES_CDN_URL')
        if cdn_url:
            return cdn_url.rstrip('/') + '/'
        
        # Usar archivos estáticos locales (tu ruta existente)
        return '/static/media/template_images/templates_tarjetas_presentacion/'
    
    # === RUTAS DE ARCHIVOS ===
    
    @classmethod
    def get_data_dir(cls) -> str:
        """Retorna el directorio donde están los archivos de datos."""
        return os.path.join(settings.BASE_DIR, 'static', 'data')
    
    @classmethod
    def get_json_path(cls) -> str:
        """Ruta al archivo JSON de templates."""
        return os.path.join(cls.get_data_dir(), 'tp_templates.json')
    
    @classmethod
    def get_csv_path(cls) -> str:
        """Ruta al archivo CSV de templates (fallback)."""
        return os.path.join(cls.get_data_dir(), 'tp_templates.csv')
    
    # === MÉTODOS PÚBLICOS ===
    
    @classmethod
    def get_all(cls, category_slug: str = None) -> List[Dict]:
        """
        Retorna todos los templates (cacheado).
        
        Args:
            category_slug: Filtrar por categoría (opcional)
            
        Returns:
            Lista de diccionarios con datos de cada template
        """
        templates = cls._get_cached_templates()
        
        if category_slug:
            templates = [
                t for t in templates 
                if t.get('category_slug') == category_slug
            ]
        
        return templates
    
    @classmethod
    def get_by_slug(cls, slug: str) -> Optional[Dict]:
        """
        Busca un template por su slug.
        
        Args:
            slug: Identificador único del template
            
        Returns:
            Diccionario con datos del template o None
        """
        slug = slug.lower()
        for template in cls.get_all():
            if template.get('slug') == slug:
                return template
        return None
    
    @classmethod
    def get_popular(cls, limit: int = None) -> List[Dict]:
        """Retorna templates marcados como populares."""
        popular = [t for t in cls.get_all() if t.get('is_popular')]
        if limit:
            popular = popular[:limit]
        return popular
    
    @classmethod
    def get_new(cls, limit: int = None) -> List[Dict]:
        """Retorna templates marcados como nuevos."""
        new = [t for t in cls.get_all() if t.get('is_new')]
        if limit:
            new = new[:limit]
        return new
    
    @classmethod
    def get_paginated(
        cls,
        page: int = 1,
        per_page: int = 24,
        filter_type: str = 'all',
        category_slug: str = None
    ) -> Dict[str, Any]:
        """
        Retorna templates paginados con metadatos de paginación.
        
        Args:
            page: Número de página (1-indexed)
            per_page: Templates por página
            filter_type: 'all', 'popular', o 'new'
            category_slug: Filtrar por categoría
            
        Returns:
            Dict con templates, total, page, total_pages, has_next, has_prev
        """
        all_templates = cls.get_all(category_slug)
        
        if filter_type == 'popular':
            all_templates = [t for t in all_templates if t.get('is_popular')]
        elif filter_type == 'new':
            all_templates = [t for t in all_templates if t.get('is_new')]
        
        total = len(all_templates)
        total_pages = max(1, (total + per_page - 1) // per_page)
        page = max(1, min(page, total_pages))
        
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            'templates': all_templates[start:end],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
            'next_page': page + 1 if page < total_pages else None,
            'prev_page': page - 1 if page > 1 else None,
        }
    
    @classmethod
    def get_stats(cls, category_slug: str = None) -> Dict[str, int]:
        """Retorna estadísticas de templates."""
        all_templates = cls.get_all(category_slug)
        return {
            'total': len(all_templates),
            'popular_count': len([t for t in all_templates if t.get('is_popular')]),
            'new_count': len([t for t in all_templates if t.get('is_new')]),
        }
    
    @classmethod
    def search(cls, query: str, limit: int = 20) -> List[Dict]:
        """Búsqueda simple por nombre o slug."""
        query = query.lower().strip()
        if not query:
            return []
        
        results = []
        for template in cls.get_all():
            if (query in template.get('slug', '').lower() or 
                query in template.get('name', '').lower()):
                results.append(template)
                if len(results) >= limit:
                    break
        
        return results
    
    @classmethod
    def clear_cache(cls):
        """Limpia el caché de templates."""
        cache.delete(cls.CACHE_KEY)
    
    @classmethod
    def refresh(cls) -> int:
        """Fuerza recarga de templates y retorna el total."""
        cls.clear_cache()
        templates = cls.get_all()
        return len(templates)
    
    @classmethod
    def check_status(cls) -> Dict[str, Any]:
        """
        Verifica el estado del sistema de templates.
        Útil para debugging.
        
        Returns:
            Dict con información de diagnóstico
        """
        json_exists = os.path.exists(cls.get_json_path())
        csv_exists = os.path.exists(cls.get_csv_path())
        
        templates = cls.get_all()
        
        # Verificar si las imágenes son accesibles (solo la primera)
        sample_url = templates[0]['thumbnail_url'] if templates else None
        
        return {
            'json_path': cls.get_json_path(),
            'json_exists': json_exists,
            'csv_path': cls.get_csv_path(),
            'csv_exists': csv_exists,
            'base_url': cls.get_base_url(),
            'templates_count': len(templates),
            'sample_image_url': sample_url,
            'cache_key': cls.CACHE_KEY,
            'is_heroku': os.environ.get('DYNO') is not None,
            'debug_mode': settings.DEBUG,
        }
    
    # === MÉTODOS PRIVADOS ===
    
    @classmethod
    def _get_cached_templates(cls) -> List[Dict]:
        """Obtiene templates del caché o los carga."""
        cached = cache.get(cls.CACHE_KEY)
        if cached is not None:
            return cached
        
        templates = cls._load_templates()
        cache.set(cls.CACHE_KEY, templates, cls.CACHE_TIMEOUT)
        return templates
    
    @classmethod
    def _load_templates(cls) -> List[Dict]:
        """
        Carga templates desde archivo.
        Prioridad: JSON > CSV
        """
        # Intentar cargar desde JSON
        json_path = cls.get_json_path()
        if os.path.exists(json_path):
            return cls._load_from_json(json_path)
        
        # Fallback a CSV
        csv_path = cls.get_csv_path()
        if os.path.exists(csv_path):
            return cls._load_from_csv(csv_path)
        
        # No hay archivo - retornar lista vacía
        print(f"[TemplateLoader] WARNING: No se encontró archivo de templates")
        print(f"  - Buscado JSON en: {json_path}")
        print(f"  - Buscado CSV en: {csv_path}")
        return []
    
    @classmethod
    def _load_from_json(cls, filepath: str) -> List[Dict]:
        """Carga templates desde archivo JSON."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            
            base_url = cls.get_base_url()
            
            # Procesar cada template
            for t in templates:
                t.setdefault('category_slug', cls.DEFAULT_CATEGORY)
                t.setdefault('is_popular', False)
                t.setdefault('is_new', False)
                t.setdefault('order', 0)
                
                # Si las URLs no son absolutas, agregar base_url
                if not t.get('thumbnail_url', '').startswith(('http://', 'https://', '/')):
                    filename = t.get('thumbnail_url', '')
                    t['thumbnail_url'] = f"{base_url}{filename}"
                    t['preview_url'] = f"{base_url}{filename}"
                # Si empiezan con el placeholder, reemplazar con base_url real
                elif 'cdn.imprentagallito.com' in t.get('thumbnail_url', ''):
                    filename = t['thumbnail_url'].split('/')[-1]
                    t['thumbnail_url'] = f"{base_url}{filename}"
                    t['preview_url'] = f"{base_url}{filename}"
            
            print(f"[TemplateLoader] Cargados {len(templates)} templates desde JSON")
            return templates
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"[TemplateLoader] Error cargando JSON: {e}")
            return []
    
    @classmethod
    def _load_from_csv(cls, filepath: str) -> List[Dict]:
        """
        Carga templates desde CSV simple (solo nombres de imagen).
        Genera metadatos automáticamente.
        """
        templates = []
        base_url = cls.get_base_url()
        
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                total = len(rows)
                
                for i, row in enumerate(rows):
                    filename = row.get('tp_templates_img_url', '').strip()
                    if not filename:
                        continue
                    
                    code = filename.replace('.jpg', '').replace('.png', '').replace('.jpeg', '')
                    
                    templates.append({
                        'slug': code.lower(),
                        'name': f'Diseño {code}',
                        'thumbnail_url': f'{base_url}{filename}',
                        'preview_url': f'{base_url}{filename}',
                        'category_slug': cls.DEFAULT_CATEGORY,
                        'is_popular': i < cls.POPULAR_COUNT,
                        'is_new': i >= total - cls.NEW_COUNT,
                        'order': i,
                    })
            
            print(f"[TemplateLoader] Cargados {len(templates)} templates desde CSV")
            return templates
            
        except IOError as e:
            print(f"[TemplateLoader] Error cargando CSV: {e}")
            return []


# === FUNCIONES DE CONVENIENCIA ===

def get_templates_for_category(category_slug: str) -> List[Dict]:
    """Atajo para obtener templates de una categoría."""
    return TemplateLoader.get_all(category_slug)


def get_template(slug: str) -> Optional[Dict]:
    """Atajo para obtener un template por slug."""
    return TemplateLoader.get_by_slug(slug)
