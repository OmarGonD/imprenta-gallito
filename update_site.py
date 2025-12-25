import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imprenta_gallito.settings')
django.setup()

from django.contrib.sites.models import Site

def update_site_domain():
    try:
        # Get the default site (usually ID 1)
        site = Site.objects.get(pk=1)
        
        # Update domain and name
        old_domain = site.domain
        site.domain = 'imprentagallito.com'
        site.name = 'Imprenta Gallito'
        site.save()
        
        print(f"✅ Éxito: Sitio actualizado de '{old_domain}' a '{site.domain}'")
        print("Ahora los correos usarán este dominio en los enlaces.")
        
    except Site.DoesNotExist:
        print("❌ Error: No se encontró el Site con ID 1.")
    except Exception as e:
        print(f"❌ Error al actualizar: {e}")

if __name__ == '__main__':
    update_site_domain()
