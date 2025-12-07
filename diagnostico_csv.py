#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIAGNÓSTICO: Ver columnas reales de cada CSV
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(r"D:\web_proyects\imprenta_gallito\static\data")

ARCHIVOS = [
    'categories_complete.csv',
    'subcategories_complete.csv',
    'products_complete.csv',
    'price_tiers_complete.csv',
    'variant_types_complete.csv',
    'variant_options_complete.csv',
    'product_variant_types_complete.csv',
    'polos_colors.csv',
    'polos_images.csv',
    'design_templates.csv',
]

print("\n" + "="*80)
print("DIAGNÓSTICO DE ARCHIVOS CSV")
print("="*80)
print(f"Directorio: {DATA_DIR}\n")

for nombre in ARCHIVOS:
    archivo = DATA_DIR / nombre
    
    if not archivo.exists():
        print(f"\n❌ NO EXISTE: {nombre}")
        continue
    
    print(f"\n{'='*80}")
    print(f"Archivo: {nombre}")
    print('='*80)
    
    # Ver contenido RAW de las primeras líneas
    print("\n📄 PRIMERA LÍNEA (RAW):")
    with open(archivo, 'rb') as f:
        primera_linea_bytes = f.readline()
        print(f"   Bytes: {primera_linea_bytes[:100]}")
    
    with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
        primera_linea = f.readline().strip()
        print(f"   Texto: {primera_linea[:150]}")
    
    # Intentar leer con pandas
    print("\n📊 INTENTANDO LEER CON PANDAS:")
    
    success = False
    for encoding in ['utf-8', 'latin1', 'cp1252']:
        for delim in [',', ';', '\t', '|']:
            try:
                df = pd.read_csv(archivo, encoding=encoding, delimiter=delim, nrows=1)
                if len(df.columns) > 1:
                    print(f"\n✅ ÉXITO con encoding={encoding}, delimiter='{delim}'")
                    print(f"\n📋 COLUMNAS ({len(df.columns)}):")
                    for i, col in enumerate(df.columns, 1):
                        # Mostrar representación exacta
                        col_repr = repr(col)
                        print(f"   {i:2d}. {col_repr}")
                    
                    print(f"\n📊 FILAS: {len(df)}")
                    print(f"\n🔍 PRIMERA FILA:")
                    print(df.iloc[0].to_dict())
                    
                    success = True
                    break
            except Exception as e:
                continue
        
        if success:
            break
    
    if not success:
        print("\n❌ NO SE PUDO LEER EL ARCHIVO")
        print("\n🔍 Intentando leer las primeras 5 líneas como texto:")
        try:
            with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f):
                    if i >= 5:
                        break
                    print(f"   Línea {i+1}: {line.strip()[:100]}")
        except:
            print("   ❌ Error al leer como texto")

print("\n" + "="*80)
print("FIN DEL DIAGNÓSTICO")
print("="*80 + "\n")
