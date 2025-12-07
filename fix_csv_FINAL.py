#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIMPIEZA CSV - VERSIÓN ULTRA SIMPLE Y ROBUSTA
"""

import pandas as pd
import shutil
from pathlib import Path

# CONFIGURACIÓN
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

print("\n" + "="*70)
print("LIMPIEZA DE CSV")
print("="*70)
print(f"Directorio: {DATA_DIR}\n")

if not DATA_DIR.exists():
    print(f"❌ No existe: {DATA_DIR}\n")
    exit(1)

exitosos = 0
errores = 0

for nombre in ARCHIVOS:
    archivo = DATA_DIR / nombre
    
    if not archivo.exists():
        print(f"⊘ No existe: {nombre}")
        errores += 1
        continue
    
    print(f"\n{'='*70}")
    print(f"Procesando: {nombre}")
    print('='*70)
    
    try:
        # BACKUP
        backup = archivo.with_suffix(".csv.backup")
        shutil.copy2(archivo, backup)
        print(f"💾 Backup: {backup.name}")
        
        # LEER - Probar diferentes encodings y delimitadores
        df = None
        
        # Intentar UTF-8 con diferentes delimitadores
        for delim in [';', ',', '\t', '|']:
            try:
                df = pd.read_csv(archivo, encoding='utf-8', delimiter=delim, on_bad_lines='skip')
                if len(df.columns) > 1:  # Si tiene más de 1 columna, funcionó
                    print(f"✅ Leído con UTF-8, delimitador '{delim}'")
                    break
            except:
                pass
        
        # Si falló, intentar latin1
        if df is None or len(df.columns) == 1:
            for delim in [';', ',', '\t', '|']:
                try:
                    df = pd.read_csv(archivo, encoding='latin1', delimiter=delim, on_bad_lines='skip')
                    if len(df.columns) > 1:
                        print(f"✅ Leído con latin1, delimitador '{delim}'")
                        break
                except:
                    pass
        
        # Si aún falló, intentar sin especificar encoding
        if df is None or len(df.columns) == 1:
            for delim in [';', ',', '\t', '|']:
                try:
                    df = pd.read_csv(archivo, delimiter=delim, on_bad_lines='skip', encoding_errors='ignore')
                    if len(df.columns) > 1:
                        print(f"✅ Leído con encoding automático, delimitador '{delim}'")
                        break
                except:
                    pass
        
        if df is None or len(df.columns) == 1:
            print(f"❌ No se pudo leer el archivo correctamente")
            errores += 1
            continue
        
        print(f"📊 {len(df)} filas, {len(df.columns)} columnas")
        
        # LIMPIAR NOMBRES DE COLUMNAS
        # Eliminar BOM, comillas, espacios
        df.columns = [
            col.replace('\ufeff', '')
               .replace('ï»¿', '')
               .strip('"')
               .strip("'")
               .strip()
            for col in df.columns
        ]
        
        print(f"📋 Columnas:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i}. {col}")
        
        # RELLENAR NA
        na_count = 0
        for col in df.columns:
            if df[col].isna().any():
                n = df[col].isna().sum()
                na_count += n
                
                if 'display_order' in col.lower() or 'quantity' in col.lower():
                    df[col].fillna(0, inplace=True)
                elif 'price' in col.lower():
                    df[col].fillna(0.0, inplace=True)
                elif df[col].dtype == 'object':
                    df[col].fillna('', inplace=True)
                else:
                    df[col].fillna(0, inplace=True)
        
        if na_count > 0:
            print(f"⚠️  Rellenados {na_count} valores NA")
        
        # GUARDAR (sobrescribe original)
        df.to_csv(archivo, index=False, encoding='utf-8', sep=',')
        print(f"✅ GUARDADO: {nombre}")
        
        exitosos += 1
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        errores += 1

# RESUMEN
print(f"\n{'='*70}")
print("RESUMEN")
print('='*70)
print(f"✅ Exitosos: {exitosos}")
print(f"❌ Errores: {errores}")

if exitosos > 0:
    print(f"\n📁 Archivos en: {DATA_DIR}")
    print("💾 Backups: *.backup")
    print("\nEjecutar: python manage.py import_catalog --force")

print()
