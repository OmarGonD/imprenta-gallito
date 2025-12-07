#!/usr/bin/env python3
"""
Script para corregir el error de sintaxis en import_catalog.py línea 539
Agrega la coma faltante automáticamente

Ejecutar desde la raíz del proyecto Django:
    python fix_import_syntax.py
"""

import shutil
from pathlib import Path

# Ruta al archivo
FILEPATH = Path("shop/management/commands/import_catalog.py")

def main():
    print("=" * 80)
    print("CORRECCIÓN DE SINTAXIS: import_catalog.py línea 539")
    print("=" * 80)
    print()
    
    if not FILEPATH.exists():
        print(f"❌ Error: No se encuentra {FILEPATH}")
        print("   Asegúrate de ejecutar este script desde la raíz del proyecto Django")
        return
    
    # Backup
    backup = FILEPATH.with_suffix(".py.backup_syntax")
    print(f"💾 Creando backup: {backup}")
    shutil.copy2(FILEPATH, backup)
    print("✅ Backup creado\n")
    
    # Leer archivo
    print(f"📖 Leyendo {FILEPATH}")
    with open(FILEPATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"   Total líneas: {len(lines)}\n")
    
    # Verificar línea 539
    LINE_NUM = 539
    line_idx = LINE_NUM - 1  # Índice 0-based
    
    if line_idx >= len(lines):
        print(f"❌ Error: El archivo solo tiene {len(lines)} líneas")
        return
    
    original_line = lines[line_idx]
    print(f"Línea {LINE_NUM} original:")
    print(f"  {original_line.rstrip()}")
    print()
    
    # Verificar si necesita corrección
    if original_line.rstrip().endswith(','):
        print("✅ La línea ya tiene coma al final, no necesita corrección")
        return
    
    if not original_line.rstrip().endswith(')'):
        print("⚠️ La línea no termina con paréntesis, verificar manualmente")
        return
    
    # Agregar coma
    print("🔧 Agregando coma al final...")
    corrected_line = original_line.rstrip() + ',\n'
    lines[line_idx] = corrected_line
    
    print(f"Línea {LINE_NUM} corregida:")
    print(f"  {corrected_line.rstrip()}")
    print()
    
    # Guardar archivo corregido
    print(f"💾 Guardando {FILEPATH}")
    with open(FILEPATH, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Archivo guardado\n")
    
    # Verificar sintaxis Python
    print("🧪 Verificando sintaxis Python...")
    import py_compile
    try:
        py_compile.compile(str(FILEPATH), doraise=True)
        print("✅ Sintaxis correcta\n")
    except py_compile.PyCompileError as e:
        print(f"❌ Aún hay errores de sintaxis:")
        print(f"   {e}")
        print("\n⚠️ Revisar manualmente el archivo")
        return
    
    # Resumen
    print("=" * 80)
    print("✅ CORRECCIÓN COMPLETADA")
    print("=" * 80)
    print()
    print("Ahora puedes ejecutar:")
    print("  python manage.py import_catalog --force")
    print()
    print(f"Backup disponible en: {backup}")
    print()


if __name__ == '__main__':
    main()
