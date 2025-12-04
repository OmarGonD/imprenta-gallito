#!/usr/bin/env python
"""
Script para REPARAR AUTOMÁTICAMENTE todas las referencias a 'id' en shop/views.py
Cambia .id por .pk y id= por pk= (excepto cart_id, product_id, etc.)
"""

import re
import sys

def fix_views_file():
    """Lee shop/views.py, repara las referencias a id, y guarda el resultado"""
    
    try:
        # Leer el archivo
        with open('shop/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("📖 Archivo leído: shop/views.py")
        print("🔧 Aplicando correcciones...\n")
        
        changes = 0
        
        # 1. Cambiar .id por .pk (pero NO cart_id, product_id, color_id, etc.)
        pattern1 = r'(?<!cart_)(?<!product_)(?<!color_)(?<!size_)(?<!category_)(?<!subcategory_)\.id(?![a-z_])'
        matches1 = re.findall(pattern1, content)
        if matches1:
            content = re.sub(pattern1, '.pk', content)
            changes += len(matches1)
            print(f"✅ Cambiados {len(matches1)} casos de .id → .pk")
        
        # 2. Cambiar id= por pk= en exclude()
        pattern2 = r'\.exclude\(\s*id='
        matches2 = re.findall(pattern2, content)
        if matches2:
            content = re.sub(pattern2, '.exclude(\n    pk=', content)
            changes += len(matches2)
            print(f"✅ Cambiados {len(matches2)} casos de exclude(id= → exclude(pk=")
        
        # 3. Cambiar id= por pk= en filter()
        pattern3 = r'\.filter\(([^)]*\s)id='
        matches3 = re.findall(pattern3, content)
        if matches3:
            content = re.sub(r'\.filter\(([^)]*\s)id=', r'.filter(\1pk=', content)
            changes += len(matches3)
            print(f"✅ Cambiados {len(matches3)} casos de filter(id= → filter(pk=")
        
        # 4. Cambiar id= por pk= en get()
        pattern4 = r'\.get\(id='
        matches4 = re.findall(pattern4, content)
        if matches4:
            content = re.sub(pattern4, '.get(pk=', content)
            changes += len(matches4)
            print(f"✅ Cambiados {len(matches4)} casos de get(id= → get(pk=")
        
        # 5. Casos especiales comunes
        content = content.replace('id=product.id', 'pk=product.pk')
        content = content.replace('id=cart.id', 'pk=cart.pk')
        content = content.replace('cart.id,', 'cart.pk,')
        content = content.replace('product.id)', 'product.pk)')
        
        if changes == 0:
            print("⚠️  No se encontraron cambios necesarios.")
            print("    Es posible que el archivo ya esté corregido,")
            print("    o que el error esté en otro lugar.")
            return False
        
        # Hacer backup
        with open('shop/views.py.backup', 'w', encoding='utf-8') as f:
            with open('shop/views.py', 'r', encoding='utf-8') as original:
                f.write(original.read())
        print("\n💾 Backup creado: shop/views.py.backup")
        
        # Guardar el archivo corregido
        with open('shop/views.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ ARCHIVO REPARADO con {changes} cambios")
        print("🔄 Por favor reinicia el servidor: python manage.py runserver")
        
        return True
        
    except FileNotFoundError:
        print("❌ ERROR: No se encontró shop/views.py")
        print("   Asegúrate de ejecutar este script desde la raíz del proyecto")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    print("="*80)
    print("  SCRIPT DE REPARACIÓN AUTOMÁTICA - shop/views.py")
    print("  Cambia .id → .pk y id= → pk=")
    print("="*80)
    print()
    
    success = fix_views_file()
    
    if success:
        print("\n" + "="*80)
        print("  ✅ ÉXITO - Archivo reparado")
        print("="*80)
        sys.exit(0)
    else:
        print("\n" + "="*80)
        print("  ⚠️  VERIFICA MANUALMENTE")
        print("="*80)
        sys.exit(1)
