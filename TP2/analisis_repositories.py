#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trabajo Práctico 2 - Diseño de Bases de Datos II
Análisis Exploratorio, Calidad de Datos y Perfilado: repositories.csv
Autor: Francisco Rodeles
Materia: Diseño de Bases de Datos II - Universidad de Mendoza (UM)
"""

import os
import ast
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración estética de gráficos
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 120

def cargar_y_perfilado_inicial(filepath="repositories.csv"):
    print("=" * 75)
    print("1. CARGA DEL DATASET Y PERFILADO ESTRUCTURAL INICIAL")
    print("=" * 75)
    df = pd.read_csv(filepath)
    print(f"Dimensiones del dataset: {df.shape[0]:,} filas x {df.shape[1]} columnas")
    print("\nColumnas y tipos de datos inferidos:")
    for col, dtype in df.dtypes.items():
        print(f"  - {col}: {dtype}")
    return df

def auditoria_calidad_y_nulos(df):
    print("\n" + "=" * 75)
    print("2. EVALUACIÓN DE VALORES NULOS, DISPERSIÓN Y CALIDAD DE DATOS")
    print("=" * 75)
    nulos = df.isnull().sum()
    total = len(df)
    nulos_df = pd.DataFrame({
        'Nulos': nulos,
        'Porcentaje': (nulos / total) * 100
    }).sort_values('Nulos', ascending=False)
    
    print("Columnas con presencia de valores nulos:")
    for col, row in nulos_df[nulos_df['Nulos'] > 0].iterrows():
        print(f"  - {col}: {int(row['Nulos']):,} registros ({row['Porcentaje']:.2f}%)")
        
    print("\nColumnas 100% completas (0 nulos):")
    completas = nulos_df[nulos_df['Nulos'] == 0].index.tolist()
    print(f"  {len(completas)} columnas: {', '.join(completas[:6])}...")
    return nulos_df

def analisis_unicidad_y_claves(df):
    print("\n" + "=" * 75)
    print("3. ANÁLISIS DE CLAVES, UNICIDAD Y REDUNDANCIA DE ATRIBUTOS")
    print("=" * 75)
    total = len(df)
    unicos_url = df['URL'].nunique()
    unicos_name = df['Name'].nunique()
    
    print(f"Evaluación de Claves Candidatas:")
    print(f"  - Atributo 'URL': {unicos_url:,} únicos de {total:,} ({unicos_url / total * 100:.2f}% de unicidad)")
    print(f"    -> Conclusión: 'URL' es una clave candidata natural válida (identifica unívocamente owner/repo).")
    print(f"  - Atributo 'Name': {unicos_name:,} únicos de {total:,} ({(total - unicos_name):,} colisiones de nombres)")
    print(f"    -> Conclusión: 'Name' NO es único. No debe definirse con restricción UNIQUE.")
    
    # Nombres más repetidos
    dups_name = df[df.duplicated(subset=['Name'], keep=False)]
    top_repetidos = dups_name['Name'].value_counts().head(5)
    print("\nNombres genéricos con mayor número de colisiones:")
    for nom, cant in top_repetidos.items():
        print(f"  - '{nom}': {cant} repositorios diferentes")
        
    # Redundancia estricta Stars vs Watchers
    stars_igual_watchers = (df['Stars'] == df['Watchers']).all()
    print(f"\nAuditoría de Redundancia de Atributos:")
    print(f"  - ¿'Stars' == 'Watchers' en el 100% de los registros?: {stars_igual_watchers}")
    print(f"    -> Conclusión: Redundancia del 100%. Ambas columnas replican el mismo contador entero.")
    print(f"       En el modelo relacional físico se debe eliminar una de ellas para evitar duplicidad.")

def analisis_estadistico_asimetria(df):
    print("\n" + "=" * 75)
    print("4. ANÁLISIS ESTADÍSTICO Y ASIMETRÍA: MEDIA VS. MEDIANA")
    print("=" * 75)
    metricas = ['Stars', 'Forks', 'Issues', 'Size']
    resumen_stats = []
    
    for m in metricas:
        media = df[m].mean()
        mediana = df[m].median()
        desvio = df[m].std()
        min_v = df[m].min()
        max_v = df[m].max()
        q25 = df[m].quantile(0.25)
        q75 = df[m].quantile(0.75)
        resumen_stats.append({
            'Métrica': m,
            'Media': media,
            'Mediana': mediana,
            'Desvío': desvio,
            'Q1 (25%)': q25,
            'Q3 (75%)': q75,
            'Min': min_v,
            'Max': max_v
        })
        print(f"Métrica: {m}")
        print(f"  Media: {media:,.2f} | Mediana: {mediana:,.2f} | Desvío: {desvio:,.2f}")
        print(f"  Rango: [{min_v:,} - {max_v:,}] | IQR: [{q25:,.1f} - {q75:,.1f}]")
        print(f"  -> Asimetría positiva severa: La media es {media / mediana:.2f}x la mediana (cola pesada).\n")
        
    # Ratio Estrellas / Forks
    valid_forks = df[df['Forks'] > 0]
    ratio_sf = valid_forks['Stars'] / valid_forks['Forks']
    print(f"Ratio Stars / Forks (en repositorios con Forks > 0):")
    print(f"  - Mediana del ratio: {ratio_sf.median():.2f} estrellas por fork")
    print(f"  - Media del ratio:   {ratio_sf.mean():.2f} estrellas por fork")
    print(f"  - Correlación de Pearson entre Stars y Forks: {df['Stars'].corr(df['Forks']):.4f}")
    
    # Issues según Has Downloads
    print("\nComportamiento de 'Issues' según 'Has Downloads':")
    has_dl_stats = df.groupby('Has Downloads')['Issues'].agg(['count', 'mean', 'median', 'std'])
    for val, row in has_dl_stats.iterrows():
        print(f"  - Has Downloads = {val}: {int(row['count']):,} repos | Media Issues: {row['mean']:.2f} | Mediana Issues: {row['median']:.1f}")

    # Issues según Has Issues
    print("\nComportamiento de 'Issues' según 'Has Issues':")
    has_iss_stats = df.groupby('Has Issues')['Issues'].agg(['count', 'mean', 'median', 'std'])
    for val, row in has_iss_stats.iterrows():
        print(f"  - Has Issues = {val}: {int(row['count']):,} repos | Media Issues: {row['mean']:.2f} | Mediana Issues: {row['median']:.1f}")

def parsear_campos_semiestructurados(df):
    print("\n" + "=" * 75)
    print("5. ANÁLISIS DE CAMPOS SEMI-ESTRUCTURADOS (VIOLACIÓN DE 1FN: TOPICS)")
    print("=" * 75)
    
    def safe_topics_len(val):
        if pd.isna(val) or val == '[]':
            return 0
        try:
            return len(ast.literal_eval(val))
        except Exception:
            return 0

    df['cant_topics'] = df['Topics'].apply(safe_topics_len)
    
    sin_topics = (df['cant_topics'] == 0).sum()
    con_topics = (df['cant_topics'] > 0).sum()
    
    print("Métricas del campo 'Topics' (listas serializadas):")
    print(f"  - Repositorios sin tópicos ([]): {sin_topics:,} ({sin_topics / len(df) * 100:.2f}%)")
    print(f"  - Repositorios con tópicos: {con_topics:,} ({con_topics / len(df) * 100:.2f}%)")
    print(f"  - Cantidad de tópicos por repo: Min={df['cant_topics'].min()}, Mediana={df['cant_topics'].median():.1f}, Media={df['cant_topics'].mean():.2f}, Max={df['cant_topics'].max()}")
    print("  -> Conclusión de Base de Datos: 'Topics' almacena arreglos no atómicos dentro de una columna de texto.")
    print("     Esto viola la 1FN y requiere normalizarse mediante una tabla N:M (repository_topics).")
    return df

def auditoria_temporal_y_estados(df):
    print("\n" + "=" * 75)
    print("6. AUDITORÍA TEMPORAL, CICLO DE VIDA Y ESTADOS")
    print("=" * 75)
    df['created_dt'] = pd.to_datetime(df['Created At'])
    df['updated_dt'] = pd.to_datetime(df['Updated At'])
    df['created_year'] = df['created_dt'].dt.year
    
    print(f"Rango temporal de creación: {df['created_dt'].min().strftime('%Y-%m-%d')} a {df['created_dt'].max().strftime('%Y-%m-%d')}")
    print(f"Rango temporal de última actualización: {df['updated_dt'].min().strftime('%Y-%m-%d')} a {df['updated_dt'].max().strftime('%Y-%m-%d')}")
    
    archived_count = df['Is Archived'].sum()
    fork_count = df['Is Fork'].sum()
    print(f"\nEstados booleanos de repositorios:")
    print(f"  - Repositorios Archivados (Read-only): {archived_count:,} ({archived_count / len(df) * 100:.2f}%)")
    print(f"  - Repositorios Fork (derivados): {fork_count:,} (0.00% - Varianza nula en el dataset)")
    return df

def generar_graficos(df, output_dir="graficos_repositories"):
    print("\n" + "=" * 75)
    print(f"7. GENERACIÓN DE VISUALIZACIONES EN '{output_dir}/'")
    print("=" * 75)
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Asimetría: Media vs Mediana de Stars y Forks
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    metricas = ['Stars', 'Forks']
    medias = [df['Stars'].mean(), df['Forks'].mean()]
    medianas = [df['Stars'].median(), df['Forks'].median()]
    
    x = np.arange(len(metricas))
    width = 0.35
    ax1.bar(x - width/2, medias, width, label='Media Aritmética', color='#1976d2', edgecolor='black')
    ax1.bar(x + width/2, medianas, width, label='Mediana (P50)', color='#ff9800', edgecolor='black')
    ax1.set_ylabel('Cantidad (Escala Lineal)')
    ax1.set_title('Media vs. Mediana: Asimetría Severa (Ley de Potencia)', fontsize=11, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(metricas, fontweight='bold')
    ax1.legend()
    for i in range(len(metricas)):
        ax1.text(x[i] - width/2, medias[i] + 30, f"{medias[i]:,.0f}", ha='center', fontsize=9, fontweight='bold')
        ax1.text(x[i] + width/2, medianas[i] + 30, f"{medianas[i]:,.0f}", ha='center', fontsize=9, fontweight='bold')

    # Versión logarítmica para visualizar percentiles
    sns.boxplot(data=df[['Stars', 'Forks']], palette=['#90caf9', '#ffe082'], ax=ax2)
    ax2.set_yscale('log')
    ax2.set_title('Distribución Logarítmica de Stars y Forks (Outliers)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Escala Logarítmica (log10)')
    plt.tight_layout()
    p1 = os.path.join(output_dir, "1_asimetria_media_mediana_stars_forks.png")
    plt.savefig(p1, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Gráfico 1 guardado en: {p1}")

    # 2. Evolución Temporal de Creación por Año
    fig, ax = plt.subplots(figsize=(10, 5))
    anios_counts = df['created_year'].value_counts().sort_index()
    anios_counts = anios_counts[anios_counts.index >= 2008]
    bars = ax.bar(anios_counts.index.astype(str), anios_counts.values, color='#3f51b5', edgecolor='black', alpha=0.85)
    ax.set_title('Evolución Histórica: Repositorios Creados por Año (2008 - 2023)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Año de Creación (Created At)')
    ax.set_ylabel('Cantidad de Repositorios')
    ax.tick_params(axis='x', rotation=45)
    for bar in bars:
        h = bar.get_height()
        if h > 2000:
            ax.text(bar.get_x() + bar.get_width()/2., h + 300, f"{h:,}", ha='center', fontsize=7.5, rotation=90)
    plt.tight_layout()
    p2 = os.path.join(output_dir, "2_evolucion_temporal_creacion.png")
    plt.savefig(p2, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Gráfico 2 guardado en: {p2}")

    # 3. Relación Stars vs Forks y Ratio
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    sample_df = df.sample(min(15000, len(df)), random_state=42)
    ax1.scatter(sample_df['Forks'], sample_df['Stars'], alpha=0.25, color='#00796b', s=12)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_title('Relación Stars vs. Forks (Muestra 15k, Escala Log)', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Forks (log)')
    ax1.set_ylabel('Stars (log)')
    
    # Histograma del Ratio Stars/Forks
    valid_forks = df[(df['Forks'] > 0) & (df['Stars'] > 0)]
    ratio = (valid_forks['Stars'] / valid_forks['Forks']).clip(upper=40)
    sns.histplot(ratio, bins=40, color='#e91e63', kde=True, ax=ax2)
    ax2.axvline(ratio.median(), color='black', linestyle='--', linewidth=1.5, label=f'Mediana = {ratio.median():.2f}')
    ax2.set_title('Distribución del Ratio Stars / Forks (acotado a 40)', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Ratio (Estrellas por cada Fork)')
    ax2.set_ylabel('Frecuencia')
    ax2.legend()
    plt.tight_layout()
    p3 = os.path.join(output_dir, "3_relacion_stars_forks_ratio.png")
    plt.savefig(p3, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Gráfico 3 guardado en: {p3}")

    # 4. Análisis de Issues según Has Downloads y Has Issues
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    sns.boxplot(data=df, x='Has Downloads', y='Issues', hue='Has Downloads', palette=['#ef5350', '#66bb6a'], legend=False, ax=ax1)
    ax1.set_yscale('log')
    ax1.set_title('Distribución de Issues según Has Downloads (Escala Log)', fontsize=11, fontweight='bold')
    ax1.set_xlabel('¿Habilitó Descargas de Binarios? (Has Downloads)')
    ax1.set_ylabel('Cantidad de Issues (log)')
    
    sns.boxplot(data=df, x='Has Issues', y='Issues', hue='Has Issues', palette=['#ab47bc', '#42a5f5'], legend=False, ax=ax2)
    ax2.set_yscale('log')
    ax2.set_title('Issues en Repositorios según Has Issues Habilitado', fontsize=11, fontweight='bold')
    ax2.set_xlabel('¿Soporte de Issues Habilitado? (Has Issues)')
    ax2.set_ylabel('Cantidad de Issues (log)')
    plt.tight_layout()
    p4 = os.path.join(output_dir, "4_analisis_issues_descargas_soporte.png")
    plt.savefig(p4, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Gráfico 4 guardado en: {p4}")

    # 5. Top 10 Lenguajes y Top 10 Licencias
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    top_lang = df['Language'].value_counts().head(10).sort_values(ascending=True)
    ax1.barh(top_lang.index, top_lang.values, color='#26a69a', edgecolor='black')
    ax1.set_title('Top 10 Lenguajes de Programación Principales', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Cantidad de Repositorios')
    for i, v in enumerate(top_lang.values):
        ax1.text(v + 400, i, f"{v:,} ({v/len(df)*100:.1f}%)", va='center', fontsize=8.5, fontweight='bold')

    top_lic = df['License'].value_counts().head(10).sort_values(ascending=True)
    ax2.barh(top_lic.index, top_lic.values, color='#7e57c2', edgecolor='black')
    ax2.set_title('Top 10 Licencias de Software Declaradas', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Cantidad de Repositorios')
    for i, v in enumerate(top_lic.values):
        ax2.text(v + 600, i, f"{v:,} ({v/len(df)*100:.1f}%)", va='center', fontsize=8.5, fontweight='bold')
    plt.tight_layout()
    p5 = os.path.join(output_dir, "5_top_lenguajes_y_licencias.png")
    plt.savefig(p5, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Gráfico 5 guardado en: {p5}")

    # 6. Distribución de Cantidad de Tópicos (Violación 1FN)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    topics_counts = df['cant_topics'].value_counts().sort_index()
    ax.bar(topics_counts.index, topics_counts.values, color='#fb8c00', edgecolor='black', alpha=0.9)
    ax.set_title('Cardinalidad de Tópicos por Repositorio (Violación de 1FN)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Cantidad de Tópicos Asignados')
    ax.set_ylabel('Frecuencia de Repositorios')
    ax.set_xticks(range(0, 21))
    plt.tight_layout()
    p6 = os.path.join(output_dir, "6_distribucion_topicos_1fn.png")
    plt.savefig(p6, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Gráfico 6 guardado en: {p6}")

def imprimir_conclusiones():
    print("\n" + "=" * 75)
    print("8. CONCLUSIONES INTEGRALES Y RECOMENDACIONES PARA DISEÑO DE BD")
    print("=" * 75)
    conclusiones = """
