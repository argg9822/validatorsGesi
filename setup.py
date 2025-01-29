from cx_Freeze import setup, Executable
import os
import sys

# Lista de dependencias (puedes obtenerlas de requirements.txt)
build_options = {
    "packages": [
        "os",
        "sys",
        "tkinter",
        "customtkinter",
        "pandas",
        "json",
        "openpyxl",
        "datetime",
        "time",
        "subprocess",
        "PIL",
        "colorama",
        "win32com",
    ],  # Añade aquí los paquetes que usas
    "excludes": [],  # Excluye paquetes innecesarios
    "include_files": [
    ("img", "img"),  # Carpeta de imágenes
    ("validadores", "validadores"),  # Carpeta de validadores
    ("crear_hc", "crear_hc"),  # Carpeta de crear_hc
    "index.py",  # Archivo principal
    "index1.py",  # Otro archivo principal
    "areas.json",  # Archivo de configuración
    "__version__.py",  # Archivo de versión
    "version.txt",  # Texto con la versión
    "bases.json",  # Archivo de bases
    "img/logo.ico",  # Asegúrate de que esta ruta sea correcta
    "installer"
], 
}

# Incluir Tcl/Tk (necesario para Tkinter)
# tcl_dir = os.path.join(os.path.dirname(sys.executable), "tcl")
# tk_dir = os.path.join(os.path.dirname(sys.executable), "tk")

# build_options["include_files"].extend([tcl_dir, tk_dir])

# Configuración para el ejecutable
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Usa esto si es una aplicación con interfaz gráfica en Windows

# Definir el ejecutable
executables = [
    Executable(
        script="Odin.py",  # Reemplaza con el nombre de tu script principal
        base=base,
        icon="img/logo.ico",  # Opcional: añade un icono para la aplicación
    )
]

# Configuración del setup
setup(
    name="Odin",  # Nombre de la aplicación
    version="1.0",  # Versión de la aplicación
    description="Validador",  # Descripción
    options={"build_exe": build_options},  # Opciones de construcción
    executables=executables,  # Ejecutables a generar
)