import cx_Freeze
from cx_Freeze import setup, Executable

# Archivos a incluir en el paquete
include_files = [
    ("img", "img"),
    ("validadores", "validadores"),
    ("index.py", "index.py"),
    ("__version__.py", "__version__.py"),
    ("version.txt", "version.txt")
]

# Ejecutable configurado con Win32GUI para ocultar la consola
executables = [Executable("splash.py", base="Win32GUI")]  # Omitir consola de comandos

# Configuración de cx_Freeze
setup(
    name="Gesi App",
    version="1.0",
    description="Gesi App",
    executables=executables,
    options={"build_exe": {
        "include_files": include_files,
        "packages": [
            "tkinter", "PIL", "requests", "json", "zipfile", "subprocess", 
            "sys", "openpyxl", "pandas", "re", "shutil", "datetime"
        ],
        "includes": [
            "validadores", "img", "colorama", "__version__", 
            "tkinter.filedialog", "tkinter.messagebox", "tkinter.simpledialog", 
            "openpyxl.styles", "openpyxl.utils"
        ],
        "excludes": ["tkinter.ttk", "tkinter.tix"]  # Excluir dependencias innecesarias
    }},
)
