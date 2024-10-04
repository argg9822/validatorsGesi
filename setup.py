import sys
import cx_Freeze
from cx_Freeze import setup, Executable

# Archivos a incluir en el paquete
include_files = [
    ("img", "img"),
    ("validadores", "validadores"),
    ("crear_hc", "crear_hc"),
    ("index.py", "index.py"),
    ("index1.py", "index1.py"),
    ("__version__.py", "__version__.py"),
    ("version.txt", "version.txt"),
    ("bases.json", "bases.json"),
]

# Configuración de base solo para Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Omitir consola de comandos en aplicaciones GUI en Windows

# Ejecutable configurado con Win32GUI
executables = [Executable("Odin.py", base=base, icon="img/logo.ico")]

# Configuración de cx_Freeze
setup(
    name="Odin",
    version="1.0",
    description="Odin",
    executables=executables,
    options={"build_exe": {
        "include_files": include_files,
        "packages": [
            "tkinter", "tkinter.tix", "customtkinter", "threading", "PIL", "requests", "json", 
            "zipfile", "subprocess", "sys", "openpyxl", "pandas", "re", "shutil", 
            "datetime", "colorama", "selenium", "math", "os", "time"
        ],
        "includes": [
            "validadores", "crear_hc", "img", "colorama", "__version__", 
            "tkinter.filedialog", "tkinter.messagebox", "tkinter.simpledialog", 
            "openpyxl.styles", "openpyxl.utils", "selenium", "selenium.webdriver.common.keys", 
            "selenium.webdriver.common.by", "selenium.webdriver.common.action_chains", 
            "selenium.common.exceptions", "selenium.webdriver.chrome.webdriver",  # Incluye el módulo webdriver
            "selenium.webdriver.support.ui", "selenium.webdriver.support.expected_conditions", 
            "selenium.webdriver.common.action_chains"
        ],
        "include_msvcr": True,
    }},
)
