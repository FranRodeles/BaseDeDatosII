# Base de Datos II

Materia: Diseño de Bases de Datos II  
Carrera: Ingeniería en Informática - Universidad de Mendoza (UM)  
Alumno: Francisco Rodeles  

---

## Requisitos previos

- Python 3.10 o superior
- pip
- Git

---

## Instalación

1. Clonar el repositorio y ubicarse en la carpeta del proyecto:

```bash
git clone git@github.com:FranRodeles/BaseDeDatosII.git
cd BaseDeDatosII
```

2. Crear y activar el entorno virtual:

En Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

En Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Actualizar pip e instalar dependencias:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Registrar el kernel para Jupyter (opcional pero recomendado):

```bash
python -m ipykernel install --user --name basededatos2 --display-name "Python (BaseDeDatosII)"
```

5. Comprobar que el entorno esté listo:

```bash
python test_env.py
```

---

## Ejecución

### Cuadernos Jupyter

Para iniciar el entorno interactivo:

```bash
jupyter notebook
```

O si se utiliza JupyterLab:

```bash
jupyter lab
```

Al abrir cualquier cuaderno (.ipynb), seleccionar el kernel correspondiente al entorno virtual (`Python (BaseDeDatosII)` o `.venv`).

### Scripts en consola

Cualquier script de Python se puede ejecutar directamente desde la terminal con el entorno virtual activo:

```bash
python <nombre_del_script>.py
```