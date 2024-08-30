import sys
import cx_Freeze
from cx_Freeze import setup, Executable

# Archivos a incluir en el paquete
include_files = [
    ("img", "img"),
    ("validadores", "validadores"),
    ("index.py", "index.py"),
    ("index1.py", "index1.py"),
    ("__version__.py", "__version__.py"),
    ("version.txt", "version.txt"),
    ("bases.json", "bases.json"),
    ("crear_hc", "crear_hc"),
    ("funciones.py", "funciones.py"),
    ("logo.ico", "logo.ico")
    
]

# Configuración de base solo para Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Omitir consola de comandos en aplicaciones GUI en Windows
# Ejecutable configurado con Win32GUI
executables = [Executable("Odin.py", base=base, icon="logo.ico")]
# Configuración de cx_Freeze
setup(
    name="Odin",
    version="1.0",
    description="Odin",
    executables=executables,
    options={"build_exe": {
        "include_files": include_files,
        "packages": [
            "tkinter", "customtkinter","threading" ,"PIL", "requests", "json", "zipfile", 
            "subprocess", "sys", "openpyxl", "pandas", "re", "shutil", 
            "datetime", "colorama", "selenium", "math", "os", "time"
        ],
        "includes": [
            "validadores", "img", "colorama", "__version__", 
            "tkinter.filedialog", "tkinter.messagebox", "tkinter.simpledialog", 
            "openpyxl.styles", "openpyxl.utils", "selenium", "selenium.webdriver.common.keys", "selenium.webdriver.common.by", 
            "selenium.webdriver.common.action_chains", "selenium.common.exceptions"
        ],
        "excludes": ["tkinter.tix"]  # Excluir dependencias innecesarias, puedes volver a agregar `ttk` si lo necesitas.
    }},
)
