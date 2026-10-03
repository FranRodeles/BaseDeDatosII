#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trabajo Práctico 2 - Diseño de Bases de Datos II
Análisis Exploratorio y Perfilado de Datos: questions_dataset.csv
Autor: Francisco Rodeles
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Configuración estética de gráficos
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 120

def cargar_y_limpiar_datos(filepath="questions_dataset.csv"):
    print("=" * 70)
    print("1. CARGA Y PERFILADO GENERAL DE DATOS")
    print("=" * 70)
    df = pd.read_csv(filepath)
    print(f"Dimensiones del dataset: {df.shape[0]} filas x {df.shape[1]} columnas")
    print(f"Columnas disponibles:\n  {list(df.columns)}")
    
    # Verificación de nulos
    nulos = df.isnull().sum()
    print("\nValores nulos por columna:")
    for col, cant in nulos.items():
        print(f"  - {col}: {cant} ({cant / len(df) * 100:.1f}%)")
        
    return df

def parsear_campos_json(df):
    print("\n" + "=" * 70)
    print("2. EXTRACCIÓN Y PARSEO DE ESTRUCTURAS JSON")
    print("=" * 70)
    
    # Función segura de parseo JSON
    def safe_json_len(val):
        try:
            parsed = json.loads(val)
            return len(parsed) if isinstance(parsed, list) else 0
        except Exception:
            return 0

    df['cant_examples'] = df['examples'].apply(safe_json_len)
    df['cant_constraints'] = df['constraints'].apply(safe_json_len)
    df['cant_test_cases'] = df['test_cases'].apply(safe_json_len)
    
    # Métricas de texto
    df['desc_char_len'] = df['description'].astype(str).str.len()
    df['desc_word_count'] = df['description'].astype(str).str.split().apply(len)
    df['title_char_len'] = df['title'].astype(str).str.len()
    
    # Fechas
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['updated_at'] = pd.to_datetime(df['updated_at'])
    df['fecha_creacion'] = df['created_at'].dt.date
    
    print("Métricas JSON agregadas:")
    print(f"  - Ejemplos: min={df['cant_examples'].min()}, max={df['cant_examples'].max()}, media={df['cant_examples'].mean():.2f}")
    print(f"  - Restricciones: min={df['cant_constraints'].min()}, max={df['cant_constraints'].max()}, media={df['cant_constraints'].mean():.2f}")
    print(f"  - Casos de prueba: min={df['cant_test_cases'].min()}, max={df['cant_test_cases'].max()}, media={df['cant_test_cases'].mean():.2f}")
    
    # Invariabilidad temporal
    mismas_fechas = (df['created_at'] == df['updated_at']).sum()
    print(f"\nInvariabilidad temporal:")
    print(f"  - Registros donde created_at == updated_at: {mismas_fechas} de {len(df)} ({mismas_fechas / len(df) * 100:.1f}%)")
    
    return df

def analizar_duplicados(df):
    print("\n" + "=" * 70)
    print("3. ANÁLISIS DE TÍTULOS Y DUPLICIDAD")
    print("=" * 70)
    
    titulos_duplicados = df[df.duplicated(subset=['title'], keep=False)].sort_values('title')
    titulos_unicos_repetidos = titulos_duplicados['title'].nunique()
    total_filas_repetidas = len(titulos_duplicados)
    
    print(f"Títulos únicos en el dataset: {df['title'].nunique()}")
    print(f"Títulos que se repiten: {titulos_unicos_repetidos} (afectando a {total_filas_repetidas} filas)")
    
    # Clasificar tipo de duplicidad
    dups_exactos = 0
    dups_mismo_titulo_distinta_desc = 0
    dups_cambio_dificultad = 0
    
    for titulo, grupo in titulos_duplicados.groupby('title'):
        first_row = grupo.iloc[0]
        descs_iguales = (grupo['description'] == first_row['description']).all()
        diffs_iguales = (grupo['difficulty_level'] == first_row['difficulty_level']).all()
        tc_iguales = (grupo['test_cases'] == first_row['test_cases']).all()
        
        if descs_iguales and diffs_iguales and tc_iguales:
            dups_exactos += 1
        elif not descs_iguales:
            dups_mismo_titulo_distinta_desc += 1
            
        if not diffs_iguales:
            dups_cambio_dificultad += 1
            
    print(f"  - Duplicados 100% idénticos (mismo enunciado y tests): {dups_exactos} grupos")
    print(f"  - Títulos idénticos pero problemas distintos: {dups_mismo_titulo_distinta_desc} grupos")
    print(f"  - Casos con cambio en nivel de dificultad: {dups_cambio_dificultad} grupos")
    
    return titulos_duplicados