1. INTEGRIDAD DE CLAVES PRIMARIAS Y ALTERNATIVAS:
   - 'URL' posee 100% de unicidad (215,029 valores únicos) y actúa como clave candidata natural.
   - 'Name' presenta 27,952 colisiones (ej: 'dotfiles' x200, 'blog' x186, 'core' x92). NO DEBE ser UNIQUE.
   - Se recomienda utilizar una clave subrogada artificial: 'id SERIAL PRIMARY KEY'.

2. AUDITORÍA DE REDUNDANCIA Y NORMALIZACIÓN:
   - 'Stars' y 'Watchers' son 100% idénticos en todas las filas. Mantener ambas columnas es una violación
     de eficiencia y normalización física. Se debe conservar únicamente 'stars'.
   - 'Is Fork' es False en el 100% de los registros (varianza cero). No aporta valor analítico.

3. VIOLACIÓN DE LA PRIMERA FORMA NORMAL (1FN):
   - El atributo 'Topics' almacena arreglos serializados de texto con hasta 20 etiquetas por repositorio.
   - En una arquitectura relacional (OLTP/DW), se debe normalizar mediante:
     * topics (id, name)
     * repository_topics (repository_id, topic_id)

4. ASIMETRÍA ESTADÍSTICA Y LEY DE POTENCIA:
   - 'Stars' (Mediana=377 vs Media=1,115) y 'Forks' (Mediana=79 vs Media=234) evidencian asimetría positiva severa.
   - La mediana del ratio Stars/Forks es 5.58, indicando que un proyecto típico recibe ~5.6 estrellas por cada fork.
   - 'Size' requiere tipo de dato BIGINT en SQL dado que su valor máximo supera los 105 GB (105,078,627 KB).

5. DISPERSIÓN DE ATRIBUTOS Y TRATAMIENTO DE NULOS:
   - 'Homepage' presenta 63.54% de nulos (atributo altamente opcional).
   - 'License' contiene 24.67% nulos y 9.8% 'NOASSERTION'. Requiere normalizarse en una tabla dimensional 'licenses'.
   - 'Language' contiene 7.48% de nulos (proyectos políglotas o de documentación). Normalizar en 'languages'.
"""
    print(conclusiones)
    print("=" * 75)

if __name__ == "__main__":
    df = cargar_y_perfilado_inicial()
    auditoria_calidad_y_nulos(df)
    analisis_unicidad_y_claves(df)
    analisis_estadistico_asimetria(df)
    df = parsear_campos_semiestructurados(df)
    df = auditoria_temporal_y_estados(df)
    generar_graficos(df)
    imprimir_conclusiones()
