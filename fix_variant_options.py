#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPARACIÓN MASIVA AUTOMÁTICA - VERSIÓN CORREGIDA
Detecta automáticamente el delimitador como lo hace import_catalog.py
Arregla TODOS los CSV que necesita: python manage.py import_catalog

Ejecutar desde la raíz del proyecto:
    python fix_all_catalog_csv.py
"""

import csv
import shutil
from pathlib import Path

# RUTA DONDE ESTÁN TUS CSV
DATA_DIR = Path("static") / "data"

# Todos los archivos que usa import_catalog
ARCHIVOS_A_REPARAR = [
    "categories_complete.csv",
    "subcategories_complete.csv",
    "products_complete.csv",
    "price_tiers_complete.csv",
    "variant_types_complete.csv",
    "variant_options_complete.csv",
    "product_variant_types_complete.csv",
    "polos_colors.csv",
    "polos_images.csv",
    "design_templates.csv",
]


def detect_delimiter(filepath: Path):
    """
    Detecta el delimitador del CSV.
    COPIA EXACTA de import_catalog.py líneas 131-142
    """
    with open(filepath, 'r', encoding='latin-1') as f:
        sample = f.read(4096)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
            return dialect.delimiter
        except csv.Error:
            # Si hay más ; que , probablemente sea ;
            if sample.count(';') > sample.count(','):
                return ';'
            return ','


def reparar_csv(archivo_path: Path):
    """Repara un archivo CSV detectando automáticamente su delimitador"""
    
    if not archivo_path.exists():
        print(f"   [SKIP] No existe → {archivo_path.name}")
        return False

    print(f"\nProcesando → {archivo_path.name}")

    # Detectar delimitador (IGUAL que import_catalog.py)
    delimiter = detect_delimiter(archivo_path)
    print(f"   Delimitador detectado: '{delimiter}' (ord {ord(delimiter)})")

    # Backup
    backup = archivo_path.with_suffix(".csv.backup")
    shutil.copy2(archivo_path, backup)
    print(f"   Backup creado → {backup.name}")

    fixed_rows = []
    lineas_reparadas = 0
    total_lineas = 0

    try:
        with open(archivo_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f, delimiter=delimiter)  # ← USAR DELIMITADOR DETECTADO
            
            try:
                header = next(reader)
                fixed_rows.append(header)
                expected_cols = len(header)
                print(f"   Columnas esperadas: {expected_cols}")
                print(f"   Header: {delimiter.join(header[:5])}{'...' if len(header)>5 else ''}")
            except StopIteration:
                print("   ⚠️ Archivo vacío")
                return False

            for line_num, row in enumerate(reader, start=2):
                total_lineas += 1
                
                # Si la fila tiene la cantidad correcta de columnas, está bien
                if len(row) == expected_cols:
                    fixed_rows.append(row)
                    continue

                # Línea problemática
                lineas_reparadas += 1
                print(f"   ⚠️ Línea {line_num}: {len(row)} columnas (esperado {expected_cols})")
                print(f"      Primeros campos: {row[:3] if len(row) >= 3 else row}")

                if len(row) > expected_cols:
                    # Hay campos extra - probablemente hay comas/delimitadores sin escapar
                    
                    # Estrategia inteligente según el tipo de columna
                    description_fields = ['description', 'desc', 'descripcion', 'texto']
                    name_fields = ['name', 'nombre', 'title', 'titulo']
                    
                    # Buscar columna de descripción
                    desc_idx = None
                    for i, h in enumerate(header):
                        if any(field in h.lower() for field in description_fields):
                            desc_idx = i
                            break
                    
                    if desc_idx is not None:
                        # Fusionar campos alrededor de la descripción
                        before = row[:desc_idx]
                        
                        # Calcular cuántos campos vienen después
                        after_count = expected_cols - desc_idx - 1
                        after = row[-after_count:] if after_count > 0 else []
                        
                        # Fusionar el medio (descripción)
                        middle_start = desc_idx
                        middle_end = len(row) - after_count if after_count > 0 else len(row)
                        description_parts = row[middle_start:middle_end]
                        
                        # Unir con el delimitador + espacio
                        description = f"{delimiter} ".join(part.strip() for part in description_parts if part.strip())
                        
                        fixed_row = before + [description] + after
                        print(f"      ✅ Fusionada descripción: {len(description_parts)} campos → 1")
                    else:
                        # Estrategia genérica: asumir que los campos del medio son el problema
                        # Mantener los primeros 2 y los últimos 3
                        fixed_row = row[:2]
                        middle = f"{delimiter} ".join(row[2:len(row)-3])
                        fixed_row.append(middle)
                        fixed_row.extend(row[-3:])
                        print(f"      ⚠️ Reparación genérica aplicada")
                    
                    # Asegurar longitud exacta
                    if len(fixed_row) > expected_cols:
                        fixed_row = fixed_row[:expected_cols]
                    elif len(fixed_row) < expected_cols:
                        fixed_row.extend([''] * (expected_cols - len(fixed_row)))
                    
                    fixed_rows.append(fixed_row)
                    
                else:
                    # Faltan campos - rellenar con vacíos
                    print(f"      ⚠️ Faltan {expected_cols - len(row)} campos, rellenando con vacíos")
                    row.extend([''] * (expected_cols - len(row)))
                    fixed_rows.append(row)

    except UnicodeDecodeError:
        # Si falla UTF-8, intentar con latin-1
        print("   ⚠️ Error UTF-8, reintentando con latin-1...")
        
        with open(archivo_path, 'r', encoding='latin-1', newline='') as f:
            reader = csv.reader(f, delimiter=delimiter)
            header = next(reader)
            fixed_rows = [header]
            expected_cols = len(header)
            
            for line_num, row in enumerate(reader, start=2):
                if len(row) == expected_cols:
                    fixed_rows.append(row)
                else:
                    lineas_reparadas += 1
                    # Aplicar misma lógica de reparación
                    if len(row) > expected_cols:
                        fixed_row = row[:2] + [f"{delimiter} ".join(row[2:-3])] + row[-3:]
                    else:
                        fixed_row = row + [''] * (expected_cols - len(row))
                    fixed_rows.append(fixed_row[:expected_cols])

    # Guardar versión reparada con el MISMO delimitador
    reparado = archivo_path.with_name(archivo_path.stem + "_repaired.csv")
    with open(reparado, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
        writer.writerows(fixed_rows)

    print(f"   Líneas reparadas: {lineas_reparadas} de {total_lineas}")
    print(f"   Guardado → {reparado.name}")

    return lineas_reparadas > 0


def verificar_con_pandas(archivo_path: Path):
    """Verifica que el archivo se pueda leer con pandas (como lo hace import_catalog)"""
    try:
        import pandas as pd
        delimiter = detect_delimiter(archivo_path)
        df = pd.read_csv(archivo_path, encoding='utf-8', delimiter=delimiter)
        return True, len(df), None
    except Exception as e:
        return False, 0, str(e)


def main():
    print("\n" + "═" * 90)
    print(" REPARACIÓN MASIVA DE TODOS LOS CSV DEL CATÁLOGO")
    print(" Versión CORREGIDA - Detecta delimitador automáticamente")
    print(" Para: python manage.py import_catalog")
    print("═" * 90 + "\n")

    if not DATA_DIR.exists():
        print(f"❌ Error: No existe la carpeta → {DATA_DIR}")
        print("   Asegúrate de ejecutar este script desde la raíz del proyecto Django")
        return

    # Verificar que pandas esté disponible
    try:
        import pandas as pd
        print("✅ Pandas disponible para verificación\n")
    except ImportError:
        print("⚠️ Pandas no disponible, solo se hará reparación básica\n")
        pd = None

    reparados = []
    con_errores = []
    
    for nombre in ARCHIVOS_A_REPARAR:
        archivo = DATA_DIR / nombre
        
        if not archivo.exists():
            print(f"\n⊘ Archivo opcional no encontrado: {nombre}")
            continue
        
        # Reparar
        tuvo_problemas = reparar_csv(archivo)
        if tuvo_problemas:
            reparados.append(nombre)
        
        # Verificar con pandas (después de reparar)
        if pd is not None:
            archivo_a_verificar = archivo.with_name(archivo.stem + "_repaired.csv") if tuvo_problemas else archivo
            ok, filas, error = verificar_con_pandas(archivo_a_verificar)
            
            if ok:
                print(f"   ✅ Verificado con pandas: {filas} filas")
            else:
                print(f"   ❌ Error en pandas: {error}")
                con_errores.append((nombre, error))

    # Resumen
    print("\n" + "═" * 90)
    print(" RESUMEN FINAL")
    print("═" * 90)
    
    if con_errores:
        print(f"\n❌ ARCHIVOS CON ERRORES EN PANDAS:")
        for nombre, error in con_errores:
            print(f"   • {nombre}")
            print(f"     Error: {error[:100]}...")
        print("\n⚠️ Estos archivos NECESITAN atención manual")
    
    if reparados:
        print(f"\n📝 Archivos reparados: {len(reparados)}")
        for arch in reparados:
            print(f"   • {arch}")
        
        print("\n¿Deseas reemplazar TODOS los originales con las versiones reparadas?")
        resp = input("\nEscribe 'SI' para reemplazar todo automáticamente: ").strip().upper()
        
        if resp == "SI":
            for nombre in reparados:
                original = DATA_DIR / nombre
                reparado = original.with_name(original.stem + "_repaired.csv")
                shutil.copy2(reparado, original)
                print(f"   ✓ Reemplazado → {nombre}")
            
            print("\n✅ ¡TODOS LOS ARCHIVOS HAN SIDO REPARADOS Y ACTUALIZADOS!")
            print("\n   Ahora puedes ejecutar con total seguridad:")
            print("       python manage.py import_catalog --force")
        else:
            print("\n⊘ No se reemplazó nada. Puedes hacerlo manualmente o volver a ejecutar.")
    else:
        if not con_errores:
            print("\n✅ ¡FELICIDADES! Todos los archivos están PERFECTOS.")
            print("   No se necesitó reparar nada.")
        else:
            print("\n⚠️ No se detectaron problemas estructurales,")
            print("   pero pandas reportó errores. Revisar manualmente.")

    print("\n" + "═" * 90 + "\n")


if __name__ == '__main__':
    main()