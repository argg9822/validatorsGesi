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
    ("version.txt", "version.txt")
    ("bases.json", "bases.json")
    
]

# Configuración de base solo para Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Omitir consola de comandos en aplicaciones GUI en Windows
# Ejecutable configurado con Win32GUI
executables = [Executable("Validador_gesi.py", base=base, icon="img/logo.ico")]
# Configuración de cx_Freeze
setup(
    name="Gesi App",
    version="1.0",
    description="Gesi App",
    executables=executables,
    options={"build_exe": {
        "include_files": include_files,
        "packages": [
            "tkinter", "customtkinter", "PIL", "requests", "json", "zipfile", 
            "subprocess", "sys", "openpyxl", "pandas", "re", "shutil", 
            "datetime", "colorama",
        ],
        "includes": [
            "validadores", "img", "colorama", "__version__", 
            "tkinter.filedialog", "tkinter.messagebox", "tkinter.simpledialog", 
            "openpyxl.styles", "openpyxl.utils"
        ],
        "excludes": ["tkinter.ttk", "tkinter.tix"]  # Excluir dependencias innecesarias
    }},
)
