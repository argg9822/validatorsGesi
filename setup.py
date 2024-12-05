import sys
from cx_Freeze import setup, Executable
import site
import os


# Definir las rutas completas a los paquetes
colorama_path = r'C:\Users\Gesi-Educativo\AppData\Local\Programs\Python\Python312\Lib\site-packages\colorama'
PIL_path = r'C:\Users\Gesi-Educativo\AppData\Local\Programs\Python\Python312\Lib\site-packages\PIL'

include_files = [
    ("img", "img"),
    ("validadores", "validadores"),
    ("crear_hc", "crear_hc"),
    ("index.py", "index.py"),
    ("index1.py", "index1.py"),
    ("__version__.py", "__version__.py"),
    ("version.txt", "version.txt"),
    ("bases.json", "bases.json"),
    (colorama_path, 'colorama'),  # Usando la ruta completa para colorama
    (PIL_path, 'PIL'),  # Usando la ruta completa para PIL
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
            "selenium.webdriver.common.action_chains","PIL.Image", "PIL.ImageTk", "tkinter.filedialog", "tkinter.messagebox",
            "win32com", "win32com.client",
        ],
        "include_msvcr": True,
    }},
)
