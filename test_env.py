#!/usr/bin/env python3
"""
Script de verificación de entorno y dependencias.
Diseño de Bases de Datos II - Universidad de Mendoza (UM)
"""

import sys
import os

def print_header(title):
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def test_imports():
    print_header("1. VERIFICACIÓN DE PAQUETES Y DEPENDENCIAS")
    packages = [
        ("NumPy", "numpy"),
        ("Pandas", "pandas"),
        ("SciPy", "scipy"),
        ("Matplotlib", "matplotlib"),
        ("Seaborn", "seaborn"),
        ("Scikit-Learn", "sklearn"),
        ("Folium", "folium"),
        ("BeautifulSoup4", "bs4"),
        ("Requests", "requests"),
        ("OpenPyXL", "openpyxl"),
        ("XLRD", "xlrd"),
        ("Odfpy", "odf"),
        ("MySQL Connector", "mysql.connector"),
        ("Psycopg2 (PostgreSQL)", "psycopg2"),
        ("TensorFlow", "tensorflow"),
        ("Keras", "keras"),
        ("Jupyter / IPyKernel", "ipykernel"),
    ]

    all_ok = True
    for name, module in packages:
        try:
            mod = __import__(module)
            version = getattr(mod, "__version__", "OK")
            print(f"  [✓] {name:<25} versión: {version}")
        except Exception as e:
            print(f"  [✗] {name:<25} ERROR: {e}")
            all_ok = False

    return all_ok

def test_datasets():
    print_header("2. VERIFICACIÓN DE ACCESO A DATASETS")
    import pandas as pd

    base_dir = os.path.dirname(os.path.abspath(__file__))
    checks = [
        ("TP2: questions_dataset.csv", os.path.join(base_dir, "TP2", "questions_dataset.csv"), lambda p: pd.read_csv(p)),
        ("TP2: repositories.csv", os.path.join(base_dir, "TP2", "repositories.csv"), lambda p: pd.read_csv(p, nrows=100)),
        ("Prácticas: vino.ods", os.path.join(base_dir, "practicas", "data", "vino.ods"), lambda p: pd.read_excel(p, sheet_name="vino")),
        ("Prácticas: vino.xls", os.path.join(base_dir, "practicas", "data", "vino.xls"), lambda p: pd.read_excel(p)),
        ("Prácticas: sponge.data", os.path.join(base_dir, "practicas", "data", "sponge.data"), lambda p: pd.read_csv(p)),
        ("Prácticas: hotel_bookings.csv", os.path.join(base_dir, "practicas", "data", "hotel_bookings.csv"), lambda p: pd.read_csv(p, nrows=100)),
    ]

    all_ok = True
    for label, path, load_fn in checks:
        if not os.path.exists(path):
            print(f"  [✗] {label:<35} No encontrado en: {path}")
            all_ok = False
            continue
        try:
            df = load_fn(path)
            print(f"  [✓] {label:<35} Carga OK (muestra {df.shape})")
        except Exception as e:
            print(f"  [✗] {label:<35} ERROR al leer: {e}")
            all_ok = False

    return all_ok

if __name__ == "__main__":
    print(f"Python en uso: {sys.executable} (v{sys.version.split()[0]})")
    pkg_ok = test_imports()
    data_ok = test_datasets()

    print_header("RESUMEN DE ESTADO DEL ENTORNO")
    if pkg_ok and data_ok:
        print("  🎉 ¡TODO ESTÁ LISTO Y FUNCIONANDO CORRECTAMENTE!")
        print("  Podés iniciar Jupyter Notebook con: jupyter notebook")
        print("  O correr los scripts del TP2 desde la carpeta TP2/.\n")
    else:
        print("  ⚠️ Hubo advertencias o errores. Revisá las dependencias marcadas arriba.\n")