def analizar_topicos(df):
    print("\n" + "=" * 70)
    print("4. ANÁLISIS DE TÓPICOS ALGORÍTMICOS")
    print("=" * 70)
    
    keywords = {
        "Arrays / Arreglos": ["array", "subarray", "vector"],
        "Árboles (Trees)": ["tree", "binary tree", "bst", "traversal"],
        "Grafos (Graphs)": ["graph", "edge", "cycle", "path"],
        "Cadenas (Strings)": ["string", "substring", "palindrome", "anagram"],
        "Búsqueda y Ordenamiento": ["sort", "search", "binary search"],
        "Listas Enlazadas": ["list", "linked list"],
        "Programación Dinámica / Sumas": ["dynamic programming", "dp", "sum", "coins"]
    }
    
    conteos_topicos = {}
    textos = (df['title'] + " " + df['description']).str.lower()
    
    for topico, kw_list in keywords.items():
        pattern = "|".join(kw_list)
        count = textos.str.contains(pattern, regex=True).sum()
        conteos_topicos[topico] = count
        print(f"  - {topico}: {count} problemas ({count / len(df) * 100:.1f}%)")
        
    return pd.Series(conteos_topicos)

def generar_graficos(df, conteos_topicos, output_dir="graficos"):
    print("\n" + "=" * 70)
    print("5. GENERACIÓN DE VISUALIZACIONES")
    print("=" * 70)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Distribución de Dificultad
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    diff_order = ['Easy', 'Medium', 'Hard']
    diff_counts = df['difficulty_level'].value_counts().reindex(diff_order)
    colores = ['#4caf50', '#ff9800', '#f44336']
    
    ax1.bar(diff_order, diff_counts, color=colores, edgecolor='black', alpha=0.85)
    ax1.set_title('Cantidad de Problemas por Nivel de Dificultad', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Nivel de Dificultad')
    ax1.set_ylabel('Frecuencia')
    for i, v in enumerate(diff_counts):
        ax1.text(i, v + 4, f"{v} ({v/len(df)*100:.1f}%)", ha='center', fontweight='bold')
        
    ax2.pie(diff_counts, labels=diff_order, colors=colores, autopct='%1.1f%%', startangle=140,
            explode=(0.04, 0.04, 0.04), wedgeprops={'edgecolor': 'black'})
    ax2.set_title('Proporción de Dificultad', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "1_distribucion_dificultad.png"), bbox_inches='tight')
    plt.close()
    print(f"  [OK] Gráfico 1 guardado en: {output_dir}/1_distribucion_dificultad.png")
    
    # 2. Distribución Temporal de Creación
    fig, ax = plt.subplots(figsize=(8, 4.5))
    fechas_count = df['fecha_creacion'].value_counts().sort_index()
    fechas_str = [d.strftime('%Y-%m-%d') for d in fechas_count.index]
    bars = ax.bar(fechas_str, fechas_count.values, color='#3f51b5', edgecolor='black', width=0.45)
    ax.set_title('Lotes de Creación de Registros (created_at)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Fecha de Inserción')
    ax.set_ylabel('Cantidad de Problemas')
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 7, f"{h} ({h/len(df)*100:.1f}%)", ha='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "2_distribucion_temporal.png"), bbox_inches='tight')
    plt.close()
    print(f"  [OK] Gráfico 2 guardado en: {output_dir}/2_distribucion_temporal.png")
    
    # 3. Longitud de Descripciones por Dificultad
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=df, x='difficulty_level', y='desc_word_count', order=diff_order, hue='difficulty_level', palette=colores, legend=False, ax=ax)
    ax.set_title('Longitud de Enunciados (en palabras) según Dificultad', fontsize=12, fontweight='bold')
    ax.set_xlabel('Nivel de Dificultad')
    ax.set_ylabel('Cantidad de Palabras en la Descripción')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "3_longitud_descripcion_boxplot.png"), bbox_inches='tight')
    plt.close()
    print(f"  [OK] Gráfico 3 guardado en: {output_dir}/3_longitud_descripcion_boxplot.png")
    
    # 4. Distribución de Campos JSON (Restricciones y Casos de Prueba)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    sns.countplot(data=df, x='cant_constraints', hue='cant_constraints', palette='Blues_d', legend=False, ax=ax1)
    ax1.set_title('Distribución de Restricciones por Pregunta', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Cantidad de Restricciones')
    ax1.set_ylabel('Frecuencia')
    
    # Casos de prueba (identificando el atípico de 32)
    sns.histplot(df['cant_test_cases'], bins=30, color='#e91e63', kde=False, ax=ax2)
    ax2.set_title('Distribución de Casos de Prueba (Notar Atípico de 32)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Cantidad de Casos de Prueba')
    ax2.set_ylabel('Frecuencia')
    ax2.annotate('ID 122 con 32 tests', xy=(32, 1), xytext=(22, 50),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
                 fontweight='bold', color='#c2185b')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "4_distribucion_json_restricciones_tests.png"), bbox_inches='tight')
    plt.close()
    print(f"  [OK] Gráfico 4 guardado en: {output_dir}/4_distribucion_json_restricciones_tests.png")
    
    # 5. Frecuencia de Tópicos Algorítmicos
    fig, ax = plt.subplots(figsize=(10, 5))
    topicos_sorted = conteos_topicos.sort_values(ascending=True)
    ax.barh(topicos_sorted.index, topicos_sorted.values, color='#009688', edgecolor='black')
    ax.set_title('Temáticas Algorítmicas más Frecuentes', fontsize=12, fontweight='bold')
    ax.set_xlabel('Cantidad de Problemas que lo Contienen')
    for i, v in enumerate(topicos_sorted.values):
        ax.text(v + 3, i, f"{v} ({v/len(df)*100:.1f}%)", va='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "5_topicos_frecuentes.png"), bbox_inches='tight')
    plt.close()
    print(f"  [OK] Gráfico 5 guardado en: {output_dir}/5_topicos_frecuentes.png")

def imprimir_conclusiones():
    print("\n" + "=" * 70)
    print("6. CONCLUSIONES PRINCIPALES PARA EL INFORME DE BASE DE DATOS")
    print("=" * 70)
    conclusiones = """
1. INTEGRIDAD DE ATRIBUTOS (COMPLETITUD AL 100%):
   - El dataset no posee ningún valor nulo (0 NaN) en sus 9 atributos y 616 registros.
   - La clave 'id' es estrictamente consecutiva (1 a 616) y única.

2. ESTRUCTURA HÍBRIDA (RELACIONAL VS. DOCUMENTAL):
   - Los campos 'examples', 'constraints' y 'test_cases' almacenan estructuras JSON anidadas.
   - En un modelo relacional (OLTP/DW), estas columnas violan la Primera Forma Normal (1FN).
     Se recomienda desacoplarlas en tablas subordinadas (ej: Question_Examples, Question_Constraints,
     Question_TestCases) conectadas por foreign key (question_id).

3. ANOMALÍA EN TÍTULOS Y COLISIÓN DE NOMBRES:
   - Existen 55 títulos que se repiten en 110 registros.
   - Hallazgo crítico: En 47 de esos 55 casos, los enunciados son COMPLETAMENTE DISTINTOS.
     El título no es un identificador semántico fiable y no debe definirse como restricción UNIQUE.
   - En 3 casos son duplicados exactos en contenido (redundancia de datos).
   - En 2 casos se modificó la dificultad asignada manteniendo el mismo nombre.

4. INVARIABILIDAD Y AUDITORÍA TEMPORAL:
   - El 100% de los registros mantiene created_at == updated_at.
   - No se registran modificaciones históricas. Toda la carga se realizó en solo 2 lotes (16 y 18 de marzo 2025).

5. VALORES ATÍPICOS (OUTLIERS):
   - La moda de test_cases es 5 (87.8% de los registros), pero el ID 122 ('Sum of Powers of Primes')
     presenta 32 casos de prueba, constituyendo un outlier extremo en volumen de verificación.
"""
    print(conclusiones)
    print("=" * 70)

if __name__ == "__main__":
    df = cargar_y_limpiar_datos()
    df = parsear_campos_json(df)
    analizar_duplicados(df)
    conteos_topicos = analizar_topicos(df)
    generar_graficos(df, conteos_topicos)
    imprimir_conclusiones()
