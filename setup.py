import sys
from cx_Freeze import setup, Executable

# Archivos y carpetas que deseas incluir
include_files = [
    ("img", "img"),  # Carpeta de imágenes
    ("validadores", "validadores"),  # Carpeta de validadores
    ("crear_hc", "crear_hc"),  # Carpeta de crear_hc
    "index.py",  # Archivo principal
    "index1.py",  # Otro archivo principal
    "areas.json",  # Archivo de configuración
    "__version__.py",  # Archivo de versión
    "version.txt",  # Texto con la versión
    "bases.json",  # Archivo de bases
]

# Configuración base solo para Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Evitar abrir consola si es una GUI

# Ejecutable configurado con un ícono
executables = [
    Executable(
        script="Odin.py",  # Archivo principal
        base=base,
        icon="img/logo.ico",  # Ícono del programa
    )
]

# Configuración del setup
setup(
    name="Odin",
    version="1.0",
    description="Odin - Gestión avanzada",
    executables=executables,
    options={
        "build_exe": {
            "include_files": include_files,  # Archivos/carpetas adicionales
            "packages": [
                "tkinter", "tkinter.tix", "customtkinter", "threading", "PIL", "requests",
                "json", "zipfile", "subprocess", "sys", "openpyxl", "pandas", "re", "shutil",
                "datetime", "colorama", "selenium", "math", "os", "time"
            ],
            "includes": [
                "validadores", "crear_hc", "img", "__version__", "tkinter.filedialog",
                "tkinter.messagebox", "tkinter.simpledialog", "openpyxl.styles", "openpyxl.utils",
                "selenium.webdriver.common.keys", "selenium.webdriver.common.by",
                "selenium.webdriver.common.action_chains", "selenium.common.exceptions",
                "selenium.webdriver.chrome.webdriver", "selenium.webdriver.support.ui",
                "selenium.webdriver.support.expected_conditions", "PIL.Image", "PIL.ImageTk",
                "win32com", "win32com.client"
            ],
            "zip_include_packages": ["*"],  # Incluir todos los paquetes en un archivo ZIP
            "zip_exclude_packages": [],  # Excluir paquetes específicos si es necesario
            "include_msvcr": True,  # Incluir las librerías de Visual C++
            "optimize": 2,  # Optimización del bytecode
        }
    },
)
