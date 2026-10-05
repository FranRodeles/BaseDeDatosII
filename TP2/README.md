# Trabajo Práctico N° 2 - Diseño de Bases de Datos II
Materia: Diseño de Bases de Datos II  
Carrera: Ingeniería en Informática - Universidad de Mendoza (UM)  
Alumno: Francisco Rodeles  

---

## Descripción del Proyecto
Este repositorio contiene la auditoría, análisis exploratorio de datos (EDA), perfilado estructural y recomendaciones de diseño relacional / Data Warehouse para dos conjuntos de datos:
1. `questions_dataset.csv`: Colección de problemas algorítmicos y desafíos de programación (616 filas x 9 columnas).
2. `repositories.csv`: Gran repositorio de proyectos y software open source de GitHub (215,029 filas x 24 columnas).

Ambos análisis abordan:
- Perfilado de integridad, completitud y columnas dispersas (sparse).
- Detección de claves candidatas vs. claves subrogadas y colisiones de nombres (`UNIQUE`).
- Auditoría de redundancia estricta entre atributos.
- Asimetría estadística y distribución de ley de potencia (power-law): Media vs. Mediana.
- Análisis de métricas condicionadas (ej. incidencias / Issues según Has Downloads y Has Issues).
- Desanidado y cardinalidad de estructuras semi-estructuradas (JSON y listas de Python) que violan la Primera Forma Normal (1FN).
- Auditoría temporal y patrones de ingesta/ciclo de vida del software.

---

## Estructura del Directorio

```text
RodelesFrancisco/
├── analisis_questions_dataset.ipynb      # Notebook interactivo de questions_dataset.csv
├── analisis_questions.py                # Script ejecutable en consola para questions
├── graficos/                             # Gráficos generados de questions_dataset
│
├── analisis_repositories_dataset.ipynb   # Notebook interactivo de repositories.csv
├── analisis_repositories.py             # Script ejecutable en consola para repositories
├── graficos_repositories/                # Gráficos generados de repositories.csv
│
├── questions_dataset.csv                 # Dataset de preguntas
├── repositories.csv                     # Dataset de repositorios
├── requirements.txt                      # Dependencias del proyecto
└── README.md                             # Documentación de instalación y ejecución
```

---

## Guía de Instalación y Ejecución

### 1. Creación y Activación del Entorno Virtual

En Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

En Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Instalación de Dependencias

Con el entorno virtual activo:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Ejecución de los Scripts en Consola

Cada script procesa su dataset correspondiente, imprime el perfilado detallado en la terminal y genera las figuras en su respectiva carpeta:

- Para analizar `questions_dataset.csv`:
  ```bash
  python analisis_questions.py
  ```
  *(Los gráficos se guardan en `graficos/`)*

- Para analizar `repositories.csv`:
  ```bash
  python analisis_repositories.py
  ```
  *(Los gráficos se guardan en `graficos_repositories/`)*

---

## Ejecución de los Cuadernos Jupyter

Para explorar el análisis interactivo con sus celdas explicativas, tablas y visualizaciones:

```bash
jupyter notebook
```
Luego seleccionar en el navegador:
- `analisis_questions_dataset.ipynb`
- `analisis_repositories_dataset.ipynb`

*(Nota: Ambos cuadernos ya cuentan con todas las salidas y gráficos pre-renderizados para una visualización inmediata sin necesidad de re-ejecutar).*

---

## Síntesis de Hallazgos para Diseño de Bases de Datos

| Dimensión Analizada | `questions_dataset.csv` | `repositories.csv` |
| :--- | :--- | :--- |
| Completitud | 100% libre de nulos en sus 9 atributos. | 19 columnas 100% completas; `Homepage` (63.5% nulos) y `License` (24.7% nulos). |
| Clave Primaria | `id` (1 a 616) estricta y consecutiva. | Clave subrogada `id SERIAL` recomendada (`URL` es clave candidata natural con 100% de unicidad). |
| Restricción UNIQUE | `title` presenta 55 colisiones (47 problemas distintos con mismo nombre). No debe ser UNIQUE. | `Name` presenta 27,952 colisiones (ej. `dotfiles`, `blog`, `core`). No debe ser UNIQUE. |
| Redundancia | `updated_at == created_at` en el 100% de los registros (sin historial de updates). | `Stars == Watchers` en el 100% de los registros. Se debe eliminar una de ellas. |
| Violación de 1FN | `examples`, `constraints`, `test_cases` (JSONs anidados). Requiere tablas subordinadas. | `Topics` (listas de Python serializadas). Requiere normalizarse en relación N:M (`repository_topics`). |
| Asimetría Estadística | Moda de `test_cases` en 5, con outlier de 32 en ID 122. | Media de `Stars` (1,115) es 2.96x la mediana (377). Ratio Stars/Forks con mediana de 5.58. `Size` requiere `BIGINT`. |
